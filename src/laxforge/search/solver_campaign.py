"""Long-running conservative solver campaign orchestration."""

from __future__ import annotations

import json
import os
import time
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from laxforge.search.formal_sphere_ansatz import solve_formal_sphere_ansatz
from laxforge.search.overnight import (
    OvernightCandidate,
    OvernightSearchConfig,
    _action_queue,
    _candidate,
    _priority,
    _scalar_factors,
    _vector_atoms,
    run_overnight_search,
)
from laxforge.search.sphere_zcr import (
    solve_heisenberg_zcr_ansatz,
    solve_sx_zcr_ansatz,
    solve_sxxx_zcr_ansatz,
)


SURVIVOR_STATUSES = {"automated_survivor_needs_human_prior_art_review"}
CampaignSpec = tuple[str, str, str, int, str, str, tuple[int, ...], int, int, int]


@dataclass(frozen=True)
class SolverCampaignConfig:
    """Configuration for a checkpointed solver campaign."""

    wall_seconds: int = 24 * 60 * 60
    target_count: int = 4096
    max_derivative_order: int = 9
    max_expansion_order: int = 45
    action_queue_limit: int = 512
    output_dir: Path = Path("runs") / "solver_campaign_latest"
    checkpoint_every: int = 25
    candidate_pool_limit: int = 4096
    frontier_vector_limit: int = 192
    blend_pair_window: int = 24
    monitor_json_path: Path | None = None
    monitor_recent_attempts: int = 50


@dataclass(frozen=True)
class SolverAttemptRecord:
    """One candidate-specific solver attempt."""

    candidate_name: str
    family: str
    order: int
    descriptor: str
    attempt_status: str
    recommendation: str
    validated_zcr: bool
    known_collision: bool
    spectral_status: str
    gauge_risk_score: float | None
    cyclic_fingerprint: str | None
    formal_ansatz_status: str | None
    formal_ansatz_unknowns: int | None
    obstruction_basis: tuple[str, ...]
    failure_reasons: tuple[str, ...]
    elapsed_seconds: float

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible attempt record."""
        return {
            "candidate_name": self.candidate_name,
            "family": self.family,
            "order": self.order,
            "descriptor": self.descriptor,
            "attempt_status": self.attempt_status,
            "recommendation": self.recommendation,
            "validated_zcr": self.validated_zcr,
            "known_collision": self.known_collision,
            "spectral_status": self.spectral_status,
            "gauge_risk_score": self.gauge_risk_score,
            "cyclic_fingerprint": self.cyclic_fingerprint,
            "formal_ansatz_status": self.formal_ansatz_status,
            "formal_ansatz_unknowns": self.formal_ansatz_unknowns,
            "obstruction_basis": list(self.obstruction_basis),
            "failure_reasons": list(self.failure_reasons),
            "elapsed_seconds": round(self.elapsed_seconds, 6),
        }


@dataclass(frozen=True)
class SolverCampaignReport:
    """Summary of a solver campaign run."""

    run_id: str
    started_at: str
    finished_at: str
    status: str
    attempts: tuple[SolverAttemptRecord, ...]
    survivor: SolverAttemptRecord | None
    candidate_count: int
    rounds_completed: int
    output_dir: str

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible campaign report."""
        return {
            "run_id": self.run_id,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "status": self.status,
            "attempt_count": len(self.attempts),
            "candidate_count": self.candidate_count,
            "output_dir": self.output_dir,
            "survivor": self.survivor.as_dict() if self.survivor else None,
            "rounds_completed": self.rounds_completed,
            "attempts": [attempt.as_dict() for attempt in self.attempts],
        }


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _span_width(span: tuple[int, ...]) -> int:
    return max(span) - min(span) if span else 0


def _campaign_vector_frontier(
    vectors: tuple[tuple[str, str, int, tuple[int, ...], int], ...],
    *,
    limit: int,
) -> tuple[tuple[str, str, int, tuple[int, ...], int], ...]:
    low_order = [vector for vector in vectors if vector[2] <= 6]
    high_pressure = sorted(
        vectors,
        key=lambda vector: (
            vector[2],
            _span_width(vector[3]),
            vector[4],
            "cross" in vector[0],
            vector[0],
        ),
        reverse=True,
    )
    merged: list[tuple[str, str, int, tuple[int, ...], int]] = []
    seen: set[str] = set()
    for vector in low_order + high_pressure:
        if vector[0] in seen:
            continue
        seen.add(vector[0])
        merged.append(vector)
        if len(merged) >= limit:
            break
    return tuple(merged)


def _campaign_candidate_from_spec(spec: CampaignSpec) -> OvernightCandidate:
    (
        name,
        family,
        descriptor,
        order,
        scalar_factor,
        vector_atom,
        derivative_span,
        priority_score,
        _scalar_complexity,
        _vector_complexity,
    ) = spec
    return _candidate(
        name=name,
        family=family,
        descriptor=descriptor,
        order=order,
        scalar_factor=scalar_factor,
        vector_atom=vector_atom,
        derivative_span=derivative_span,
        priority_score=priority_score,
    )


def _bounded_campaign_candidates(
    config: SolverCampaignConfig,
    *,
    max_order: int,
    attempted_names: set[str],
) -> tuple[OvernightCandidate, ...]:
    scalar_factors = _scalar_factors(max_order)
    vector_atoms = _vector_atoms(max_order)
    frontier_vectors = _campaign_vector_frontier(
        vector_atoms,
        limit=max(24, min(config.frontier_vector_limit, len(vector_atoms))),
    )
    spec_budget = max(config.target_count, config.action_queue_limit * 4, 512)
    spec_budget = min(spec_budget, config.candidate_pool_limit)
    specs: list[CampaignSpec] = []

    for scalar_key, scalar_expr, scalar_order, scalar_complexity in scalar_factors:
        for vector_key, vector_expr, vector_order, span, vector_complexity in frontier_vectors:
            order = max(scalar_order, vector_order)
            descriptor = f"s x (({scalar_expr}) {vector_expr})"
            priority = _priority(
                "scalar_weighted_cross",
                order,
                scalar_complexity,
                vector_complexity,
                span,
            )
            specs.append(
                (
                    f"overnight sphere {scalar_key} times {vector_key}",
                    "scalar_weighted_cross",
                    descriptor,
                    order,
                    scalar_key,
                    vector_key,
                    span,
                    priority,
                    scalar_complexity,
                    vector_complexity,
                )
            )
            if len(specs) >= spec_budget:
                break
        if len(specs) >= spec_budget:
            break

    blend_scalars = scalar_factors[:12]
    blend_vectors = frontier_vectors[: max(2, min(len(frontier_vectors), config.frontier_vector_limit))]
    for scalar_key, scalar_expr, scalar_order, scalar_complexity in blend_scalars:
        for left_index, (
            left_key,
            left_expr,
            left_order,
            left_span,
            left_complexity,
        ) in enumerate(blend_vectors):
            pair_limit = 0
            for right_key, right_expr, right_order, right_span, right_complexity in blend_vectors[
                left_index + 1 :
            ]:
                order = max(scalar_order, left_order, right_order)
                span = tuple(sorted(set(left_span + right_span)))
                family = (
                    "cross_atom_blend"
                    if "cross" in left_key or "cross" in right_key
                    else "two_atom_blend"
                )
                priority = _priority(
                    family,
                    order,
                    scalar_complexity,
                    left_complexity + right_complexity,
                    span,
                )
                specs.append(
                    (
                        f"overnight sphere {scalar_key} blend {left_key} {right_key}",
                        family,
                        f"s x (({scalar_expr}) {left_expr} + {right_expr})",
                        order,
                        scalar_key,
                        f"{left_key}+{right_key}",
                        span,
                        priority,
                        scalar_complexity,
                        left_complexity + right_complexity,
                    )
                )
                pair_limit += 1
                if pair_limit >= config.blend_pair_window or len(specs) >= spec_budget:
                    break
            if len(specs) >= spec_budget:
                break
        if len(specs) >= spec_budget:
            break

    candidates = tuple(
        _campaign_candidate_from_spec(spec)
        for spec in sorted(specs, key=lambda item: (-item[7], item[1], item[0]))
        if spec[0] not in attempted_names
    )
    return _action_queue(candidates, config.action_queue_limit)


def _extract_spectral_status(report: dict[str, Any]) -> str:
    spectral = report.get("spectral_report") or {}
    return str(spectral.get("status", "unknown"))


def _extract_gauge_risk(report: dict[str, Any]) -> float | None:
    value = report.get("gauge_risk_score")
    return None if value is None else float(value)


def _counter_dict(values: list[str | None]) -> dict[str, int]:
    return {
        ("none" if key is None else str(key)): count
        for key, count in sorted(Counter(values).items(), key=lambda item: (-item[1], str(item[0])))
    }


def _write_monitor_snapshot(
    monitor_json_path: Path | None,
    *,
    output_dir: Path,
    run_id: str,
    started_at: str,
    status: str,
    attempts: list[SolverAttemptRecord],
    candidate_count: int,
    rounds_completed: int,
    survivor: SolverAttemptRecord | None,
    recent_limit: int,
) -> None:
    if monitor_json_path is None:
        return
    snapshot = {
        "schema": "laxforge.campaign_monitor.v1",
        "run_id": run_id,
        "started_at": started_at,
        "updated_at": _utc_now(),
        "status": status,
        "attempt_count": len(attempts),
        "candidate_count": candidate_count,
        "rounds_completed": rounds_completed,
        "output_dir": str(output_dir),
        "survivor": survivor.as_dict() if survivor else None,
        "counts": {
            "attempt_status": _counter_dict([attempt.attempt_status for attempt in attempts]),
            "recommendation": _counter_dict([attempt.recommendation for attempt in attempts]),
            "formal_ansatz_status": _counter_dict(
                [attempt.formal_ansatz_status for attempt in attempts]
            ),
            "family": _counter_dict([attempt.family for attempt in attempts]),
            "validated_zcr": sum(1 for attempt in attempts if attempt.validated_zcr),
            "known_collision": sum(1 for attempt in attempts if attempt.known_collision),
            "formal_candidates_needing_matrix_validation": sum(
                1
                for attempt in attempts
                if attempt.attempt_status == "formal_zcr_candidate_needs_matrix_validation"
            ),
            "automated_survivors": sum(
                1 for attempt in attempts if attempt.attempt_status in SURVIVOR_STATUSES
            ),
        },
        "latest_attempts": [
            attempt.as_dict() for attempt in attempts[-max(1, recent_limit) :]
        ],
        "language_guard": {
            "claim": "evidence-only",
            "note": "All records require human mathematical and prior-art review before any external claim.",
        },
    }
    try:
        monitor_json_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = monitor_json_path.with_name(f"{monitor_json_path.name}.tmp")
        tmp_path.write_text(
            json.dumps(snapshot, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        tmp_path.replace(monitor_json_path)
    except OSError:
        return


def _attempt_candidate(candidate: OvernightCandidate) -> SolverAttemptRecord:
    start = time.monotonic()
    known_collision = False
    validated_zcr = False
    spectral_status = "unresolved"
    gauge_risk_score: float | None = None
    cyclic_fingerprint: str | None = None
    formal_ansatz_status: str | None = None
    formal_ansatz_unknowns: int | None = None
    obstruction_basis: tuple[str, ...] = ()
    failure_reasons = tuple(candidate.failure_reasons)
    attempt_status = "unsupported_current_solver_family"
    recommendation = "needs_human_review"

    if candidate.dossier.recommendation == "discard":
        attempt_status = "discard_control"
        recommendation = "discard"
        spectral_status = "absent"
        failure_reasons = (
            "zero-control candidate used only to verify campaign plumbing",
            "discarded before ansatz work",
        )
    elif candidate.family == "scalar_weighted_cross" and candidate.scalar_factor == "unit":
        if candidate.vector_atom == "sxx":
            report = solve_heisenberg_zcr_ansatz().as_dict()
            collision_report = report["collision_report"]
            gauge_report = report["gauge_report"]
            cyclic_report = report["cyclic_report"]
            validated_zcr = bool(report["validated"])
            known_collision = collision_report.get("classification") == "known"
            spectral_status = _extract_spectral_status(gauge_report)
            gauge_risk_score = _extract_gauge_risk(gauge_report)
            cyclic_fingerprint = str(cyclic_report.get("fingerprint"))
            attempt_status = "validated_known_collision"
            recommendation = "discard"
            failure_reasons = (
                "validated ZCR matches Heisenberg/symmetric-space known-family evidence",
                "discarded for discovery purposes by collision gate",
            )
        elif candidate.vector_atom == "sxxx":
            report = solve_sxxx_zcr_ansatz().as_dict()
            gauge_report = report["gauge_report"]
            cyclic_report = report["cyclic_report"]
            validated_zcr = bool(report["validated"])
            spectral_status = _extract_spectral_status(gauge_report)
            gauge_risk_score = _extract_gauge_risk(gauge_report)
            cyclic_fingerprint = str(cyclic_report.get("fingerprint"))
            obstruction_basis = tuple(str(item) for item in report["obstruction_basis"])
            attempt_status = "blocked_current_ansatz_family"
            recommendation = "blocked"
            failure_reasons = (
                "current low-order so(3) ansatz family is obstructed",
                "this is not a global falsification of all possible ZCRs",
            )
        elif candidate.vector_atom == "sx":
            report = solve_sx_zcr_ansatz().as_dict()
            gauge_report = report["gauge_report"]
            cyclic_report = report["cyclic_report"]
            spectral_status = _extract_spectral_status(gauge_report)
            gauge_risk_score = _extract_gauge_risk(gauge_report)
            cyclic_fingerprint = str(cyclic_report.get("fingerprint"))
            attempt_status = "blocked_first_potential_gate"
            recommendation = "blocked"
            obstruction_basis = tuple(str(item) for item in report["obstruction_basis"])
            failure_reasons = tuple(str(item) for item in report["obstruction_basis"])
    elif candidate.family in {"cross_atom_blend", "two_atom_blend", "scalar_weighted_cross"}:
        formal_report = solve_formal_sphere_ansatz(candidate, degree=3)
        formal_ansatz_status = formal_report.status
        formal_ansatz_unknowns = formal_report.unknown_count
        if formal_report.solved:
            attempt_status = "formal_zcr_candidate_needs_matrix_validation"
            obstruction_basis = ()
            failure_reasons = (
                "formal local-vector ansatz solved coefficient constraints",
                "explicit matrix reconstruction, gauge, cyclic, and prior-art gates remain required",
            )
        else:
            attempt_status = "formal_ansatz_obstruction_or_gap"
            obstruction_basis = formal_report.obstruction_basis
            failure_reasons = (
                "candidate is tangent by construction",
                f"formal ansatz status: {formal_report.status}",
                "matrix reconstruction and stronger gates did not run for this candidate",
            )

    elapsed = time.monotonic() - start
    if (
        validated_zcr
        and not known_collision
        and recommendation != "discard"
        and spectral_status not in {"absent", "fake_scalar_identity_lambda"}
    ):
        attempt_status = "automated_survivor_needs_human_prior_art_review"
        recommendation = "needs_human_review"

    return SolverAttemptRecord(
        candidate_name=candidate.name,
        family=candidate.family,
        order=candidate.order,
        descriptor=candidate.descriptor,
        attempt_status=attempt_status,
        recommendation=recommendation,
        validated_zcr=validated_zcr,
        known_collision=known_collision,
        spectral_status=spectral_status,
        gauge_risk_score=gauge_risk_score,
        cyclic_fingerprint=cyclic_fingerprint,
        formal_ansatz_status=formal_ansatz_status,
        formal_ansatz_unknowns=formal_ansatz_unknowns,
        obstruction_basis=obstruction_basis,
        failure_reasons=failure_reasons,
        elapsed_seconds=elapsed,
    )


def _write_checkpoint(
    output_dir: Path,
    *,
    run_id: str,
    started_at: str,
    status: str,
    attempts: list[SolverAttemptRecord],
    candidate_count: int,
    rounds_completed: int,
    survivor: SolverAttemptRecord | None,
    monitor_json_path: Path | None = None,
    monitor_recent_attempts: int = 50,
) -> None:
    checkpoint = {
        "run_id": run_id,
        "started_at": started_at,
        "updated_at": _utc_now(),
        "status": status,
        "attempt_count": len(attempts),
        "candidate_count": candidate_count,
        "rounds_completed": rounds_completed,
        "survivor": survivor.as_dict() if survivor else None,
        "latest_attempts": [attempt.as_dict() for attempt in attempts[-25:]],
    }
    (output_dir / "checkpoint.json").write_text(
        json.dumps(checkpoint, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_monitor_snapshot(
        monitor_json_path,
        output_dir=output_dir,
        run_id=run_id,
        started_at=started_at,
        status=status,
        attempts=attempts,
        candidate_count=candidate_count,
        rounds_completed=rounds_completed,
        survivor=survivor,
        recent_limit=monitor_recent_attempts,
    )


def run_solver_campaign(config: SolverCampaignConfig | None = None) -> SolverCampaignReport:
    """Run a checkpointed solver campaign until deadline, survivor, or queue exhaustion."""
    config = config or SolverCampaignConfig()
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    attempts_path = output_dir / "attempts.jsonl"
    started_at = _utc_now()
    run_id = "SOLVER-CAMPAIGN-001"
    deadline = time.monotonic() + config.wall_seconds
    low_order_seed = run_overnight_search(
        OvernightSearchConfig(
            target_count=500,
            action_queue_limit=50,
            max_derivative_order=4,
        )
    )
    known_low_order = [
        candidate
        for candidate in low_order_seed.candidates
        if candidate.family == "scalar_weighted_cross"
        and candidate.scalar_factor == "unit"
        and candidate.vector_atom in {"sx", "sxx", "sxxx"}
    ]
    attempts: list[SolverAttemptRecord] = []
    survivor: SolverAttemptRecord | None = None
    status = "running"
    attempted_names: set[str] = set()
    rounds_completed = 0
    candidate_count = 0
    _write_checkpoint(
        output_dir,
        run_id=run_id,
        started_at=started_at,
        status=status,
        attempts=attempts,
        candidate_count=candidate_count,
        rounds_completed=rounds_completed,
        survivor=survivor,
        monitor_json_path=config.monitor_json_path,
        monitor_recent_attempts=config.monitor_recent_attempts,
    )
    with attempts_path.open("a", encoding="utf-8") as handle:
        round_index = 0
        while time.monotonic() < deadline and survivor is None:
            current_order = config.max_derivative_order + round_index
            current_order = min(current_order, config.max_expansion_order)
            round_candidates = list(
                _bounded_campaign_candidates(
                    config,
                    max_order=current_order,
                    attempted_names=attempted_names,
                )
            )
            if round_index == 0:
                seen = {candidate.name for candidate in round_candidates}
                round_candidates = list(
                    candidate for candidate in known_low_order if candidate.name not in seen
                ) + round_candidates

            if not round_candidates:
                if current_order >= config.max_expansion_order:
                    status = "bounded_search_space_exhausted_without_survivor"
                    break
                round_index += 1
                continue

            candidate_count += len(round_candidates)
            for candidate in round_candidates:
                if time.monotonic() >= deadline:
                    status = "time_budget_exhausted"
                    break
                attempted_names.add(candidate.name)
                attempt = _attempt_candidate(candidate)
                attempts.append(attempt)
                handle.write(json.dumps(attempt.as_dict(), sort_keys=True) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
                if attempt.attempt_status in SURVIVOR_STATUSES:
                    survivor = attempt
                    status = "automated_survivor_found"
                    break
                if len(attempts) % config.checkpoint_every == 0:
                    _write_checkpoint(
                        output_dir,
                        run_id=run_id,
                        started_at=started_at,
                        status=status,
                        attempts=attempts,
                        candidate_count=candidate_count,
                        rounds_completed=rounds_completed,
                        survivor=survivor,
                        monitor_json_path=config.monitor_json_path,
                        monitor_recent_attempts=config.monitor_recent_attempts,
                    )
            rounds_completed += 1
            round_index += 1
            if status == "time_budget_exhausted":
                break

    if survivor is None and status == "running":
        status = "time_budget_exhausted" if time.monotonic() >= deadline else "candidate_queue_exhausted_without_survivor"

    finished_at = _utc_now()
    report = SolverCampaignReport(
        run_id=run_id,
        started_at=started_at,
        finished_at=finished_at,
        status=status,
        attempts=tuple(attempts),
        survivor=survivor,
        candidate_count=candidate_count,
        rounds_completed=rounds_completed,
        output_dir=str(output_dir),
    )
    _write_checkpoint(
        output_dir,
        run_id=run_id,
        started_at=started_at,
        status=status,
        attempts=attempts,
        candidate_count=candidate_count,
        rounds_completed=rounds_completed,
        survivor=survivor,
        monitor_json_path=config.monitor_json_path,
        monitor_recent_attempts=config.monitor_recent_attempts,
    )
    (output_dir / "summary.json").write_text(
        json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report
