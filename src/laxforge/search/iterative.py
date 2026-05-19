"""Iterative discovery frontier orchestration.

The frontier records which candidates survive as process work, not as conclusions.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from laxforge.search.bulk import run_scaled_candidate_search
from laxforge.search.run_matrix import (
    run_cohomological_deformation_search,
    run_density_matrix_search,
    run_nonlocal_covering_search,
)
from laxforge.search.semidirect import run_semidirect_deformation_search
from laxforge.search.sphere import SphereSearchConfig, run_sphere_low_order_search


@dataclass(frozen=True)
class DiscoveryIterationConfig:
    """Configuration for the deterministic iterative discovery frontier."""

    max_iterations: int = 3
    frontier_limit: int = 160
    include_dis001: bool = True
    include_dis002: bool = True
    include_dis003: bool = True
    include_dis004: bool = True
    include_dis005: bool = True
    include_dis006: bool = True
    attempt_sxxx_ansatz: bool = True


@dataclass(frozen=True)
class FrontierCandidate:
    """A candidate's current position in the discovery process."""

    item_id: str
    name: str
    lane: str
    iteration: int
    recommendation: str
    classification: str
    connection_status: str
    process_disposition: str
    potential_status: str
    priority: int
    next_action: str
    gate_gaps: tuple[str, ...]
    evidence_summary: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible frontier candidate record."""
        return {
            "item_id": self.item_id,
            "name": self.name,
            "lane": self.lane,
            "iteration": self.iteration,
            "recommendation": self.recommendation,
            "classification": self.classification,
            "connection_status": self.connection_status,
            "process_disposition": self.process_disposition,
            "potential_status": self.potential_status,
            "priority": self.priority,
            "next_action": self.next_action,
            "gate_gaps": list(self.gate_gaps),
            "evidence_summary": list(self.evidence_summary),
        }


@dataclass(frozen=True)
class DiscoveryIteration:
    """One deterministic pass through the current evidence lanes."""

    index: int
    run_ids: tuple[str, ...]
    candidates_seen: tuple[str, ...]
    frontier_ids: tuple[str, ...]
    discarded_ids: tuple[str, ...]
    notes: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible iteration record."""
        return {
            "index": self.index,
            "run_ids": list(self.run_ids),
            "candidates_seen": list(self.candidates_seen),
            "frontier_ids": list(self.frontier_ids),
            "discarded_ids": list(self.discarded_ids),
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class IterativeDiscoveryReport:
    """Current iterative discovery process report."""

    run_id: str
    process_status: str
    stop_reason: str
    iterations: tuple[DiscoveryIteration, ...]
    frontier: tuple[FrontierCandidate, ...]
    discarded: tuple[FrontierCandidate, ...]
    all_records: tuple[FrontierCandidate, ...]

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible iterative discovery report."""
        return {
            "run_id": self.run_id,
            "process_status": self.process_status,
            "stop_reason": self.stop_reason,
            "iterations": [iteration.as_dict() for iteration in self.iterations],
            "frontier": [record.as_dict() for record in self.frontier],
            "discarded": [record.as_dict() for record in self.discarded],
            "all_records": [record.as_dict() for record in self.all_records],
        }

    def to_markdown(self) -> str:
        """Render a concise process summary."""
        lines = [
            f"# Discovery Process {self.run_id}",
            "",
            f"- Process status: `{self.process_status}`",
            f"- Stop reason: {self.stop_reason}",
            f"- Active frontier: {len(self.frontier)}",
            f"- Discarded records: {len(self.discarded)}",
            "",
            "| Candidate | Lane | Status | Priority | Next Action |",
            "|---|---|---|---:|---|",
        ]
        for record in self.frontier:
            lines.append(
                "| "
                f"{record.name} | "
                f"{record.lane} | "
                f"`{record.potential_status}` | "
                f"{record.priority} | "
                f"{record.next_action} |"
            )
        if not self.frontier:
            lines.append("| none | - | - | 0 | no queued action |")
        lines.extend(["", "## Discarded", ""])
        lines.extend(
            f"- {record.name}: `{record.classification}`, `{record.connection_status}`"
            for record in self.discarded
        )
        return "\n".join(lines).rstrip() + "\n"


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return cleaned or "item"


def _candidate_record(candidate: Any, lane: str, iteration: int) -> FrontierCandidate:
    dossier = candidate.dossier
    recommendation = str(dossier.recommendation)
    classification = str(dossier.classification.value)
    connection_status = str(getattr(candidate, "connection_status", "unknown"))
    solve_status = str(getattr(candidate, "solve_status", ""))
    name = str(candidate.name)

    if recommendation == "discard":
        return FrontierCandidate(
            item_id=_slug(name),
            name=name,
            lane=lane,
            iteration=iteration,
            recommendation=recommendation,
            classification=classification,
            connection_status=connection_status,
            process_disposition="discard",
            potential_status="discarded",
            priority=0,
            next_action="No process action; retained as control or collision evidence.",
            gate_gaps=tuple(candidate.failure_reasons),
            evidence_summary=(
                f"classified as {classification}",
                f"connection status {connection_status}",
            ),
        )

    if recommendation == "blocked":
        return FrontierCandidate(
            item_id=_slug(name),
            name=name,
            lane=lane,
            iteration=iteration,
            recommendation=recommendation,
            classification=classification,
            connection_status=connection_status,
            process_disposition="frontier",
            potential_status="blocked_by_ansatz_obstruction",
            priority=36,
            next_action=(
                "Current low-order so(3) ansatz family is obstructed; "
                "expand the ansatz family after the next queued candidate."
            ),
            gate_gaps=tuple(candidate.failure_reasons),
            evidence_summary=(
                "zero-curvature attempt recorded an obstruction in the current ansatz family",
                "broader ZCR search remains open",
            ),
        )

    if lane == "DIS-001" and solve_status == "unsupported_non_split_product":
        return FrontierCandidate(
            item_id=_slug(name),
            name=name,
            lane=lane,
            iteration=iteration,
            recommendation=recommendation,
            classification=classification,
            connection_status=connection_status,
            process_disposition="frontier",
            potential_status="blocked_by_missing_capability",
            priority=54,
            next_action="Implement non-split coefficient multiplication, then construct zero-curvature equations.",
            gate_gaps=(
                "coefficient algebra does not yet support the requested product",
                "zero-curvature residual not constructed",
                "gauge and cyclic checks cannot run until a matrix pair exists",
            ),
            evidence_summary=(
                "semidirect deformation probe remains structurally interesting",
                "current gate evidence is incomplete",
            ),
        )

    if lane == "DIS-002" and connection_status == "no_validated_zcr":
        order = int(getattr(candidate, "order", 99))
        priority = 68 if order == 3 else 58
        solver = (
            "Run a low-order so(3) ansatz with higher-derivative V terms and gauge/cyclic checks."
            if order == 3
            else "Run a minimal so(3) ansatz falsification pass with spectral and gauge checks."
        )
        return FrontierCandidate(
            item_id=_slug(name),
            name=name,
            lane=lane,
            iteration=iteration,
            recommendation=recommendation,
            classification=classification,
            connection_status=connection_status,
            process_disposition="frontier",
            potential_status="promising_potential",
            priority=priority,
            next_action=solver,
            gate_gaps=(
                "no nontrivial zero-curvature representation validated",
                "spectral parameter status unresolved",
                "conservation and Hamiltonian evidence not mined",
                "known sphere-family collision checks remain active",
            ),
            evidence_summary=(
                "sphere constraint tangent condition passed",
                "candidate is deterministic and low order",
                "not discarded because a ZCR attempt has not yet falsified it",
            ),
        )

    if lane == "DIS-003" and recommendation == "needs_human_review":
        priority = int(getattr(candidate, "priority_score", 34))
        return FrontierCandidate(
            item_id=_slug(name),
            name=name,
            lane=lane,
            iteration=iteration,
            recommendation=recommendation,
            classification=classification,
            connection_status=connection_status,
            process_disposition="frontier",
            potential_status="density_matrix_pending",
            priority=priority,
            next_action=(
                "Attempt density-matrix ZCR construction, then run isospectral and trace "
                "invariant gates."
            ),
            gate_gaps=tuple(candidate.failure_reasons),
            evidence_summary=(
                "density-matrix lane restored to DIS-003",
                "matrix pair and invariant gates remain open",
                "candidate remains review-only until solver gates run",
            ),
        )

    if lane == "DIS-004" and recommendation == "needs_human_review":
        priority = int(getattr(candidate, "priority_score", 28))
        return FrontierCandidate(
            item_id=_slug(name),
            name=name,
            lane=lane,
            iteration=iteration,
            recommendation=recommendation,
            classification=classification,
            connection_status=connection_status,
            process_disposition="frontier",
            potential_status="nonlocal_covering_pending",
            priority=priority,
            next_action="Construct the smallest pseudopotential ZCR ansatz and record nonlocal gates.",
            gate_gaps=tuple(candidate.failure_reasons),
            evidence_summary=(
                "nonlocal covering lane records explicit open gates",
                "pseudopotential compatibility remains unproved",
            ),
        )

    if lane == "DIS-005" and recommendation == "needs_human_review":
        priority = int(getattr(candidate, "priority_score", 30))
        return FrontierCandidate(
            item_id=_slug(name),
            name=name,
            lane=lane,
            iteration=iteration,
            recommendation=recommendation,
            classification=classification,
            connection_status=connection_status,
            process_disposition="frontier",
            potential_status="cohomology_pending",
            priority=priority,
            next_action="Separate cocycle evidence from gauge coboundaries before any stronger gate.",
            gate_gaps=tuple(candidate.failure_reasons),
            evidence_summary=(
                "cohomological deformation lane records cocycle/coboundary risk",
                "gauge quotient evidence remains open",
            ),
        )

    if lane == "DIS-006" and recommendation == "needs_human_review":
        priority = int(getattr(candidate, "priority_score", 30))
        return FrontierCandidate(
            item_id=_slug(name),
            name=name,
            lane=lane,
            iteration=iteration,
            recommendation=recommendation,
            classification=classification,
            connection_status=connection_status,
            process_disposition="frontier",
            potential_status="batch_triage_pending",
            priority=priority,
            next_action=(
                "Select by priority, then attempt the smallest supported ZCR ansatz with "
                "gauge, cyclic, and collision checks."
            ),
            gate_gaps=tuple(candidate.failure_reasons),
            evidence_summary=(
                "scaled DIS-006 descriptor is tangent by construction",
                "matrix pair is not constructed in the batch pass",
                "candidate remains review-only until solver gates run",
            ),
        )

    return FrontierCandidate(
        item_id=_slug(name),
        name=name,
        lane=lane,
        iteration=iteration,
        recommendation=recommendation,
        classification=classification,
        connection_status=connection_status,
        process_disposition="frontier",
        potential_status="needs_review",
        priority=40,
        next_action="Run the next honest gate supported by the current codebase.",
        gate_gaps=tuple(candidate.failure_reasons),
        evidence_summary=(
            f"classified as {classification}",
            f"recommendation {recommendation}",
        ),
    )


def run_iterative_discovery(
    config: DiscoveryIterationConfig | None = None,
) -> IterativeDiscoveryReport:
    """Run the current lanes as a deterministic iterative discovery frontier."""
    config = config or DiscoveryIterationConfig()
    lane_reports = []
    if config.include_dis001:
        lane_reports.append(run_semidirect_deformation_search())
    if config.include_dis002:
        lane_reports.append(
            run_sphere_low_order_search(
                SphereSearchConfig(attempt_sxxx_ansatz=config.attempt_sxxx_ansatz)
            )
        )
    if config.include_dis003:
        lane_reports.append(run_density_matrix_search())
    if config.include_dis004:
        lane_reports.append(run_nonlocal_covering_search())
    if config.include_dis005:
        lane_reports.append(run_cohomological_deformation_search())
    if config.include_dis006:
        lane_reports.append(run_scaled_candidate_search())

    all_records: list[FrontierCandidate] = []
    for report in lane_reports:
        all_records.extend(
            _candidate_record(candidate, report.run_id, iteration=1)
            for candidate in report.candidates
        )

    discarded = tuple(record for record in all_records if record.process_disposition == "discard")
    frontier = tuple(
        sorted(
            (record for record in all_records if record.process_disposition == "frontier"),
            key=lambda record: (-record.priority, record.lane, record.name),
        )[: config.frontier_limit]
    )

    iterations = [
        DiscoveryIteration(
            index=1,
            run_ids=tuple(report.run_id for report in lane_reports),
            candidates_seen=tuple(record.item_id for record in all_records),
            frontier_ids=tuple(record.item_id for record in frontier),
            discarded_ids=tuple(record.item_id for record in discarded),
            notes=(
                "Seed lanes generated deterministic controls and probes.",
                "Discarded controls and known-family collisions were removed from the active queue.",
            ),
        )
    ]
    if config.max_iterations > 1:
        iterations.append(
            DiscoveryIteration(
                index=2,
                run_ids=("FRONTIER",),
                candidates_seen=tuple(record.item_id for record in frontier),
                frontier_ids=tuple(record.item_id for record in frontier),
                discarded_ids=(),
                notes=(
                    "Frontier candidates require the next solver or algebra capability before reranking.",
                    "No candidate passes all gates in this pass.",
                ),
            )
        )

    process_status = "frontier_active" if frontier else "all_candidates_discarded"
    stop_reason = (
        "active frontier awaits next ansatz, gauge, cyclic, conservation, or algebra gate"
        if frontier
        else "all current candidates were discarded by conservative gates"
    )
    return IterativeDiscoveryReport(
        run_id="ITER-001",
        process_status=process_status,
        stop_reason=stop_reason,
        iterations=tuple(iterations[: config.max_iterations]),
        frontier=frontier,
        discarded=discarded,
        all_records=tuple(all_records),
    )


def write_iterative_discovery_report(
    report: IterativeDiscoveryReport, output_dir: str | Path, overwrite: bool = True
) -> Path:
    """Write JSON and Markdown summaries only when explicitly requested."""
    output_path = Path(output_dir)
    if output_path.exists() and any(output_path.iterdir()) and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing iterative discovery output: {output_path}")
    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / "run.json").write_text(
        json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_path / "run.md").write_text(report.to_markdown(), encoding="utf-8")
    return output_path
