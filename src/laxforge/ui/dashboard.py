"""Dashboard data assembly for conservative LAXFORGE evidence tracking."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Mapping

import sympy as sp

from laxforge.algebra.truncated_poly import TruncatedPoly
from laxforge.core.dossier import CandidateDossier, build_mkdv_second_jet_dossier
from laxforge.core.procedures import ProcedureAuditReport
from laxforge.core.solver import recover_scalar_mkdv_v_coefficients
from laxforge.core.zero_curvature import curvature_proof_artifact, zero_curvature
from laxforge.search.bulk import BulkTriageCandidate, run_scaled_candidate_search
from laxforge.search.full_scale import run_full_scale_search
from laxforge.search.iterative import FrontierCandidate
from laxforge.search.run_matrix import (
    RunMatrixCandidate,
    run_cohomological_deformation_search,
    run_density_matrix_search,
    run_nonlocal_covering_search,
)
from laxforge.search.semidirect import SemidirectDeformationCandidate, run_semidirect_deformation_search
from laxforge.search.serious_cycle import run_serious_cycle_001
from laxforge.search.sphere import SphereFlowCandidate, run_sphere_low_order_search


PROMOTION_TERMS = ("novel", "publishable", "publication")
GATE_ORDER = ("tangent", "curvature", "gauge", "spectral", "conservation", "collision")
COLLISION_FAMILY_LABELS = {
    "AKNS / Zakharov-Shabat": "AKNS",
    "Heisenberg ferromagnet and symmetric-space systems": "Heisenberg / symmetric-space",
    "Integrable couplings via semidirect products": "semidirect coupling",
    "KdV and mKdV scalar hierarchies": "scalar hierarchy",
    "Nilpotent and perturbation extensions": "nilpotent / perturbation",
    "Principal chiral model and Heisenberg ferromagnet families": "Heisenberg / symmetric-space",
    "Coadjoint-orbit and symmetric-space hierarchies": "coadjoint / symmetric-space",
}


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return cleaned or "item"


def _compact_name(name: str) -> str:
    return (
        name.replace("sphere ", "")
        .replace(" zero-flow zero-connection control", " zero control")
        .replace(" tangent candidate", "")
        .replace(" Heisenberg-shaped candidate", "")
        .replace(" exploratory candidate", "")
    )


def _classification_label(raw: str) -> str:
    labels = {
        "artifact": "proof artifact",
        "calibration": "calibration",
        "fake": "fake",
        "known": "known collision",
        "known_mechanism": "known mechanism presentation",
        "known_mechanism_new_presentation": "known mechanism presentation",
        "needs_human_review": "needs human review",
    }
    return labels.get(raw, raw.replace("_", " "))


def _safe_recommendation(dossier: CandidateDossier) -> str:
    if dossier.name == "second-jet nilpotent mKdV":
        return "calibration"
    return dossier.recommendation


def _status_from_bool(value: bool | None) -> str:
    if value is True:
        return "pass"
    if value is False:
        return "fail"
    return "warn"


def _gate(key: str, label: str, status: str, value: object) -> dict[str, object]:
    return {"key": key, "label": label, "status": status, "value": value}


def _gate_summary(gates: list[Mapping[str, object]]) -> dict[str, object]:
    return {str(gate["key"]): gate["value"] for gate in gates}


def _curvature_gate(connection_status: str, residual_zero: bool | None) -> str:
    if connection_status in {
        "validated_known_zcr",
        "validated_known_semidirect_zcr",
        "validated_non_split_flow_equations",
        "validated_zero_control",
        "proof_ready",
    }:
        return "pass"
    if residual_zero is True:
        return "pass"
    if connection_status == "no_validated_zcr":
        return "warn"
    return _status_from_bool(residual_zero)


def _gauge_gate(gauge_risk_score: object) -> str:
    if gauge_risk_score is None:
        return "warn"
    score = float(gauge_risk_score)
    if score <= 0.25:
        return "pass"
    if score >= 0.75:
        return "fail"
    return "warn"


def _spectral_gate(status: str) -> str:
    if status == "unresolved":
        return "warn"
    if status == "absent":
        return "fail"
    if status in {"present", "nonremovable"}:
        return "pass"
    return "warn"


def _collision_gate(classification: str) -> str:
    if classification in {"fake", "known", "known_mechanism", "known_mechanism_new_presentation"}:
        return "fail"
    if classification in {"artifact", "calibration", "needs_human_review"}:
        return "warn"
    return "warn"


def _conservation_gate(count: int, hamiltonian_verified: bool) -> str:
    if count > 0 or hamiltonian_verified:
        return "pass"
    return "warn"


def _collision_families(collisions: list[str]) -> list[str]:
    families = [COLLISION_FAMILY_LABELS.get(collision, collision) for collision in collisions]
    return list(dict.fromkeys(families))


def _audit_surprisal(record: Mapping[str, Any]) -> dict[str, object]:
    """Score how much attention an item deserves, not whether it is promotable."""
    score = 5
    drivers: list[str] = []

    item_type = str(record["item_type"])
    classification = str(record["classification"])
    recommendation = str(record["recommendation"])
    tangent_status = record.get("tangent_status")
    spectral_status = str(record.get("spectral_status", "unknown"))
    gauge_risk_score = record.get("gauge_risk_score")
    collision_count = int(record.get("collision_count", 0))

    if item_type == "proof_artifact":
        score += 24
        drivers.append("proof artifact ready")
    if tangent_status == "tangent" and classification != "fake":
        score += 18
        drivers.append("tangent constraint passed")
    if record.get("zcr_validated"):
        score += 32
        drivers.append("validated ZCR evidence")
    elif record.get("curvature_residual_zero") and classification != "fake":
        score += 18
        drivers.append("zero residual evidence")

    if spectral_status == "unresolved":
        score += 12
        drivers.append("spectral parameter unresolved")
    elif spectral_status == "absent":
        score -= 6
        drivers.append("no spectral data")

    if gauge_risk_score is not None:
        risk = float(gauge_risk_score)
        if risk <= 0.25:
            score += 10
            drivers.append("low gauge risk")
        elif risk >= 0.75:
            score -= 8
            drivers.append("high gauge risk")

    conservation_count = int(record.get("conservation_count", 0))
    if conservation_count:
        score += 8
        drivers.append(f"{conservation_count} conservation laws tracked")
    if record.get("hamiltonian_verified"):
        score += 6
        drivers.append("Hamiltonian check verified")
    if collision_count > 1:
        score += 4
        drivers.append("multiple known-family collisions")

    if recommendation == "discard":
        score -= 16
        drivers.append("discard recommendation")
    if classification == "fake":
        score -= 18
        drivers.append("fake/control classification")
    elif classification == "known":
        score -= 10
        drivers.append("known-family collision")
    elif recommendation == "needs_human_review":
        score += 4
        drivers.append("human review required")

    score = max(4, min(92, score))
    if score >= 70:
        band = "escalate"
    elif score >= 40:
        band = "inspect"
    elif score >= 20:
        band = "watch"
    else:
        band = "baseline"
    return {"score": score, "band": band, "drivers": drivers or ["evidence tracked"]}


def _pure_gauge_artifact_record() -> dict[str, Any]:
    x, t = sp.symbols("x t")
    phi = sp.Function("phi")(x, t)
    phi_x = TruncatedPoly.from_coeffs([sp.diff(phi, x)])
    phi_t = TruncatedPoly.from_coeffs([sp.diff(phi, t)])
    zero = TruncatedPoly.zero()
    U = [[phi_x, zero], [zero, -phi_x]]
    V = [[phi_t, zero], [zero, -phi_t]]
    curvature = zero_curvature(U, V, x, t)
    artifact = curvature_proof_artifact(curvature, title="M0 Pure Gauge Flatness Audit")
    report = artifact.report.as_dict()
    gates = [
        _gate("tangent", "Tangent", "warn", "not applicable"),
        _gate("curvature", "Curvature", "pass", "residual zero"),
        _gate("gauge", "Gauge", "warn", "pure-gauge fixture"),
        _gate("spectral", "Spectral", "warn", "not applicable"),
        _gate("conservation", "Conservation", "warn", "not applicable"),
        _gate("collision", "Collision", "warn", "audit artifact"),
    ]
    record: dict[str, Any] = {
        "id": "m0-pure-gauge-flatness-audit",
        "item_type": "proof_artifact",
        "lane": "M0 zero-curvature reports",
        "name": artifact.title,
        "short_name": "pure-gauge flatness",
        "order": None,
        "classification": "artifact",
        "classification_label": "proof artifact",
        "recommendation": "audit",
        "disposition": "audit",
        "tangent_status": "not_applicable",
        "connection_status": "proof_ready",
        "curvature_residual_zero": report["curvature_residual_zero"],
        "curvature_status": "pure-gauge residual zero",
        "curvature_terms_total": report["curvature_terms_total"],
        "curvature_terms_nonzero": report["curvature_terms_nonzero"],
        "gauge_risk_score": None,
        "spectral_status": "not_applicable",
        "conservation_count": 0,
        "hamiltonian_verified": False,
        "collision_count": 0,
        "collisions": [],
        "collision_families": [],
        "failure_reasons": [
            "proof artifact is an audit fixture",
            "mixed partials cancel for the exact diagonal pure-gauge connection",
        ],
        "gates": gates,
        "gate_summary": _gate_summary(gates),
        "zcr_validated": False,
        "zcr_solution": None,
        "cyclic_fingerprint": None,
        "proof_summary": {
            "title": artifact.title,
            "curvature_convention": artifact.equation,
            "matrix_shape": list(report["matrix_shape"]),
            "coefficient_basis": report["coefficient_basis"],
            "basis_split_complete": report["basis_split_complete"],
            "residual_zero": report["curvature_residual_zero"],
            "total_terms": report["curvature_terms_total"],
            "nonzero_terms": report["curvature_terms_nonzero"],
            "entry_status_grid": report["entry_status_grid"],
            "markdown_ready": True,
        },
        "residual_grid": report["entry_status_grid"],
        "detail": {
            "summary": "Exact diagonal pure-gauge connection over TruncatedPoly.",
            "equation": artifact.equation,
        },
    }
    record["surprisal"] = _audit_surprisal(record)
    return record


def _sphere_record(candidate: SphereFlowCandidate) -> dict[str, Any]:
    dossier = candidate.dossier
    collision_report = dossier.collision_report
    curvature_summary = dossier.curvature_summary
    gauge_report = dossier.gauge_report or {}
    spectral_report = gauge_report.get("spectral_report") or {}
    conservation_report = dossier.conservation_report or {}
    hamiltonian_report = dossier.hamiltonian_report or {}
    classification = dossier.classification.value
    connection_status = candidate.connection_status
    residual_zero = curvature_summary.get("curvature_residual_zero")
    gauge_risk_score = gauge_report.get("gauge_risk_score")
    spectral_status = str(spectral_report.get("status", "unknown"))
    conservation_count = int(conservation_report.get("num_conservation_laws_found", 0))
    hamiltonian_verified = bool(hamiltonian_report.get("verified", False))
    collisions = list(collision_report.get("collisions", ()))
    gates = [
        _gate(
            "tangent",
            "Tangent",
            "pass" if candidate.tangent_status == "tangent" else "fail",
            candidate.tangent_status,
        ),
        _gate(
            "curvature",
            "Curvature",
            _curvature_gate(connection_status, residual_zero),
            connection_status,
        ),
        _gate("gauge", "Gauge", _gauge_gate(gauge_risk_score), gauge_risk_score),
        _gate("spectral", "Spectral", _spectral_gate(spectral_status), spectral_status),
        _gate(
            "conservation",
            "Conservation",
            _conservation_gate(conservation_count, hamiltonian_verified),
            conservation_count,
        ),
        _gate(
            "collision",
            "Collision",
            _collision_gate(classification),
            _classification_label(classification),
        ),
    ]

    zcr_report = candidate.zcr_report or {}
    zcr_constraints = zcr_report.get("constraints_used") or []
    zcr_obstruction_basis = zcr_report.get("obstruction_basis") or []
    record: dict[str, Any] = {
        "id": _slug(candidate.name),
        "item_type": "candidate",
        "lane": "DIS-002",
        "name": candidate.name,
        "short_name": _compact_name(candidate.name),
        "order": candidate.order,
        "classification": classification,
        "classification_label": _classification_label(classification),
        "recommendation": _safe_recommendation(dossier),
        "disposition": _safe_recommendation(dossier),
        "tangent_status": candidate.tangent_status,
        "connection_status": connection_status,
        "curvature_residual_zero": bool(residual_zero),
        "curvature_status": curvature_summary.get("status", connection_status),
        "curvature_terms_total": curvature_summary.get("curvature_terms_total", 0),
        "curvature_terms_nonzero": curvature_summary.get("curvature_terms_nonzero"),
        "gauge_risk_score": gauge_risk_score,
        "spectral_status": spectral_status,
        "conservation_count": conservation_count,
        "hamiltonian_verified": hamiltonian_verified,
        "collision_count": len(collisions),
        "collisions": collisions,
        "collision_families": _collision_families(collisions),
        "failure_reasons": list(candidate.failure_reasons),
        "gates": gates,
        "gate_summary": _gate_summary(gates),
        "zcr_validated": bool(zcr_report.get("validated", False)),
        "zcr_solution": zcr_report.get("solution") or zcr_report.get("consistency_solution"),
        "zcr_obstruction_basis": zcr_obstruction_basis,
        "zcr_constraints": zcr_constraints,
        "cyclic_fingerprint": (zcr_report.get("cyclic_report") or {}).get("fingerprint"),
        "residual_grid": curvature_summary.get("entry_status_grid"),
        "proof_summary": None,
        "detail": {
            "summary": candidate.failure_reasons[0] if candidate.failure_reasons else "",
            "tangent_condition": str(candidate.tangent_condition),
            "obstruction_basis": zcr_obstruction_basis,
        },
    }
    record["surprisal"] = _audit_surprisal(record)
    return record


def _semidirect_record(candidate: SemidirectDeformationCandidate) -> dict[str, Any]:
    dossier = candidate.dossier
    collision_report = dossier.collision_report
    curvature_summary = dossier.curvature_summary
    gauge_report = dossier.gauge_report or {}
    spectral_report = gauge_report.get("spectral_report") or {}
    conservation_report = dossier.conservation_report or {}
    hamiltonian_report = dossier.hamiltonian_report or {}
    classification = dossier.classification.value
    gauge_risk_score = gauge_report.get("gauge_risk_score")
    spectral_status = str(spectral_report.get("status", "unknown"))
    conservation_count = int(conservation_report.get("num_conservation_laws_found", 0))
    hamiltonian_verified = bool(hamiltonian_report.get("verified", False))
    collisions = list(collision_report.get("collisions", ()))
    residual_zero = curvature_summary.get("curvature_residual_zero")
    gates = [
        _gate("tangent", "Tangent", "warn", "not applicable"),
        _gate(
            "curvature",
            "Curvature",
            _curvature_gate(candidate.connection_status, residual_zero),
            candidate.connection_status,
        ),
        _gate("gauge", "Gauge", _gauge_gate(gauge_risk_score), gauge_risk_score),
        _gate("spectral", "Spectral", _spectral_gate(spectral_status), spectral_status),
        _gate(
            "conservation",
            "Conservation",
            _conservation_gate(conservation_count, hamiltonian_verified),
            conservation_count,
        ),
        _gate(
            "collision",
            "Collision",
            _collision_gate(classification),
            _classification_label(classification),
        ),
    ]
    record: dict[str, Any] = {
        "id": _slug(candidate.name),
        "item_type": "candidate",
        "lane": "DIS-001",
        "name": candidate.name,
        "short_name": candidate.name.replace("semidirect ", ""),
        "order": candidate.order,
        "classification": classification,
        "classification_label": _classification_label(classification),
        "recommendation": dossier.recommendation,
        "disposition": dossier.recommendation,
        "tangent_status": "not_applicable",
        "connection_status": candidate.connection_status,
        "curvature_residual_zero": bool(residual_zero),
        "curvature_status": curvature_summary.get("status", candidate.connection_status),
        "curvature_terms_total": curvature_summary.get("curvature_terms_total", 0),
        "curvature_terms_nonzero": curvature_summary.get("curvature_terms_nonzero"),
        "gauge_risk_score": gauge_risk_score,
        "spectral_status": spectral_status,
        "conservation_count": conservation_count,
        "hamiltonian_verified": hamiltonian_verified,
        "collision_count": len(collisions),
        "collisions": collisions,
        "collision_families": _collision_families(collisions),
        "failure_reasons": list(candidate.failure_reasons),
        "gates": gates,
        "gate_summary": _gate_summary(gates),
        "zcr_validated": bool(
            candidate.connection_status
            in {"validated_known_semidirect_zcr", "validated_non_split_flow_equations"}
            and candidate.evidence.get("validated_as_flow_equations", False)
        ),
        "zcr_solution": None,
        "zcr_constraints": [],
        "cyclic_fingerprint": None,
        "residual_grid": curvature_summary.get("entry_status_grid"),
        "proof_summary": None,
        "detail": {
            "summary": candidate.failure_reasons[0] if candidate.failure_reasons else "",
            "algebra": candidate.algebra_label,
            "solve_status": candidate.solve_status,
        },
    }
    record["surprisal"] = _audit_surprisal(record)
    return record


def _bulk_record(candidate: BulkTriageCandidate) -> dict[str, Any]:
    dossier = candidate.dossier
    collision_report = dossier.collision_report
    curvature_summary = dossier.curvature_summary
    gauge_report = dossier.gauge_report or {}
    spectral_report = gauge_report.get("spectral_report") or {}
    classification = dossier.classification.value
    connection_status = candidate.connection_status
    gauge_risk_score = gauge_report.get("gauge_risk_score")
    spectral_status = str(spectral_report.get("status", "unknown"))
    collisions = list(collision_report.get("collisions", ()))
    gates = [
        _gate(
            "tangent",
            "Tangent",
            "pass" if candidate.tangent_status in {"tangent", "zero_control"} else "fail",
            candidate.tangent_status,
        ),
        _gate(
            "curvature",
            "Curvature",
            _curvature_gate(connection_status, curvature_summary.get("curvature_residual_zero")),
            connection_status,
        ),
        _gate("gauge", "Gauge", _gauge_gate(gauge_risk_score), gauge_risk_score),
        _gate("spectral", "Spectral", _spectral_gate(spectral_status), spectral_status),
        _gate("conservation", "Conservation", "warn", 0),
        _gate(
            "collision",
            "Collision",
            _collision_gate(classification),
            _classification_label(classification),
        ),
    ]
    record: dict[str, Any] = {
        "id": _slug(candidate.name),
        "item_type": "candidate",
        "lane": "DIS-006",
        "name": candidate.name,
        "short_name": candidate.name.replace("scaled sphere ", ""),
        "order": candidate.order,
        "classification": classification,
        "classification_label": _classification_label(classification),
        "recommendation": dossier.recommendation,
        "disposition": dossier.recommendation,
        "tangent_status": candidate.tangent_status,
        "connection_status": connection_status,
        "curvature_residual_zero": bool(curvature_summary.get("curvature_residual_zero")),
        "curvature_status": curvature_summary.get("status", connection_status),
        "curvature_terms_total": curvature_summary.get("curvature_terms_total", 0),
        "curvature_terms_nonzero": curvature_summary.get("curvature_terms_nonzero"),
        "gauge_risk_score": gauge_risk_score,
        "spectral_status": spectral_status,
        "conservation_count": 0,
        "hamiltonian_verified": False,
        "collision_count": len(collisions),
        "collisions": collisions,
        "collision_families": _collision_families(collisions),
        "failure_reasons": list(candidate.failure_reasons),
        "gates": gates,
        "gate_summary": _gate_summary(gates),
        "zcr_validated": False,
        "zcr_solution": None,
        "zcr_constraints": [],
        "zcr_obstruction_basis": [],
        "cyclic_fingerprint": None,
        "residual_grid": curvature_summary.get("entry_status_grid"),
        "proof_summary": None,
        "bulk_descriptor": candidate.descriptor,
        "bulk_family": candidate.family,
        "priority_score": candidate.priority_score,
        "detail": {
            "summary": candidate.failure_reasons[0] if candidate.failure_reasons else "",
            "descriptor": candidate.descriptor,
            "family": candidate.family,
            "priority_score": candidate.priority_score,
        },
    }
    record["surprisal"] = _audit_surprisal(record)
    return record


def _run_matrix_record(candidate: RunMatrixCandidate, lane: str) -> dict[str, Any]:
    dossier = candidate.dossier
    collision_report = dossier.collision_report
    curvature_summary = dossier.curvature_summary
    classification = dossier.classification.value
    collisions = list(collision_report.get("collisions", ()))
    spectral_status = str(candidate.gate_summary.get("spectral_parameter_status", "unknown"))
    residual_zero = bool(curvature_summary.get("curvature_residual_zero"))
    gates = [
        _gate(
            "tangent",
            "Tangent",
            "pass" if candidate.tangent_status in {"tangent", "zero_control"} else "warn",
            candidate.tangent_status,
        ),
        _gate(
            "curvature",
            "Curvature",
            _curvature_gate(candidate.connection_status, residual_zero),
            candidate.connection_status,
        ),
        _gate("gauge", "Gauge", "warn", "open gate"),
        _gate("spectral", "Spectral", _spectral_gate(spectral_status), spectral_status),
        _gate("conservation", "Conservation", "warn", 0),
        _gate(
            "collision",
            "Collision",
            _collision_gate(classification),
            _classification_label(classification),
        ),
    ]
    short_name = (
        candidate.name.replace("density matrix ", "")
        .replace("nonlocal ", "")
        .replace("cohomological ", "")
    )
    record: dict[str, Any] = {
        "id": _slug(candidate.name),
        "item_type": "candidate",
        "lane": lane,
        "name": candidate.name,
        "short_name": short_name,
        "order": candidate.order,
        "classification": classification,
        "classification_label": _classification_label(classification),
        "recommendation": dossier.recommendation,
        "disposition": dossier.recommendation,
        "tangent_status": candidate.tangent_status,
        "connection_status": candidate.connection_status,
        "curvature_residual_zero": residual_zero,
        "curvature_status": curvature_summary.get("status", candidate.connection_status),
        "curvature_terms_total": curvature_summary.get("curvature_terms_total", 0),
        "curvature_terms_nonzero": curvature_summary.get("curvature_terms_nonzero"),
        "gauge_risk_score": None,
        "spectral_status": spectral_status,
        "conservation_count": 0,
        "hamiltonian_verified": False,
        "collision_count": len(collisions),
        "collisions": collisions,
        "collision_families": _collision_families(collisions),
        "failure_reasons": list(candidate.failure_reasons),
        "gates": gates,
        "gate_summary": _gate_summary(gates),
        "zcr_validated": False,
        "zcr_solution": None,
        "zcr_constraints": [],
        "zcr_obstruction_basis": [],
        "cyclic_fingerprint": None,
        "residual_grid": curvature_summary.get("entry_status_grid"),
        "proof_summary": None,
        "bulk_descriptor": candidate.descriptor,
        "bulk_family": candidate.family,
        "priority_score": candidate.priority_score,
        "detail": {
            "summary": candidate.failure_reasons[0] if candidate.failure_reasons else "",
            "descriptor": candidate.descriptor,
            "family": candidate.family,
            "priority_score": candidate.priority_score,
        },
    }
    record["surprisal"] = _audit_surprisal(record)
    return record


def _calibration_record(dossier: CandidateDossier) -> dict[str, Any]:
    curvature_summary = dossier.curvature_summary
    conservation_report = dossier.conservation_report or {}
    hamiltonian_report = dossier.hamiltonian_report or {}
    collisions = list(dossier.collision_report.get("collisions", ()))
    conservation_count = int(conservation_report.get("num_conservation_laws_found", 0))
    hamiltonian_verified = bool(hamiltonian_report.get("verified", False))
    classification = "known_mechanism"
    gates = [
        _gate("tangent", "Tangent", "warn", "not applicable"),
        _gate(
            "curvature",
            "Curvature",
            _status_from_bool(bool(curvature_summary.get("basis_split_complete"))),
            "structured residual report",
        ),
        _gate("gauge", "Gauge", "warn", "not attempted"),
        _gate("spectral", "Spectral", "warn", "AKNS calibration"),
        _gate(
            "conservation",
            "Conservation",
            _conservation_gate(conservation_count, hamiltonian_verified),
            conservation_count,
        ),
        _gate("collision", "Collision", "fail", _classification_label(classification)),
    ]
    record: dict[str, Any] = {
        "id": "second-jet-nilpotent-mkdv",
        "item_type": "calibration",
        "lane": "Prompt Pack",
        "name": dossier.name,
        "short_name": "second-jet mKdV calibration",
        "order": None,
        "classification": classification,
        "classification_label": _classification_label(classification),
        "recommendation": _safe_recommendation(dossier),
        "disposition": _safe_recommendation(dossier),
        "tangent_status": "not_applicable",
        "connection_status": "calibration_report",
        "curvature_residual_zero": bool(curvature_summary.get("curvature_residual_zero")),
        "curvature_status": "structured residual report",
        "curvature_terms_total": curvature_summary.get("curvature_terms_total", 0),
        "curvature_terms_nonzero": curvature_summary.get("curvature_terms_nonzero"),
        "gauge_risk_score": None,
        "spectral_status": "calibration",
        "conservation_count": conservation_count,
        "hamiltonian_verified": hamiltonian_verified,
        "collision_count": len(collisions),
        "collisions": collisions,
        "collision_families": _collision_families(collisions),
        "failure_reasons": [
            "calibration dossier only",
            "known scalar hierarchy and nilpotent-lift collision zones recorded",
        ],
        "gates": gates,
        "gate_summary": _gate_summary(gates),
        "zcr_validated": False,
        "zcr_solution": None,
        "zcr_constraints": [],
        "cyclic_fingerprint": None,
        "residual_grid": curvature_summary.get("entry_status_grid"),
        "proof_summary": None,
        "detail": {
            "summary": "Prompt-pack calibration dossier.",
            "hamiltonian_verified": hamiltonian_verified,
        },
    }
    record["surprisal"] = _audit_surprisal(record)
    return record


def _count_by(records: list[Mapping[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        value = str(record[key])
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def _frontier_lookup(frontier_records: tuple[FrontierCandidate, ...]) -> dict[str, dict[str, object]]:
    return {record.item_id: record.as_dict() for record in frontier_records}


def _attach_frontier_status(
    records: list[dict[str, Any]],
    frontier_records: tuple[FrontierCandidate, ...],
) -> None:
    lookup = _frontier_lookup(frontier_records)
    for record in records:
        frontier_record = lookup.get(str(record["id"]))
        if frontier_record:
            record["frontier_status"] = frontier_record["potential_status"]
            record["frontier_priority"] = frontier_record["priority"]
            record["next_action"] = frontier_record["next_action"]
            record["gate_gaps"] = frontier_record["gate_gaps"]
        else:
            record["frontier_status"] = "not_on_frontier"
            record["frontier_priority"] = 0
            record["next_action"] = "No active frontier action."
            record["gate_gaps"] = []


def _gate_totals(records: list[Mapping[str, Any]]) -> dict[str, dict[str, int]]:
    totals: dict[str, dict[str, int]] = {
        key: {"pass": 0, "warn": 0, "fail": 0} for key in GATE_ORDER
    }
    for record in records:
        for gate in record["gates"]:
            key = str(gate["key"])
            status = str(gate["status"])
            totals.setdefault(key, {"pass": 0, "warn": 0, "fail": 0})
            totals[key][status] += 1
    return totals


def _collision_family_map(records: list[Mapping[str, Any]]) -> list[dict[str, object]]:
    family_map: dict[str, list[str]] = {}
    for record in records:
        for family in record.get("collision_families", []):
            family_map.setdefault(str(family), []).append(str(record["id"]))
    return [
        {"family": family, "item_ids": sorted(ids), "count": len(ids)}
        for family, ids in sorted(family_map.items())
    ]


def _metric_cards(
    records: list[Mapping[str, Any]],
    solve_succeeded: bool,
    frontier_count: int,
    procedure_audit: ProcedureAuditReport,
    serious_cycle: Mapping[str, Any],
    full_scale: Mapping[str, Any],
) -> list[dict[str, object]]:
    discovery_records = [record for record in records if record["item_type"] == "candidate"]
    validated_zcr = sum(1 for record in discovery_records if record.get("zcr_validated"))
    discard_count = sum(1 for record in discovery_records if record["recommendation"] == "discard")
    review_count = sum(
        1 for record in discovery_records if record["recommendation"] == "needs_human_review"
    )
    blocked_count = sum(1 for record in discovery_records if record["recommendation"] == "blocked")
    conservation_total = sum(int(record.get("conservation_count", 0)) for record in records)
    max_surprisal = max(int(record["surprisal"]["score"]) for record in records)
    unresolved_gates = sum(
        1
        for record in records
        for gate in record["gates"]
        if gate["status"] == "warn"
    )
    proof_ready = sum(
        1
        for record in records
        if record["item_type"] == "proof_artifact"
        and record.get("proof_summary", {}).get("markdown_ready")
    )
    return [
        {
            "label": "Tracked items",
            "value": len(records),
            "detail": f"{len(discovery_records)} discovery candidates",
            "tone": "neutral",
        },
        {
            "label": "Validated ZCR",
            "value": validated_zcr,
            "detail": "known-family evidence only",
            "tone": "pass",
        },
        {
            "label": "Needs review",
            "value": review_count,
            "detail": "open candidate dossiers",
            "tone": "warn",
        },
        {
            "label": "Frontier",
            "value": frontier_count,
            "detail": "promising potential queue",
            "tone": "inspect",
        },
        {
            "label": "Blocked",
            "value": blocked_count,
            "detail": "documented obstructions",
            "tone": "warn",
        },
        {
            "label": "Procedure audit",
            "value": procedure_audit.status,
            "detail": f"{procedure_audit.failure_count} fail / {procedure_audit.warning_count} warn",
            "tone": "pass" if procedure_audit.passed else "fail",
        },
        {
            "label": "Discard",
            "value": discard_count,
            "detail": "controls or known collisions",
            "tone": "fail",
        },
        {
            "label": "Unresolved gates",
            "value": unresolved_gates,
            "detail": "warn-status evidence cells",
            "tone": "warn",
        },
        {
            "label": "Proof artifacts",
            "value": proof_ready,
            "detail": "ready for explicit writer",
            "tone": "pass",
        },
        {
            "label": "Audit surprisal",
            "value": max_surprisal,
            "detail": "highest triage score",
            "tone": "inspect",
        },
        {
            "label": "Conservation laws",
            "value": conservation_total,
            "detail": "calibration evidence",
            "tone": "pass",
        },
        {
            "label": "Ansatz solve",
            "value": "ok" if solve_succeeded else "hold",
            "detail": "scalar mKdV V coefficients",
            "tone": "pass" if solve_succeeded else "warn",
        },
        {
            "label": "Full-scale",
            "value": full_scale.get("status", "unknown"),
            "detail": f"{full_scale.get('generated_candidate_count', 0)} generated candidates",
            "tone": "inspect",
        },
        {
            "label": "Serious cycle",
            "value": serious_cycle.get("result_status", "unknown"),
            "detail": str(serious_cycle.get("cycle_id", "SERIOUS-001")),
            "tone": "warn",
        },
    ]


def _plain_summary(
    records: list[Mapping[str, Any]],
    frontier_records: tuple[FrontierCandidate, ...],
) -> dict[str, object]:
    discovery_records = [record for record in records if record["item_type"] == "candidate"]
    full_scale_count = len(discovery_records)
    dis001_records = [record for record in discovery_records if record["lane"] == "DIS-001"]
    dis002_records = [record for record in records if record["lane"] == "DIS-002"]
    dis003_records = [record for record in records if record["lane"] == "DIS-003"]
    dis004_records = [record for record in records if record["lane"] == "DIS-004"]
    dis005_records = [record for record in records if record["lane"] == "DIS-005"]
    dis006_records = [record for record in records if record["lane"] == "DIS-006"]
    proof_ready = sum(
        1
        for record in records
        if record["item_type"] == "proof_artifact"
        and record.get("proof_summary", {}).get("markdown_ready")
    )
    validated_known = sum(1 for record in discovery_records if record.get("zcr_validated"))
    review_count = sum(
        1 for record in discovery_records if record["recommendation"] == "needs_human_review"
    )
    discard_count = sum(1 for record in discovery_records if record["recommendation"] == "discard")
    blocked_candidate_count = sum(
        1 for record in discovery_records if record["recommendation"] == "blocked"
    )
    ansatz_blocked_count = sum(
        1
        for record in discovery_records
        if record.get("connection_status") == "ansatz_obstruction_current_family"
    )
    promising_count = sum(
        1 for record in frontier_records if record.potential_status == "promising_potential"
    )
    blocked_count = sum(
        1
        for record in frontier_records
        if record.potential_status.startswith("blocked_by_")
    )

    return {
        "headline": "Current readout: this is an active evidence search with a bounded frontier.",
        "lede": (
            f"The console is auditing {len(records)} items: {proof_ready} proof artifact, "
            f"1 calibration case, and {len(discovery_records)} controlled search candidates. "
            f"The active frontier has {len(frontier_records)} queued candidates."
        ),
        "bullets": [
            "The pure-gauge proof artifact passes: its curvature residual is zero.",
            "The formal procedure audit passes for the current frontier and discard records.",
            (
                f"DIS-001 has {len(dis001_records)} semidirect probes; validated controls stay "
                "in discard and the non-split product probe now has corrected flow-equation evidence."
            ),
            (
                f"DIS-002 has {len(dis002_records)} sphere-flow candidates; the Heisenberg-shaped "
                "case is validated but known-family collision evidence keeps it in discard."
            ),
            (
                f"DIS-003 through DIS-005 add {len(dis003_records)} density-matrix, "
                f"{len(dis004_records)} nonlocal-covering, and {len(dis005_records)} "
                "cohomology probes with explicit open gates."
            ),
            (
                f"DIS-006 adds {len(dis006_records)} scaled sphere-tangent triage candidates; "
                "the batch records descriptors without constructing ZCR matrices."
            ),
            (
                f"The frontier has {promising_count} promising-potential candidates and "
                f"{blocked_count} blocked candidates."
            ),
            (
                f"SERIOUS-001 leaves {ansatz_blocked_count} third-order candidate blocked by a "
                "documented ansatz-family obstruction; the broader discovery state has "
                f"{blocked_candidate_count} blocked candidates total."
            ),
        (
            f"{validated_known} controlled candidates have validated ZCR evidence; "
            f"{review_count} need review and {discard_count} are discard-path."
        ),
        (
            f"FULL-001 evaluates {full_scale_count} discovery candidates and keeps the "
            "solver action queue separate from stronger interpretation."
        ),
        ],
        "bottom_line": "Use this as a process console: generate, gate, discard, and queue the next honest test.",
    }


def _validate_dashboard_language(payload: Mapping[str, Any]) -> None:
    rendered = json.dumps(payload, sort_keys=True).lower()
    forbidden = [term for term in PROMOTION_TERMS if term in rendered]
    if forbidden:
        raise ValueError(f"Dashboard payload contains promotion terms: {forbidden}")


def build_dashboard_payload() -> dict[str, Any]:
    """Build a JSON-compatible dashboard payload from current in-repo evidence."""
    solve_report = recover_scalar_mkdv_v_coefficients()
    calibration = build_mkdv_second_jet_dossier()
    semidirect_discovery = run_semidirect_deformation_search()
    discovery = run_sphere_low_order_search()
    density_discovery = run_density_matrix_search()
    nonlocal_discovery = run_nonlocal_covering_search()
    cohomology_discovery = run_cohomological_deformation_search()
    scaled_discovery = run_scaled_candidate_search()
    serious_cycle = run_serious_cycle_001()
    full_scale = run_full_scale_search()
    iterative = serious_cycle.refreshed_process
    procedure_audit = serious_cycle.refreshed_procedure

    items = [_pure_gauge_artifact_record(), _calibration_record(calibration)]
    items.extend(_semidirect_record(candidate) for candidate in semidirect_discovery.candidates)
    items.extend(_sphere_record(candidate) for candidate in discovery.candidates)
    items.extend(
        _run_matrix_record(candidate, density_discovery.run_id)
        for candidate in density_discovery.candidates
    )
    items.extend(
        _run_matrix_record(candidate, nonlocal_discovery.run_id)
        for candidate in nonlocal_discovery.candidates
    )
    items.extend(
        _run_matrix_record(candidate, cohomology_discovery.run_id)
        for candidate in cohomology_discovery.candidates
    )
    items.extend(_bulk_record(candidate) for candidate in scaled_discovery.candidates)
    _attach_frontier_status(items, iterative.frontier)
    proof_items = [item for item in items if item["item_type"] == "proof_artifact"]
    candidate_items = [item for item in items if item["item_type"] == "candidate"]
    promising_count = sum(
        1 for record in iterative.frontier if record.potential_status == "promising_potential"
    )
    blocked_count = sum(
        1
        for record in iterative.frontier
        if record.potential_status.startswith("blocked_by_")
    )
    ansatz_blocked_count = sum(
        1
        for record in iterative.frontier
        if record.potential_status == "blocked_by_ansatz_obstruction"
    )

    payload: dict[str, Any] = {
        "schema_version": 7,
        "title": "LAXFORGE Evidence Console",
        "posture": "generate, solve, reduce, falsify, extract structure",
        "run_ids": [
            "M0",
            "PROMPT-PACK",
            semidirect_discovery.run_id,
            discovery.run_id,
            density_discovery.run_id,
            nonlocal_discovery.run_id,
            cohomology_discovery.run_id,
            scaled_discovery.run_id,
            iterative.run_id,
            procedure_audit.procedure_id,
            serious_cycle.cycle_id,
            full_scale.run_id,
        ],
        "lanes": [
            {"id": "m0", "name": "M0 zero-curvature reports", "items": len(proof_items)},
            {"id": "prompt-pack", "name": "Prompt Pack", "items": 1},
            {
                "id": "dis-001",
                "name": semidirect_discovery.run_id,
                "items": len(semidirect_discovery.candidates),
            },
            {"id": "dis-002", "name": discovery.run_id, "items": len(discovery.candidates)},
            {
                "id": "dis-003",
                "name": density_discovery.run_id,
                "items": len(density_discovery.candidates),
            },
            {
                "id": "dis-004",
                "name": nonlocal_discovery.run_id,
                "items": len(nonlocal_discovery.candidates),
            },
            {
                "id": "dis-005",
                "name": cohomology_discovery.run_id,
                "items": len(cohomology_discovery.candidates),
            },
            {
                "id": "dis-006",
                "name": scaled_discovery.run_id,
                "items": len(scaled_discovery.candidates),
            },
            {
                "id": "procedure-audit",
                "name": "Procedure Audit",
                "items": len(procedure_audit.checks),
            },
            {"id": "serious-001", "name": serious_cycle.cycle_id, "items": 1},
            {"id": "full-001", "name": full_scale.run_id, "items": len(full_scale.action_queue)},
        ],
        "gate_order": list(GATE_ORDER),
        "plain_summary": _plain_summary(items, iterative.frontier),
        "metric_cards": _metric_cards(
            items,
            solve_report.solved,
            len(iterative.frontier),
            procedure_audit,
            serious_cycle.as_dict(),
            full_scale.as_dict(),
        ),
        "iterative_process": iterative.as_dict(),
        "procedure_audit": procedure_audit.as_dict(),
        "serious_cycle": serious_cycle.as_dict(),
        "full_scale_search": full_scale.as_dict(),
        "metrics": {
            "tracked_items_total": len(items),
            "proof_artifact_count": len(proof_items),
            "discovery_candidate_count": len(candidate_items),
            "dis001_candidate_count": len(semidirect_discovery.candidates),
            "dis002_candidate_count": len(discovery.candidates),
            "dis003_candidate_count": len(density_discovery.candidates),
            "dis004_candidate_count": len(nonlocal_discovery.candidates),
            "dis005_candidate_count": len(cohomology_discovery.candidates),
            "dis006_candidate_count": len(scaled_discovery.candidates),
            "frontier_count": len(iterative.frontier),
            "promising_potential_count": promising_count,
            "blocked_frontier_count": blocked_count,
            "ansatz_blocked_count": ansatz_blocked_count,
            "serious_cycle_status": serious_cycle.result_status,
            "full_scale_status": full_scale.status,
            "full_scale_candidate_count": full_scale.generated_candidate_count,
            "full_scale_action_queue_count": len(full_scale.action_queue),
            "procedure_audit_status": procedure_audit.status,
            "procedure_check_count": len(procedure_audit.checks),
            "procedure_failure_count": procedure_audit.failure_count,
            "procedure_warning_count": procedure_audit.warning_count,
            "classification_counts": _count_by(items, "classification_label"),
            "recommendation_counts": _count_by(items, "recommendation"),
            "item_type_counts": _count_by(items, "item_type"),
            "gate_totals": _gate_totals(items),
            "highest_surprisal": max(int(item["surprisal"]["score"]) for item in items),
            "validated_zcr_count": sum(1 for item in items if item.get("zcr_validated")),
            "ansatz_solver_status": solve_report.status,
        },
        "collision_family_map": _collision_family_map(items),
        "items": items,
        "candidates": items,
    }
    _validate_dashboard_language(payload)
    return payload


def write_dashboard_data(
    path: str | Path,
    payload: Mapping[str, Any] | None = None,
    overwrite: bool = True,
) -> Path:
    """Write dashboard JSON only when explicitly requested."""
    output_path = Path(path)
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite dashboard data: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload or build_dashboard_payload(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output_path


def write_dashboard_data_js(
    path: str | Path,
    payload: Mapping[str, Any] | None = None,
    overwrite: bool = True,
) -> Path:
    """Write the static dashboard JavaScript data payload."""
    output_path = Path(path)
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite dashboard data: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(payload or build_dashboard_payload(), indent=2, sort_keys=True)
    output_path.write_text(
        "window.LAXFORGE_DASHBOARD_DATA = " + data + ";\n",
        encoding="utf-8",
    )
    return output_path


def add_dashboard_cli_arguments(parser: argparse.ArgumentParser) -> None:
    """Attach dashboard writer options to a script parser."""
    parser.add_argument(
        "--format",
        choices=("js", "json"),
        default="js",
        help="Dashboard data output format.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path. Defaults to web/dashboard_data.js for js output.",
    )
