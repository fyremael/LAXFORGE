"""Controlled DIS-001 semidirect deformation search."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import sympy as sp

from laxforge.algebra.truncated_poly import TruncatedPoly
from laxforge.core.dossier import CandidateDossier
from laxforge.core.gauge import analyze_gauge_risk
from laxforge.core.prior_art import classify_candidate
from laxforge.core.zero_curvature import curvature_report, zero_curvature
from laxforge.examples.mkdv_second_jet import build_pair, expected_flow_components
from laxforge.search.controlled import DiscoveryRunReport


@dataclass(frozen=True)
class SemidirectSearchConfig:
    """Configuration for the first small DIS-001 deformation pass."""

    max_order: int = 3
    include_zero_control: bool = True
    include_rescaling_control: bool = True
    include_non_split_probe: bool = True


@dataclass(frozen=True)
class SemidirectDeformationCandidate:
    """DIS-001 candidate with conservative gate evidence."""

    name: str
    algebra_label: str
    order: int
    ansatz_degree: int
    connection_status: str
    solve_status: str
    gate_summary: dict[str, Any]
    dossier: CandidateDossier
    failure_reasons: tuple[str, ...]
    evidence: dict[str, Any]

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible candidate record."""
        return {
            "name": self.name,
            "algebra_label": self.algebra_label,
            "order": self.order,
            "ansatz_degree": self.ansatz_degree,
            "connection_status": self.connection_status,
            "solve_status": self.solve_status,
            "gate_summary": self.gate_summary,
            "dossier": self.dossier.as_dict(),
            "failure_reasons": list(self.failure_reasons),
            "evidence": self.evidence,
        }

    def to_markdown(self) -> str:
        """Render a concise candidate summary without promotion language."""
        lines = [
            f"# Candidate: {self.name}",
            "",
            f"- Algebra: `{self.algebra_label}`",
            f"- Classification: `{self.dossier.classification.value}`",
            f"- Recommendation: `{self.dossier.recommendation}`",
            f"- Connection status: `{self.connection_status}`",
            f"- Solve status: `{self.solve_status}`",
            "",
            "## Gate Summary",
            "",
        ]
        for key in sorted(self.gate_summary):
            lines.append(f"- `{key}`: `{self.gate_summary[key]}`")
        if self.failure_reasons:
            lines.extend(["", "## Failure Reasons", ""])
            lines.extend(f"- {reason}" for reason in self.failure_reasons)
        collisions = self.dossier.collision_report.get("collisions", [])
        if collisions:
            lines.extend(["", "## Collision Warnings", ""])
            lines.extend(f"- {collision}" for collision in collisions)
        return "\n".join(lines).rstrip() + "\n"


def _tp_matrix_to_expr(matrix: list[list[TruncatedPoly]]) -> sp.Matrix:
    return sp.Matrix([[entry.as_expr() for entry in row] for row in matrix])


def _zero_curvature_summary() -> dict[str, object]:
    zero = TruncatedPoly.zero(order=1)
    return curvature_report([[zero, zero], [zero, zero]]).as_dict()


def _split_nilpotent_mkdv_evidence() -> dict[str, Any]:
    x, t, lam, _fields, U, V = build_pair(order=2)
    curvature = zero_curvature(U, V, x, t)
    report = curvature_report(curvature)
    expected = expected_flow_components(x, t)[:2]

    upper_right = report.entries["(0,1)"].simplified_coefficients
    lower_left = report.entries["(1,0)"].simplified_coefficients
    diag_00 = report.entries["(0,0)"].simplified_coefficients
    diag_11 = report.entries["(1,1)"].simplified_coefficients
    checks = {
        "diag_00_zero": all(sp.simplify(component) == 0 for component in diag_00),
        "diag_11_zero": all(sp.simplify(component) == 0 for component in diag_11),
        "upper_right_expected": all(
            sp.simplify(actual - wanted) == 0 for actual, wanted in zip(upper_right, expected)
        ),
        "lower_left_negative_expected": all(
            sp.simplify(actual + wanted) == 0 for actual, wanted in zip(lower_left, expected)
        ),
    }
    gauge_report = analyze_gauge_risk(
        _tp_matrix_to_expr(U),
        _tp_matrix_to_expr(V),
        lambda_symbol=lam,
    ).as_dict()
    return {
        "checks": checks,
        "curvature_report": report.as_dict(),
        "expected_flow_coefficients": [str(component) for component in expected],
        "gauge_report": gauge_report,
        "validated_as_flow_equations": all(checks.values()),
    }


def _candidate_gate_summary(
    connection_status: str,
    solve_status: str,
    gauge_report: dict[str, object] | None,
    conservation_status: str,
    collision_classification: str,
    recommendation: str,
) -> dict[str, object]:
    spectral_report = (gauge_report or {}).get("spectral_report") or {}
    return {
        "curvature_validation": connection_status,
        "solve_status": solve_status,
        "gauge_risk_score": (gauge_report or {}).get("gauge_risk_score"),
        "spectral_parameter_status": spectral_report.get("status", "unknown"),
        "conservation_evidence": conservation_status,
        "collision_classification": collision_classification,
        "recommendation": recommendation,
    }


def _build_zero_control(lambda_symbol: sp.Symbol) -> SemidirectDeformationCandidate:
    zero = sp.zeros(2)
    gauge_report = analyze_gauge_risk(zero, zero, lambda_symbol=lambda_symbol).as_dict()
    collision_report = classify_candidate(
        "semidirect zero-connection control",
        metadata={"fake_pair": True},
    )
    recommendation = "discard"
    gate_summary = _candidate_gate_summary(
        "validated_zero_control",
        "not_attempted",
        gauge_report,
        "not_mined",
        collision_report.classification.value,
        recommendation,
    )
    dossier = CandidateDossier(
        name="semidirect zero-connection control",
        classification=collision_report.classification,
        curvature_summary=_zero_curvature_summary(),
        gauge_report=gauge_report,
        collision_report=collision_report.as_dict(),
        conservation_report={"status": "not_mined", "num_conservation_laws_found": 0},
        hamiltonian_report={"status": "not_attempted", "verified": False},
        recommendation=recommendation,
        novelty_status=collision_report.novelty_status,
    )
    return SemidirectDeformationCandidate(
        name="semidirect zero-connection control",
        algebra_label="zero pair over scalar algebra",
        order=0,
        ansatz_degree=0,
        connection_status="validated_zero_control",
        solve_status="not_attempted",
        gate_summary=gate_summary,
        dossier=dossier,
        failure_reasons=(
            "zero connection is a fake pair",
            "control candidate exists only to verify DIS-001 plumbing",
        ),
        evidence={"validated_as_flow_equations": False},
    )


def _build_split_nilpotent_control() -> SemidirectDeformationCandidate:
    evidence = _split_nilpotent_mkdv_evidence()
    collision_report = classify_candidate(
        "semidirect split nilpotent mKdV lift control",
        metadata={"semidirect_lift": True, "known_projection": "scalar mKdV AKNS"},
    )
    recommendation = "discard"
    connection_status = (
        "validated_known_semidirect_zcr"
        if evidence["validated_as_flow_equations"]
        else "residuals_unresolved"
    )
    gate_summary = _candidate_gate_summary(
        connection_status,
        "solved_by_known_mkdv_template",
        evidence["gauge_report"],
        "not_mined",
        collision_report.classification.value,
        recommendation,
    )
    dossier = CandidateDossier(
        name="semidirect split nilpotent mKdV lift control",
        classification=collision_report.classification,
        curvature_summary=evidence["curvature_report"],
        gauge_report=evidence["gauge_report"],
        collision_report=collision_report.as_dict(),
        conservation_report={"status": "not_mined", "num_conservation_laws_found": 0},
        hamiltonian_report={"status": "not_attempted", "verified": False},
        recommendation=recommendation,
        novelty_status=collision_report.novelty_status,
    )
    return SemidirectDeformationCandidate(
        name="semidirect split nilpotent mKdV lift control",
        algebra_label="R[eps]/(eps^2) perturbative semidirect lift",
        order=1,
        ansatz_degree=3,
        connection_status=connection_status,
        solve_status="solved_by_known_mkdv_template",
        gate_summary=gate_summary,
        dossier=dossier,
        failure_reasons=(
            "validated ZCR is the known perturbative mKdV semidirect lift",
            "known integrable-coupling and nilpotent-lift collision zones apply",
            "candidate is discarded for DIS-001 discovery purposes",
        ),
        evidence=evidence,
    )


def _build_rescaling_control() -> SemidirectDeformationCandidate:
    evidence = _split_nilpotent_mkdv_evidence()
    collision_report = classify_candidate(
        "semidirect rescaled perturbation parameter control",
        metadata={"field_rescaling_control": True},
    )
    recommendation = "discard"
    gate_summary = _candidate_gate_summary(
        "field_rescaling_control",
        "parameter_removable_by_field_rescaling",
        evidence["gauge_report"],
        "not_mined",
        collision_report.classification.value,
        recommendation,
    )
    dossier = CandidateDossier(
        name="semidirect rescaled perturbation parameter control",
        classification=collision_report.classification,
        curvature_summary=evidence["curvature_report"],
        gauge_report=evidence["gauge_report"],
        collision_report=collision_report.as_dict(),
        conservation_report={"status": "not_mined", "num_conservation_laws_found": 0},
        hamiltonian_report={"status": "not_attempted", "verified": False},
        recommendation=recommendation,
        novelty_status=collision_report.novelty_status,
    )
    return SemidirectDeformationCandidate(
        name="semidirect rescaled perturbation parameter control",
        algebra_label="R[eps]/(eps^2) with removable perturbation scaling",
        order=1,
        ansatz_degree=3,
        connection_status="field_rescaling_control",
        solve_status="parameter_removable_by_field_rescaling",
        gate_summary=gate_summary,
        dossier=dossier,
        failure_reasons=(
            "rescaling the perturbation component does not create a distinct candidate",
            "parameter-control candidate is discarded",
        ),
        evidence={**evidence, "rescaling_parameter_status": "removable"},
    )


def _build_non_split_probe() -> SemidirectDeformationCandidate:
    collision_report = classify_candidate(
        "semidirect non-split product deformation probe",
        metadata={"non_split_semidirect_probe": True},
    )
    recommendation = "needs_human_review"
    curvature_summary = {
        "curvature_residual_zero": False,
        "curvature_terms_total": 0,
        "curvature_terms_nonzero": None,
        "basis_split_complete": False,
        "status": "not_constructed",
        "reason": "current coefficient algebra supports truncated nilpotent products only",
    }
    gate_summary = _candidate_gate_summary(
        "not_constructed",
        "unsupported_non_split_product",
        None,
        "not_mined",
        collision_report.classification.value,
        recommendation,
    )
    dossier = CandidateDossier(
        name="semidirect non-split product deformation probe",
        classification=collision_report.classification,
        curvature_summary=curvature_summary,
        gauge_report=None,
        collision_report=collision_report.as_dict(),
        conservation_report={"status": "not_mined", "num_conservation_laws_found": 0},
        hamiltonian_report={"status": "not_attempted", "verified": False},
        recommendation=recommendation,
        novelty_status=collision_report.novelty_status,
    )
    return SemidirectDeformationCandidate(
        name="semidirect non-split product deformation probe",
        algebra_label="non-split semidirect product probe",
        order=2,
        ansatz_degree=3,
        connection_status="not_constructed",
        solve_status="unsupported_non_split_product",
        gate_summary=gate_summary,
        dossier=dossier,
        failure_reasons=(
            "non-split multiplication is not implemented in the current coefficient algebra",
            "zero-curvature equations were not constructed for this probe",
            "candidate remains a queued algebra task rather than validated evidence",
        ),
        evidence={"validated_as_flow_equations": False, "required_algebra": "non-split product"},
    )


def run_semidirect_deformation_search(
    config: SemidirectSearchConfig | None = None,
) -> DiscoveryRunReport:
    """Run the deterministic DIS-001 semidirect deformation search."""
    config = config or SemidirectSearchConfig()
    lam = sp.Symbol("lambda")
    candidates: list[SemidirectDeformationCandidate] = []

    if config.include_zero_control:
        candidates.append(_build_zero_control(lam))
    if config.max_order >= 1:
        candidates.append(_build_split_nilpotent_control())
        if config.include_rescaling_control:
            candidates.append(_build_rescaling_control())
    if config.max_order >= 2 and config.include_non_split_probe:
        candidates.append(_build_non_split_probe())

    return DiscoveryRunReport(
        run_id="DIS-001",
        arena="small semidirect deformation search around mKdV AKNS",
        candidates=tuple(candidates),
    )


def _run_markdown(report: DiscoveryRunReport) -> str:
    lines = [
        f"# Discovery Run {report.run_id}",
        "",
        f"- Arena: {report.arena}",
        f"- Ranking basis: {report.ranking_basis}",
        f"- Candidates: {len(report.candidates)}",
        "",
        "| Candidate | Classification | Recommendation | Connection | Solve |",
        "|---|---|---|---|---|",
    ]
    for candidate in report.candidates:
        lines.append(
            "| "
            f"{candidate.name} | "
            f"`{candidate.dossier.classification.value}` | "
            f"`{candidate.dossier.recommendation}` | "
            f"`{candidate.connection_status}` | "
            f"`{candidate.solve_status}` |"
        )
    return "\n".join(lines).rstrip() + "\n"


def write_semidirect_discovery_run(
    report: DiscoveryRunReport, output_dir: str | Path, overwrite: bool = True
) -> Path:
    """Write JSON and Markdown summaries only when explicitly requested."""
    output_path = Path(output_dir)
    if output_path.exists() and any(output_path.iterdir()) and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing discovery output: {output_path}")
    output_path.mkdir(parents=True, exist_ok=True)

    (output_path / "run.json").write_text(
        json.dumps(report.as_dict(), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (output_path / "run.md").write_text(_run_markdown(report), encoding="utf-8")

    candidates_dir = output_path / "candidates"
    candidates_dir.mkdir(exist_ok=True)
    for index, candidate in enumerate(report.candidates):
        stem = f"{index:02d}_{candidate.name.replace(' ', '_')}"
        (candidates_dir / f"{stem}.json").write_text(
            json.dumps(candidate.as_dict(), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (candidates_dir / f"{stem}.md").write_text(candidate.to_markdown(), encoding="utf-8")

    return output_path
