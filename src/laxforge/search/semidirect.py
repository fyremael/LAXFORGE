"""Controlled DIS-001 semidirect deformation search."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import sympy as sp

from laxforge.algebra.finite import (
    FiniteAlgebraElement,
    fa_zero_curvature,
    upper_triangular_semidirect_algebra,
)
from laxforge.algebra.truncated_poly import TruncatedPoly
from laxforge.core.dossier import CandidateDossier
from laxforge.core.gauge import analyze_gauge_risk
from laxforge.core.prior_art import classify_candidate
from laxforge.core.solver import ConstraintSolveConfig, solve_symbolic_constraints
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


def _fa_matrix_to_expr(matrix: list[list[FiniteAlgebraElement]]) -> sp.Matrix:
    return sp.Matrix([[entry.as_expr() for entry in row] for row in matrix])


def _fa_matrix_as_strings(matrix: list[list[FiniteAlgebraElement]]) -> list[list[str]]:
    return [[str(entry.as_expr()) for entry in row] for row in matrix]


def _fa_matrix_subs(
    matrix: list[list[FiniteAlgebraElement]], substitutions: dict[sp.Symbol, sp.Expr]
) -> list[list[FiniteAlgebraElement]]:
    return [
        [
            FiniteAlgebraElement.from_coeffs(
                [sp.simplify(coeff.subs(substitutions)) for coeff in entry.coeffs],
                entry.algebra,
            )
            for entry in row
        ]
        for row in matrix
    ]


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


def _non_split_semidirect_evidence() -> dict[str, Any]:
    x, t, lam = sp.symbols("x t lambda")
    u = sp.Function("u")(x, t)
    v = sp.Function("v")(x, t)
    w = sp.Function("w")(x, t)
    alpha, beta = sp.symbols("alpha beta")
    algebra = upper_triangular_semidirect_algebra()
    lam_unit = FiniteAlgebraElement.from_coeffs([lam], algebra)
    q = FiniteAlgebraElement.from_coeffs([u, v, w], algebra)
    qx = q.diff(x)
    qxx = qx.diff(x)
    q2 = q**2
    q3 = q2 * q
    diag_a = FiniteAlgebraElement.from_coeffs([-4 * lam**3], algebra) + q2 * (-2 * lam)
    diagonal_commutator = q * qx - qx * q

    U = [[lam_unit, q], [-q, -lam_unit]]
    upper_entry = q * (-4 * lam**2) + qx * (-2 * lam) - qxx - q3 * 2
    lower_entry = q * (4 * lam**2) + qx * (-2 * lam) + qxx + q3 * 2
    uncorrected_V = [
        [
            diag_a,
            upper_entry,
        ],
        [
            lower_entry,
            -diag_a,
        ],
    ]
    uncorrected_curvature = fa_zero_curvature(U, uncorrected_V, x, t)
    uncorrected_report = curvature_report(uncorrected_curvature)
    corrected_V_ansatz = [
        [
            diag_a + diagonal_commutator * alpha,
            upper_entry,
        ],
        [
            lower_entry,
            -diag_a + diagonal_commutator * beta,
        ],
    ]
    corrected_curvature_ansatz = fa_zero_curvature(U, corrected_V_ansatz, x, t)
    correction_report = curvature_report(corrected_curvature_ansatz)
    diagonal_equations = tuple(
        coefficient
        for key in ("(0,0)", "(1,1)")
        for coefficient in correction_report.entries[key].simplified_coefficients
    )
    solve_report = solve_symbolic_constraints(
        diagonal_equations,
        (alpha, beta),
        ConstraintSolveConfig(
            max_equations=6,
            max_unknowns=2,
            allow_nonlinear=False,
            allow_groebner=False,
        ),
    )
    correction_solution = solve_report.solution if solve_report.solved else {}
    V = _fa_matrix_subs(corrected_V_ansatz, correction_solution)
    curvature = fa_zero_curvature(U, V, x, t)
    report = curvature_report(curvature)
    diagonal_zero = all(
        term.is_zero
        for key in ("(0,0)", "(1,1)")
        for term in report.entries[key].terms
    )
    lower_is_negative = all(
        sp.simplify(upper + lower) == 0
        for upper, lower in zip(
            report.entries["(0,1)"].simplified_coefficients,
            report.entries["(1,0)"].simplified_coefficients,
        )
    )
    flow_equations = tuple(
        sp.simplify(coefficient)
        for coefficient in report.entries["(0,1)"].simplified_coefficients
    )
    validated_as_flow_equations = solve_report.solved and diagonal_zero and lower_is_negative
    gauge_report = analyze_gauge_risk(
        _fa_matrix_to_expr(U),
        _fa_matrix_to_expr(V),
        lambda_symbol=lam,
    ).as_dict()
    return {
        "algebra_name": algebra.name,
        "algebra_basis": list(algebra.basis),
        "algebra_product_table": algebra.product_table(),
        "associative": algebra.is_associative(),
        "U": _fa_matrix_as_strings(U),
        "V": _fa_matrix_as_strings(V),
        "uncorrected_V": _fa_matrix_as_strings(uncorrected_V),
        "uncorrected_curvature_report": uncorrected_report.as_dict(),
        "curvature_report": report.as_dict(),
        "gauge_report": gauge_report,
        "diagonal_correction": {
            "ansatz": "V00 += alpha [q,q_x], V11 += beta [q,q_x]",
            "commutator": str(diagonal_commutator.as_expr()),
            "solve_report": solve_report.as_dict(),
            "diagonal_zero_after_solve": diagonal_zero,
            "lower_left_is_negative_upper_right": lower_is_negative,
        },
        "flow_equations": {
            "basis": list(algebra.basis),
            "upper_right": [str(equation) for equation in flow_equations],
            "lower_left_is_negative_upper_right": lower_is_negative,
        },
        "validated_as_flow_equations": validated_as_flow_equations,
        "matrix_pair_constructed": True,
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
    evidence = _non_split_semidirect_evidence()
    collision_report = classify_candidate(
        "semidirect non-split product deformation probe",
        metadata={"non_split_semidirect_probe": True},
    )
    recommendation = "needs_human_review"
    connection_status = (
        "validated_non_split_flow_equations"
        if evidence["validated_as_flow_equations"]
        else "constructed_non_split_curvature"
    )
    solve_status = (
        "solved_bounded_non_split_diagonal_correction"
        if evidence["validated_as_flow_equations"]
        else "residuals_unresolved_non_split_product"
    )
    curvature_summary = {
        **evidence["curvature_report"],
        "status": connection_status,
    }
    gate_summary = _candidate_gate_summary(
        connection_status,
        solve_status,
        evidence["gauge_report"],
        "not_mined",
        collision_report.classification.value,
        recommendation,
    )
    dossier = CandidateDossier(
        name="semidirect non-split product deformation probe",
        classification=collision_report.classification,
        curvature_summary=curvature_summary,
        gauge_report=evidence["gauge_report"],
        collision_report=collision_report.as_dict(),
        conservation_report={"status": "not_mined", "num_conservation_laws_found": 0},
        hamiltonian_report={"status": "not_attempted", "verified": False},
        recommendation=recommendation,
        novelty_status=collision_report.novelty_status,
    )
    return SemidirectDeformationCandidate(
        name="semidirect non-split product deformation probe",
        algebra_label=str(evidence["algebra_name"]),
        order=2,
        ansatz_degree=3,
        connection_status=connection_status,
        solve_status=solve_status,
        gate_summary=gate_summary,
        dossier=dossier,
        failure_reasons=(
            "bounded solver fixes the diagonal residual with V00 += [q,q_x] and V11 += [q,q_x]",
            "off-diagonal curvature entries define three coupled non-split flow equations",
            "gauge-preserving reductions, conservation, Hamiltonian, and prior-art gates remain open",
        ),
        evidence=evidence,
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
