"""Controlled DIS-002 sphere-valued low-order search."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import sympy as sp

from laxforge.algebra.truncated_poly import TruncatedPoly
from laxforge.core.dossier import CandidateDossier
from laxforge.core.gauge import analyze_gauge_risk
from laxforge.core.prior_art import CandidateClassification, classify_candidate
from laxforge.core.zero_curvature import curvature_report
from laxforge.search.controlled import DiscoveryRunReport
from laxforge.search.sphere_zcr import (
    solve_heisenberg_zcr_ansatz,
    solve_sx_zcr_ansatz,
    solve_sxxx_zcr_ansatz,
)


@dataclass(frozen=True)
class SphereSearchConfig:
    """Configuration for the fixed low-order DIS-002 sphere search."""

    max_order: int = 3
    include_zero_control: bool = True
    include_heisenberg_template: bool = True
    attempt_sx_ansatz: bool = True
    attempt_sxxx_ansatz: bool = True


@dataclass(frozen=True)
class SphereFlowCandidate:
    """Sphere-flow candidate with gate evidence and conservative disposition."""

    name: str
    flow_vector: tuple[sp.Expr, sp.Expr, sp.Expr]
    order: int
    tangent_condition: sp.Expr
    tangent_status: str
    connection_status: str
    gate_summary: dict[str, Any]
    dossier: CandidateDossier
    failure_reasons: tuple[str, ...]
    zcr_report: dict[str, object] | None = None

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible candidate record."""
        return {
            "name": self.name,
            "flow_vector": [str(component) for component in self.flow_vector],
            "order": self.order,
            "tangent_condition": str(self.tangent_condition),
            "tangent_status": self.tangent_status,
            "connection_status": self.connection_status,
            "gate_summary": self.gate_summary,
            "dossier": self.dossier.as_dict(),
            "failure_reasons": list(self.failure_reasons),
            "zcr_report": self.zcr_report,
        }

    def to_markdown(self) -> str:
        """Render a concise candidate summary without promotion language."""
        lines = [
            f"# Candidate: {self.name}",
            "",
            f"- Classification: `{self.dossier.classification.value}`",
            f"- Recommendation: `{self.dossier.recommendation}`",
            f"- Order: {self.order}",
            f"- Tangent status: `{self.tangent_status}`",
            f"- Connection status: `{self.connection_status}`",
            f"- Tangent condition: `{self.tangent_condition}`",
            "",
            "## Gate Summary",
            "",
        ]
        for key in sorted(self.gate_summary):
            lines.append(f"- `{key}`: `{self.gate_summary[key]}`")
        if self.failure_reasons:
            lines.extend(["", "## Failure Reasons", ""])
            lines.extend(f"- {reason}" for reason in self.failure_reasons)
        if self.zcr_report:
            solution = self.zcr_report.get("solution") or self.zcr_report.get(
                "consistency_solution"
            )
            lines.extend(
                [
                    "",
                    "## ZCR Evidence",
                    "",
                    f"- Validated: `{self.zcr_report['validated']}`",
                    f"- Solution: `{solution}`",
                    f"- Cyclic fingerprint: `{self.zcr_report['cyclic_report']['fingerprint']}`",
                ]
            )
            if self.zcr_report.get("obstruction_basis"):
                lines.extend(["", "## Ansatz Obstruction", ""])
                lines.extend(f"- {term}" for term in self.zcr_report["obstruction_basis"])
        collisions = self.dossier.collision_report.get("collisions", [])
        if collisions:
            lines.extend(["", "## Collision Warnings", ""])
            lines.extend(f"- {collision}" for collision in collisions)
        return "\n".join(lines).rstrip() + "\n"


def _sphere_fields() -> tuple[sp.Symbol, sp.Symbol, sp.Symbol, sp.Matrix]:
    x, t = sp.symbols("x t")
    s1 = sp.Function("s1")(x, t)
    s2 = sp.Function("s2")(x, t)
    s3 = sp.Function("s3")(x, t)
    return x, t, sp.Symbol("lambda"), sp.Matrix([s1, s2, s3])


def _zero_curvature_summary() -> dict[str, object]:
    zero = TruncatedPoly.zero(order=1)
    return curvature_report([[zero, zero], [zero, zero]]).as_dict()


def _unvalidated_curvature_summary() -> dict[str, object]:
    return {
        "curvature_residual_zero": False,
        "curvature_terms_total": 0,
        "curvature_terms_nonzero": None,
        "basis_split_complete": False,
        "status": "not_constructed",
        "reason": "no nontrivial zero-curvature representation constructed in DIS-002 pass",
    }


def _candidate_gate_summary(
    tangent_condition: sp.Expr,
    tangent_status: str,
    connection_status: str,
    gauge_report: dict[str, object],
    conservation_status: str,
    collision_classification: CandidateClassification,
    recommendation: str,
) -> dict[str, object]:
    spectral_report = gauge_report.get("spectral_report") or {}
    return {
        "tangent_condition": str(tangent_condition),
        "tangent_status": tangent_status,
        "curvature_validation": connection_status,
        "gauge_risk_score": gauge_report.get("gauge_risk_score"),
        "spectral_parameter_status": spectral_report.get("status", "unknown"),
        "conservation_evidence": conservation_status,
        "collision_classification": collision_classification.value,
        "recommendation": recommendation,
    }


def _build_candidate(
    name: str,
    flow_vector: sp.Matrix,
    order: int,
    s: sp.Matrix,
    lambda_symbol: sp.Symbol,
    fake_pair: bool = False,
    heisenberg_template: bool = False,
    sx_ansatz_attempt: bool = False,
    sxxx_ansatz_attempt: bool = False,
) -> SphereFlowCandidate:
    tangent_condition = sp.simplify(s.dot(flow_vector))
    tangent_status = "tangent" if tangent_condition == 0 else "not_tangent"
    U = sp.zeros(2)
    V = sp.zeros(2)
    gauge_report = analyze_gauge_risk(U, V, lambda_symbol=lambda_symbol).as_dict()
    zcr_report = None
    metadata = {
        "fake_pair": fake_pair,
        "sphere_tangent_flow": True,
        "heisenberg_template": heisenberg_template,
    }
    if heisenberg_template:
        heisenberg_report = solve_heisenberg_zcr_ansatz()
        zcr_report = heisenberg_report.as_dict()
        if heisenberg_report.validated:
            metadata["known_heisenberg_zcr"] = True
            gauge_report = heisenberg_report.gauge_report
    if sx_ansatz_attempt:
        sx_report = solve_sx_zcr_ansatz()
        zcr_report = sx_report.as_dict()
        metadata["sx_potential_obstruction"] = (
            not sx_report.validated and not sx_report.first_potential_opened
        )
        metadata["sx_recursive_tower_gate"] = (
            sx_report.first_potential_opened and not sx_report.validated
        )
        gauge_report = sx_report.gauge_report
    if sxxx_ansatz_attempt:
        sxxx_report = solve_sxxx_zcr_ansatz()
        zcr_report = sxxx_report.as_dict()
        metadata["sxxx_ansatz_obstruction"] = not sxxx_report.validated
        gauge_report = sxxx_report.gauge_report

    collision_report = classify_candidate(name, metadata=metadata)
    if fake_pair or metadata.get("known_heisenberg_zcr"):
        recommendation = "discard"
    elif metadata.get("sx_potential_obstruction") or metadata.get("sx_recursive_tower_gate"):
        recommendation = "blocked"
    elif metadata.get("sxxx_ansatz_obstruction"):
        recommendation = "blocked"
    else:
        recommendation = "needs_human_review"
    if fake_pair:
        connection_status = "validated_zero_control"
        curvature_summary = _zero_curvature_summary()
    elif metadata.get("known_heisenberg_zcr"):
        connection_status = "validated_known_zcr"
        curvature_summary = {
            "curvature_residual_zero": True,
            "curvature_terms_total": 2,
            "curvature_terms_nonzero": 0,
            "basis_split_complete": True,
            "status": "validated_mod_constraints",
            "constraints_used": zcr_report["constraints_used"] if zcr_report else [],
        }
    elif metadata.get("sx_potential_obstruction"):
        connection_status = "blocked_first_potential_gate"
        curvature_summary = {
            "curvature_residual_zero": False,
            "curvature_terms_total": int((zcr_report or {}).get("formal_equations", 0)),
            "curvature_terms_nonzero": len((zcr_report or {}).get("obstruction_basis", [])),
            "basis_split_complete": True,
            "status": "blocked_first_potential_gate",
            "constraints_used": zcr_report["constraints_used"] if zcr_report else [],
            "obstruction_basis": zcr_report["obstruction_basis"] if zcr_report else [],
        }
    elif metadata.get("sx_recursive_tower_gate"):
        connection_status = "blocked_recursive_nonlocal_tower_gate"
        residual_basis = (zcr_report or {}).get("nonlocal_residual_basis", {})
        recursive_residual = residual_basis.get("lambda^2_after_first_potential", [])
        curvature_summary = {
            "curvature_residual_zero": False,
            "curvature_terms_total": sum(len(terms) for terms in residual_basis.values()),
            "curvature_terms_nonzero": len(recursive_residual),
            "basis_split_complete": True,
            "status": "blocked_recursive_nonlocal_tower_gate",
            "constraints_used": zcr_report["constraints_used"] if zcr_report else [],
            "covering_equations": zcr_report["covering_equations"] if zcr_report else [],
            "obstruction_basis": zcr_report["obstruction_basis"] if zcr_report else [],
        }
    elif metadata.get("sxxx_ansatz_obstruction"):
        connection_status = "ansatz_obstruction_current_family"
        curvature_summary = {
            "curvature_residual_zero": False,
            "curvature_terms_total": sum(
                len(terms)
                for terms in (zcr_report or {}).get("reduced_residual_basis", {}).values()
            ),
            "curvature_terms_nonzero": len((zcr_report or {}).get("obstruction_basis", [])),
            "basis_split_complete": True,
            "status": "ansatz_obstruction_current_family",
            "constraints_used": zcr_report["constraints_used"] if zcr_report else [],
            "obstruction_basis": zcr_report["obstruction_basis"] if zcr_report else [],
        }
    else:
        connection_status = "no_validated_zcr"
        curvature_summary = _unvalidated_curvature_summary()
    conservation_status = "not_mined"

    if fake_pair:
        failure_reasons = (
            "zero connection is a fake pair",
            "no nontrivial spectral data",
            "control candidate exists only to verify dossier plumbing",
        )
    elif metadata.get("known_heisenberg_zcr"):
        failure_reasons = (
            "validated ZCR matches a Heisenberg/symmetric-space known-family template",
            "candidate is discarded for DIS-002 discovery purposes",
            "conservation and Hamiltonian evidence not mined for this candidate",
        )
    elif metadata.get("sx_potential_obstruction"):
        failure_reasons = (
            "supported U=lambda*hat(s) family requires D_x(W) = s cross s_x",
            "current local-vector ansatz has no local potential W for that gate",
            "nonlocal potentials or different spatial matrices remain untested",
        )
    elif metadata.get("sx_recursive_tower_gate"):
        failure_reasons = (
            "local-vector ansatz has no local W with D_x(W) = s cross s_x",
            "first nonlocal potential p1_x = s cross s_x cancels the first residual",
            "finite one-potential truncation leaves lambda^2 residual s cross p1",
            "recursive nonlocal tower or alternate-U closure remains unproved",
        )
    elif metadata.get("sxxx_ansatz_obstruction"):
        failure_reasons = (
            "current low-order so(3) ansatz family is obstructed",
            "this is not a global falsification of possible ZCR structure",
            "expand the ansatz family or move to the next frontier candidate",
        )
    else:
        failure_reasons = (
            "no nontrivial zero-curvature representation validated",
            "spectral parameter status unresolved",
            "conservation and Hamiltonian evidence not mined for this candidate",
        )
    if heisenberg_template and not metadata.get("known_heisenberg_zcr"):
        failure_reasons = failure_reasons + (
            "known-family collision warnings include Heisenberg/symmetric-space families",
        )

    gate_summary = _candidate_gate_summary(
        tangent_condition=tangent_condition,
        tangent_status=tangent_status,
        connection_status=connection_status,
        gauge_report=gauge_report,
        conservation_status=conservation_status,
        collision_classification=collision_report.classification,
        recommendation=recommendation,
    )
    if zcr_report:
        gate_summary.update(
            {
                "zcr_validated": zcr_report["validated"],
                "zcr_solution": zcr_report.get("solution")
                or zcr_report.get("consistency_solution"),
                "cyclic_fingerprint": zcr_report["cyclic_report"]["fingerprint"],
            }
        )
        if "obstruction_basis" in zcr_report:
            gate_summary["zcr_obstruction_basis"] = zcr_report["obstruction_basis"]
    dossier = CandidateDossier(
        name=name,
        classification=collision_report.classification,
        curvature_summary=curvature_summary,
        gauge_report=gauge_report,
        collision_report=collision_report.as_dict(),
        conservation_report={"status": conservation_status, "num_conservation_laws_found": 0},
        hamiltonian_report={"status": "not_attempted", "verified": False},
        recommendation=recommendation,
        novelty_status=collision_report.novelty_status,
    )
    return SphereFlowCandidate(
        name=name,
        flow_vector=tuple(flow_vector),
        order=order,
        tangent_condition=tangent_condition,
        tangent_status=tangent_status,
        connection_status=connection_status,
        gate_summary=gate_summary,
        dossier=dossier,
        failure_reasons=failure_reasons,
        zcr_report=zcr_report,
    )


def run_sphere_low_order_search(config: SphereSearchConfig | None = None) -> DiscoveryRunReport:
    """Run the deterministic DIS-002 low-order sphere search."""
    config = config or SphereSearchConfig()
    x, _t, lambda_symbol, s = _sphere_fields()
    zero_flow = sp.zeros(3, 1)
    candidates: list[SphereFlowCandidate] = []

    if config.include_zero_control:
        candidates.append(
            _build_candidate(
                name="sphere zero-flow zero-connection control",
                flow_vector=zero_flow,
                order=0,
                s=s,
                lambda_symbol=lambda_symbol,
                fake_pair=True,
            )
        )

    flow_templates: list[tuple[str, int, sp.Matrix, bool]] = [
        ("sphere s_cross_s_x tangent candidate", 1, s.cross(s.diff(x)), False),
        (
            "sphere s_cross_s_xx Heisenberg-shaped candidate",
            2,
            s.cross(s.diff(x, 2)),
            config.include_heisenberg_template,
        ),
        ("sphere s_cross_s_xxx exploratory candidate", 3, s.cross(s.diff(x, 3)), False),
    ]
    for name, order, flow, heisenberg_template in flow_templates:
        if order <= config.max_order:
            candidates.append(
                _build_candidate(
                    name=name,
                    flow_vector=flow,
                    order=order,
                    s=s,
                    lambda_symbol=lambda_symbol,
                    heisenberg_template=heisenberg_template,
                    sx_ansatz_attempt=order == 1 and config.attempt_sx_ansatz,
                    sxxx_ansatz_attempt=order == 3 and config.attempt_sxxx_ansatz,
                )
            )

    return DiscoveryRunReport(
        run_id="DIS-002",
        arena="sphere-valued tangent-projected low-order flow search",
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
        "| Candidate | Classification | Recommendation | Tangent | Connection |",
        "|---|---|---|---|---|",
    ]
    for candidate in report.candidates:
        lines.append(
            "| "
            f"{candidate.name} | "
            f"`{candidate.dossier.classification.value}` | "
            f"`{candidate.dossier.recommendation}` | "
            f"`{candidate.tangent_status}` | "
            f"`{candidate.connection_status}` |"
        )
    return "\n".join(lines).rstrip() + "\n"


def write_discovery_run(
    report: DiscoveryRunReport, output_dir: str | Path, overwrite: bool = True
) -> Path:
    """Write JSON and Markdown summaries for a discovery run only when requested."""
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
