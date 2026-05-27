"""Scaled deterministic candidate triage for the next discovery phase."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import sympy as sp

from laxforge.core.dossier import CandidateDossier
from laxforge.core.prior_art import classify_candidate
from laxforge.search.controlled import DiscoveryRunReport
from laxforge.search.formal_sphere_ansatz import solve_formal_sphere_ansatz


SCALAR_FACTORS: tuple[tuple[str, str, int], ...] = (
    ("unit", "1", 0),
    ("speed_sq", "<s_x,s_x>", 2),
    ("accel_sq", "<s_xx,s_xx>", 4),
    ("jerk_sq", "<s_xxx,s_xxx>", 6),
    ("sx_sxx", "<s_x,s_xx>", 3),
    ("sx_sxxx", "<s_x,s_xxx>", 4),
    ("sxx_sxxx", "<s_xx,s_xxx>", 5),
    ("sx_sxxxx", "<s_x,s_xxxx>", 5),
    ("sxx_sxxxx", "<s_xx,s_xxxx>", 6),
    ("curvature_energy", "<s_x,s_x> + <s_xx,s_xx>", 4),
)
VECTOR_ATOMS: tuple[tuple[str, str, int], ...] = (
    ("sx", "s_x", 1),
    ("sxx", "s_xx", 2),
    ("sxxx", "s_xxx", 3),
    ("sxxxx", "s_xxxx", 4),
    ("sxxxxx", "s_xxxxx", 5),
    ("sx_sxx_cross", "s_x x s_xx", 3),
)


@dataclass(frozen=True)
class BulkSearchConfig:
    """Configuration for the scaled deterministic triage phase."""

    target_count: int = 128
    include_zero_control: bool = True
    max_derivative_order: int = 5
    attempt_first_priority_ansatz: bool = True


@dataclass(frozen=True)
class BulkTriageCandidate:
    """One scaled-search candidate with conservative evidence gates."""

    name: str
    family: str
    descriptor: str
    flow_vector: tuple[str, str, str]
    order: int
    tangent_condition: sp.Expr
    tangent_status: str
    connection_status: str
    gate_summary: dict[str, Any]
    dossier: CandidateDossier
    failure_reasons: tuple[str, ...]
    priority_score: int
    scalar_factor: str | None = None
    vector_atom: str | None = None
    formal_ansatz_report: dict[str, object] | None = None

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible candidate record."""
        dossier = self.dossier.as_dict()
        dossier.pop("novelty_status", None)
        collision_report = dict(dossier.get("collision_report") or {})
        collision_report.pop("novelty_status", None)
        dossier["collision_report"] = collision_report
        return {
            "name": self.name,
            "family": self.family,
            "descriptor": self.descriptor,
            "flow_vector": list(self.flow_vector),
            "order": self.order,
            "tangent_condition": str(self.tangent_condition),
            "tangent_status": self.tangent_status,
            "connection_status": self.connection_status,
            "gate_summary": self.gate_summary,
            "dossier": dossier,
            "failure_reasons": list(self.failure_reasons),
            "priority_score": self.priority_score,
            "scalar_factor": self.scalar_factor,
            "vector_atom": self.vector_atom,
            "formal_ansatz_report": self.formal_ansatz_report,
        }

    def to_markdown(self) -> str:
        """Render a concise audit summary for this candidate."""
        lines = [
            f"# Candidate: {self.name}",
            "",
            f"- Family: `{self.family}`",
            f"- Descriptor: `{self.descriptor}`",
            f"- Classification: `{self.dossier.classification.value}`",
            f"- Recommendation: `{self.dossier.recommendation}`",
            f"- Order: {self.order}",
            f"- Tangent status: `{self.tangent_status}`",
            f"- Connection status: `{self.connection_status}`",
            f"- Priority score: {self.priority_score}",
            "",
            "## Gate Summary",
            "",
        ]
        for key in sorted(self.gate_summary):
            lines.append(f"- `{key}`: `{self.gate_summary[key]}`")
        lines.extend(["", "## Failure Reasons", ""])
        lines.extend(f"- {reason}" for reason in self.failure_reasons)
        if self.formal_ansatz_report:
            lines.extend(
                [
                    "",
                    "## Formal Ansatz Evidence",
                    "",
                    f"- Status: `{self.formal_ansatz_report['status']}`",
                    f"- Unknowns: `{self.formal_ansatz_report['unknown_count']}`",
                    f"- Equations: `{self.formal_ansatz_report['equation_count']}`",
                ]
            )
        return "\n".join(lines).rstrip() + "\n"


@dataclass(frozen=True)
class _FormalCandidateAdapter:
    """Minimal shape required by the formal sphere ansatz solver."""

    name: str
    order: int
    scalar_factor: str
    vector_atom: str


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _curvature_summary(status: str) -> dict[str, object]:
    if status == "validated_zero_control":
        return {
            "curvature_residual_zero": True,
            "curvature_terms_total": 0,
            "curvature_terms_nonzero": 0,
            "basis_split_complete": True,
            "status": status,
        }
    return {
        "curvature_residual_zero": False,
        "curvature_terms_total": 0,
        "curvature_terms_nonzero": None,
        "basis_split_complete": False,
        "status": status,
        "reason": "scaled triage records descriptors before constructing ZCR matrices",
    }


def _gauge_report() -> dict[str, object]:
    return {
        "gauge_risk_score": None,
        "status": "not_attempted",
        "spectral_report": {"status": "unresolved"},
        "reason": "no matrix pair constructed in scaled triage pass",
    }


def _obstructed_gauge_report() -> dict[str, object]:
    return {
        "gauge_risk_score": None,
        "status": "not_attempted_after_formal_obstruction",
        "spectral_report": {"status": "unresolved"},
        "reason": "formal local-vector ansatz did not produce a matrix pair",
    }


def _candidate(
    name: str,
    family: str,
    descriptor: str,
    order: int,
    priority_score: int,
    scalar_factor: str | None = None,
    vector_atom: str | None = None,
    attempt_formal_ansatz: bool = False,
    fake_pair: bool = False,
) -> BulkTriageCandidate:
    metadata = {"fake_pair": fake_pair} if fake_pair else {"sphere_tangent_flow": True}
    collision_report = classify_candidate(name, metadata=metadata)
    recommendation = "discard" if fake_pair else "needs_human_review"
    connection_status = "validated_zero_control" if fake_pair else "not_constructed_batch_triage"
    tangent_status = "tangent" if not fake_pair else "zero_control"
    tangent_condition = sp.Integer(0)
    failure_reasons = (
        (
            "zero flow and zero connection are retained only as a scaled-run control",
            "control is classified fake and recommended discard",
            "no spectral or conservation evidence is present",
        )
        if fake_pair
        else (
            "flow is tangent by cross-product construction",
            "zero-curvature matrix pair has not been constructed in the scaled triage pass",
            "spectral, gauge, cyclic, conservation, and Hamiltonian gates remain open",
            "sphere, Heisenberg, and symmetric-space collision checks remain active",
        )
    )
    gate_summary = {
        "tangent_condition": str(tangent_condition),
        "tangent_status": tangent_status,
        "curvature_validation": connection_status,
        "gauge_risk_score": None,
        "spectral_parameter_status": "unresolved",
        "conservation_evidence": "not_mined",
        "collision_classification": collision_report.classification.value,
        "recommendation": recommendation,
        "descriptor": descriptor,
        "priority_score": priority_score,
    }
    formal_ansatz_report = None
    curvature_summary = _curvature_summary(connection_status)
    gauge_report = _gauge_report()
    if attempt_formal_ansatz and scalar_factor and vector_atom and not fake_pair:
        formal_report = solve_formal_sphere_ansatz(
            _FormalCandidateAdapter(
                name=name,
                order=order,
                scalar_factor=scalar_factor,
                vector_atom=vector_atom,
            ),
            degree=3,
        )
        formal_ansatz_report = formal_report.as_dict()
        if formal_report.solved:
            connection_status = "formal_zcr_candidate_needs_matrix_validation"
            recommendation = "needs_human_review"
            curvature_summary = {
                "curvature_residual_zero": False,
                "curvature_terms_total": formal_report.equation_count,
                "curvature_terms_nonzero": None,
                "basis_split_complete": True,
                "status": connection_status,
                "formal_degree": formal_report.degree,
                "formal_unknowns": formal_report.unknown_count,
                "formal_basis_size": formal_report.basis_size,
                "solution": formal_report.solution,
                "reason": (
                    "formal local-vector ansatz solved coefficient constraints; matrix "
                    "reconstruction remains open"
                ),
            }
            failure_reasons = (
                "flow is tangent by cross-product construction",
                "degree-3 local-vector formal ansatz solved coefficient constraints",
                "explicit matrix reconstruction, gauge, cyclic, conservation, and Hamiltonian gates remain open",
                "sphere, Heisenberg, and symmetric-space collision checks remain active",
            )
        else:
            connection_status = "formal_ansatz_obstruction_current_family"
            recommendation = "blocked"
            curvature_summary = {
                "curvature_residual_zero": False,
                "curvature_terms_total": formal_report.equation_count,
                "curvature_terms_nonzero": len(formal_report.obstruction_basis),
                "basis_split_complete": True,
                "status": connection_status,
                "formal_degree": formal_report.degree,
                "formal_unknowns": formal_report.unknown_count,
                "formal_basis_size": formal_report.basis_size,
                "formal_ansatz_status": formal_report.status,
                "obstruction_basis": list(formal_report.obstruction_basis),
            }
            gauge_report = _obstructed_gauge_report()
            failure_reasons = (
                "flow is tangent by cross-product construction",
                "degree-3 local-vector formal ansatz with U=lambda*hat(s) has no solution",
                "obstruction basis is recorded for the supported formal residual equations",
                "broader matrix, gauge, cyclic, conservation, and Hamiltonian gates remain open",
                "sphere, Heisenberg, and symmetric-space collision checks remain active",
            )
        gate_summary.update(
            {
                "curvature_validation": connection_status,
                "formal_ansatz_status": formal_report.status,
                "formal_ansatz_unknowns": formal_report.unknown_count,
                "formal_ansatz_equations": formal_report.equation_count,
                "zcr_obstruction_basis": list(formal_report.obstruction_basis),
                "recommendation": recommendation,
            }
        )
    dossier = CandidateDossier(
        name=name,
        classification=collision_report.classification,
        curvature_summary=curvature_summary,
        gauge_report=gauge_report,
        collision_report=collision_report.as_dict(),
        conservation_report={"status": "not_mined", "num_conservation_laws_found": 0},
        hamiltonian_report={"status": "not_attempted", "verified": False},
        recommendation=recommendation,
        novelty_status=collision_report.novelty_status,
    )
    return BulkTriageCandidate(
        name=name,
        family=family,
        descriptor=descriptor,
        flow_vector=(f"component form deferred for {descriptor}", "", ""),
        order=order,
        tangent_condition=tangent_condition,
        tangent_status=tangent_status,
        connection_status=connection_status,
        gate_summary=gate_summary,
        dossier=dossier,
        failure_reasons=failure_reasons,
        priority_score=priority_score,
        scalar_factor=scalar_factor,
        vector_atom=vector_atom,
        formal_ansatz_report=formal_ansatz_report,
    )


def _candidate_specs(
    config: BulkSearchConfig,
) -> list[tuple[str, str, str, int, int, str, str]]:
    specs: list[tuple[str, str, str, int, int, str, str]] = []
    for scalar_key, scalar_expr, scalar_order in SCALAR_FACTORS:
        for vector_key, vector_expr, vector_order in VECTOR_ATOMS:
            if vector_order > config.max_derivative_order:
                continue
            order = max(vector_order, scalar_order)
            name = f"scaled sphere {scalar_key} times {vector_key}"
            descriptor = f"s x (({scalar_expr}) {vector_expr})"
            priority = 26 + min(18, order * 2) + (3 if scalar_key == "unit" else 0)
            specs.append(
                (name, "single_factor_cross", descriptor, order, priority, scalar_key, vector_key)
            )

    blend_scalars = SCALAR_FACTORS[:5]
    for scalar_key, scalar_expr, scalar_order in blend_scalars:
        for left_index, (left_key, left_expr, left_order) in enumerate(VECTOR_ATOMS):
            for right_key, right_expr, right_order in VECTOR_ATOMS[left_index + 1 :]:
                if max(left_order, right_order) > config.max_derivative_order:
                    continue
                order = max(left_order, right_order, scalar_order)
                name = f"scaled sphere {scalar_key} blend {left_key} {right_key}"
                descriptor = f"s x (({scalar_expr}) {left_expr} + {right_expr})"
                priority = 24 + min(20, order * 2) + (2 if "sxxx" in name else 0)
                specs.append(
                    (
                        name,
                        "two_atom_blend",
                        descriptor,
                        order,
                        priority,
                        scalar_key,
                        f"{left_key}+{right_key}",
                    )
                )
    return specs


def run_scaled_candidate_search(config: BulkSearchConfig | None = None) -> DiscoveryRunReport:
    """Run DIS-006 as a deterministic 100+ candidate triage batch."""
    config = config or BulkSearchConfig()
    if config.target_count < 100:
        raise ValueError("DIS-006 scaled candidate search requires at least 100 candidates")

    candidates: list[BulkTriageCandidate] = []
    if config.include_zero_control:
        candidates.append(
            _candidate(
                name="scaled sphere zero-flow zero-connection control",
                family="control",
                descriptor="s_t = 0 with U = V = 0",
                order=0,
                priority_score=0,
                fake_pair=True,
            )
        )

    top_spec_name = "scaled sphere unit times sxxxxx"
    for name, family, descriptor, order, priority, scalar_factor, vector_atom in _candidate_specs(
        config
    ):
        if len(candidates) >= config.target_count:
            break
        candidates.append(
            _candidate(
                name=name,
                family=family,
                descriptor=descriptor,
                order=order,
                priority_score=priority,
                scalar_factor=scalar_factor,
                vector_atom=vector_atom,
                attempt_formal_ansatz=config.attempt_first_priority_ansatz
                and name == top_spec_name,
            )
        )

    if len(candidates) < config.target_count:
        raise RuntimeError(
            f"DIS-006 generated only {len(candidates)} candidates; requested {config.target_count}"
        )

    return DiscoveryRunReport(
        run_id="DIS-006",
        arena="scaled deterministic sphere-tangent triage search",
        candidates=tuple(candidates),
    )


def _run_markdown(report: DiscoveryRunReport) -> str:
    lines = [
        f"# Discovery Run {report.run_id}",
        "",
        f"- Arena: {report.arena}",
        f"- Candidates: {len(report.candidates)}",
        f"- Ranking basis: {report.ranking_basis}",
        "",
        "| Candidate | Family | Order | Recommendation | Connection |",
        "|---|---|---:|---|---|",
    ]
    for candidate in report.candidates:
        lines.append(
            "| "
            f"{candidate.name} | "
            f"`{candidate.family}` | "
            f"{candidate.order} | "
            f"`{candidate.dossier.recommendation}` | "
            f"`{candidate.connection_status}` |"
        )
    return "\n".join(lines).rstrip() + "\n"


def write_scaled_candidate_search(
    report: DiscoveryRunReport, output_dir: str | Path, overwrite: bool = True
) -> Path:
    """Write DIS-006 JSON and Markdown only when explicitly requested."""
    output_path = Path(output_dir)
    if output_path.exists() and any(output_path.iterdir()) and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing DIS-006 output: {output_path}")
    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / "run.json").write_text(
        json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_path / "run.md").write_text(_run_markdown(report), encoding="utf-8")
    candidates_dir = output_path / "candidates"
    candidates_dir.mkdir(exist_ok=True)
    for index, candidate in enumerate(report.candidates):
        stem = f"{index:03d}_{_slug(candidate.name)}"
        (candidates_dir / f"{stem}.json").write_text(
            json.dumps(candidate.as_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (candidates_dir / f"{stem}.md").write_text(candidate.to_markdown(), encoding="utf-8")
    return output_path
