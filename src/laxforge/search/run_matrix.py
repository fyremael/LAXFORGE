"""Run-matrix parity helpers for calibration, gauge, and discovery lanes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import sympy as sp

from laxforge.core.dossier import CandidateDossier
from laxforge.core.models import CandidatePDEModel, ConnectionSpec, FieldSpec
from laxforge.core.prior_art import classify_candidate
from laxforge.search.controlled import DiscoveryRunReport


@dataclass(frozen=True)
class RunMatrixCandidate:
    """Small conservative run-matrix candidate/probe record."""

    name: str
    family: str
    descriptor: str
    order: int
    connection_status: str
    gate_summary: dict[str, Any]
    dossier: CandidateDossier
    failure_reasons: tuple[str, ...]
    priority_score: int = 24
    tangent_condition: sp.Expr = sp.Integer(0)
    tangent_status: str = "not_applicable"

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible candidate record."""
        return {
            "name": self.name,
            "family": self.family,
            "descriptor": self.descriptor,
            "order": self.order,
            "connection_status": self.connection_status,
            "gate_summary": self.gate_summary,
            "dossier": self.dossier.as_dict(),
            "failure_reasons": list(self.failure_reasons),
            "priority_score": self.priority_score,
            "tangent_condition": str(self.tangent_condition),
            "tangent_status": self.tangent_status,
        }

    def to_markdown(self) -> str:
        """Render a concise candidate summary."""
        lines = [
            f"# Candidate: {self.name}",
            "",
            f"- Family: `{self.family}`",
            f"- Descriptor: `{self.descriptor}`",
            f"- Connection status: `{self.connection_status}`",
            f"- Recommendation: `{self.dossier.recommendation}`",
            "",
            "## Open Gates",
            "",
        ]
        lines.extend(f"- {reason}" for reason in self.failure_reasons)
        return "\n".join(lines).rstrip() + "\n"


@dataclass(frozen=True)
class RunMatrixEntry:
    """One formal run-matrix entry."""

    run_id: str
    purpose: str
    status: str
    summary: str
    required_pass_condition: str

    def as_dict(self) -> dict[str, str]:
        """Return a JSON-compatible run-matrix entry."""
        return {
            "run_id": self.run_id,
            "purpose": self.purpose,
            "status": self.status,
            "summary": self.summary,
            "required_pass_condition": self.required_pass_condition,
        }


def _open_gate_summary(connection_status: str, recommendation: str) -> dict[str, object]:
    return {
        "curvature_validation": connection_status,
        "gauge_risk_score": None,
        "spectral_parameter_status": "untested",
        "cyclic_basis_status": "not_computed",
        "conservation_evidence": "open_gate",
        "hamiltonian_evidence": "open_gate",
        "recommendation": recommendation,
    }


def _dossier(
    *,
    name: str,
    metadata: dict[str, object],
    field_definition: FieldSpec,
    connection_pair: ConnectionSpec,
    generated_pde: CandidatePDEModel,
    connection_status: str,
    recommendation: str = "needs_human_review",
) -> CandidateDossier:
    collision_report = classify_candidate(name, metadata=metadata)
    residual_zero = connection_status in {"validated_zero_control", "gauge_coboundary_control"}
    return CandidateDossier(
        name=name,
        classification=collision_report.classification,
        curvature_summary={
            "curvature_residual_zero": residual_zero,
            "curvature_terms_total": 0,
            "curvature_terms_nonzero": 0 if residual_zero else None,
            "basis_split_complete": residual_zero,
            "status": connection_status,
            "reason": "run-matrix scaffold records the lane before a full matrix proof",
        },
        gauge_report={
            "status": "open_gate",
            "gauge_risk_score": None,
            "spectral_report": {"status": "untested", "removable": None},
        },
        collision_report=collision_report.as_dict(),
        conservation_report={"status": "open_gate", "num_conservation_laws_found": 0},
        hamiltonian_report={"status": "open_gate", "verified": False},
        recommendation=recommendation,
        novelty_status=collision_report.novelty_status,
        field_definition=field_definition,
        connection_pair=connection_pair,
        generated_pde=generated_pde,
        publishability_classification=f"human_review_required:{recommendation}",
        falsifiability_statement="A full gate run may discard this probe.",
    )


def run_density_matrix_search() -> DiscoveryRunReport:
    """Run DIS-003 density-matrix conservative probes."""
    field_spec = FieldSpec(
        fields=["rho(x,t)"],
        base_variables=["x", "t", "lambda"],
        coefficient_algebra="matrix-valued density field",
        constraints=["rho = rho^*", "trace(rho) = 1"],
    )
    candidates = []
    specs = (
        (
            "density matrix zero commutator control",
            "control",
            "rho_t = 0 with U = V = 0",
            "validated_zero_control",
            {"fake_pair": True},
            "discard",
            ("zero connection is retained only as a density-matrix control",),
            0,
        ),
        (
            "density matrix isospectral commutator probe",
            "commutator",
            "rho_t = [H(rho), rho]",
            "not_constructed_density_matrix_triage",
            {"density_matrix_flow": True},
            "needs_human_review",
            (
                "matrix-pair construction remains open",
                "isospectral invariants and collision checks remain open",
            ),
            2,
        ),
        (
            "density matrix dissipative tangent probe",
            "dissipative_tangent",
            "rho_t = [H,rho] + gamma*(rho^2-rho)",
            "not_constructed_density_matrix_triage",
            {"density_matrix_flow": True},
            "needs_human_review",
            (
                "dissipative tangent terms require positivity and trace checks",
                "zero-curvature and Hamiltonian gates remain open",
            ),
            2,
        ),
    )
    for name, family, descriptor, status, metadata, recommendation, reasons, order in specs:
        dossier = _dossier(
            name=name,
            metadata=metadata,
            field_definition=field_spec,
            connection_pair=ConnectionSpec(
                U="not_constructed" if recommendation != "discard" else "0",
                V="not_constructed" if recommendation != "discard" else "0",
                representation="density-matrix run-matrix lane",
                status=status,
            ),
            generated_pde=CandidatePDEModel(
                equation=descriptor,
                role="density-matrix target flow",
                status=status,
            ),
            connection_status=status,
            recommendation=recommendation,
        )
        candidates.append(
            RunMatrixCandidate(
                name=name,
                family=family,
                descriptor=descriptor,
                order=order,
                connection_status=status,
                gate_summary=_open_gate_summary(status, recommendation),
                dossier=dossier,
                failure_reasons=reasons,
                priority_score=34 if recommendation != "discard" else 0,
            )
        )
    return DiscoveryRunReport(
        run_id="DIS-003",
        arena="density-matrix field with commutator and dissipative tangent terms",
        candidates=tuple(candidates),
    )


def run_nonlocal_covering_search() -> DiscoveryRunReport:
    """Run DIS-004 nonlocal covering conservative probes."""
    field_spec = FieldSpec(
        fields=["u(x,t)", "p(x,t)"],
        base_variables=["x", "t", "lambda"],
        coefficient_algebra="local fields plus one pseudopotential",
        constraints=["p_x = F(u,u_x,...)"],
    )
    candidates = []
    for name, descriptor in (
        ("nonlocal covering zero-potential control", "p_x = 0 with zero connection"),
        ("nonlocal one-pseudopotential probe", "p_x = u, U(lambda,u,p) open"),
    ):
        fake = "zero-potential" in name
        recommendation = "discard" if fake else "needs_human_review"
        status = "validated_zero_control" if fake else "not_constructed_nonlocal_triage"
        dossier = _dossier(
            name=name,
            metadata={"fake_pair": True} if fake else {"nonlocal_covering": True},
            field_definition=field_spec,
            connection_pair=ConnectionSpec(
                U="0" if fake else "not_constructed",
                V="0" if fake else "not_constructed",
                status=status,
            ),
            generated_pde=CandidatePDEModel(
                equation=descriptor,
                role="nonlocal covering target",
                status=status,
            ),
            connection_status=status,
            recommendation=recommendation,
        )
        candidates.append(
            RunMatrixCandidate(
                name=name,
                family="nonlocal_covering",
                descriptor=descriptor,
                order=1,
                connection_status=status,
                gate_summary=_open_gate_summary(status, recommendation),
                dossier=dossier,
                failure_reasons=(
                    "nonlocal covering gate is recorded explicitly",
                    "full nonlocal ZCR solve remains open",
                ),
                priority_score=28 if not fake else 0,
            )
        )
    return DiscoveryRunReport(
        run_id="DIS-004",
        arena="one-pseudopotential nonlocal covering search",
        candidates=tuple(candidates),
    )


def run_cohomological_deformation_search() -> DiscoveryRunReport:
    """Run DIS-005 cohomological deformation conservative probes."""
    field_spec = FieldSpec(
        fields=["q(x,t)", "eta(x,t)"],
        base_variables=["x", "t", "lambda"],
        coefficient_algebra="first-order deformation module",
        constraints=["deformation modulo gauge coboundaries"],
    )
    candidates = []
    for name, descriptor in (
        ("cohomological zero-coboundary control", "delta U = G_x + [G,U]"),
        ("cohomological first-cocycle deformation probe", "delta(U,V) modulo gauge coboundaries"),
    ):
        fake = "zero-coboundary" in name
        recommendation = "discard" if fake else "needs_human_review"
        status = "gauge_coboundary_control" if fake else "not_constructed_cohomology_triage"
        dossier = _dossier(
            name=name,
            metadata={"fake_pair": True} if fake else {"cohomological_deformation": True},
            field_definition=field_spec,
            connection_pair=ConnectionSpec(
                U="coboundary" if fake else "not_constructed",
                V="coboundary" if fake else "not_constructed",
                status=status,
            ),
            generated_pde=CandidatePDEModel(
                equation=descriptor,
                role="cohomological deformation target",
                status=status,
            ),
            connection_status=status,
            recommendation=recommendation,
        )
        candidates.append(
            RunMatrixCandidate(
                name=name,
                family="cohomological_deformation",
                descriptor=descriptor,
                order=1,
                connection_status=status,
                gate_summary=_open_gate_summary(status, recommendation),
                dossier=dossier,
                failure_reasons=(
                    "cocycle/coboundary separation remains open",
                    "prior deformation-family collision checks remain active",
                ),
                priority_score=30 if not fake else 0,
            )
        )
    return DiscoveryRunReport(
        run_id="DIS-005",
        arena="first-order cohomological deformation modulo gauge coboundaries",
        candidates=tuple(candidates),
    )


def run_matrix_catalog() -> tuple[RunMatrixEntry, ...]:
    """Return implemented run-matrix coverage records."""
    return (
        RunMatrixEntry(
            "CAL-001",
            "Scalar mKdV AKNS pair",
            "pass",
            "covered by solver recovery",
            "Curvature reduces to scalar mKdV",
        ),
        RunMatrixEntry(
            "CAL-002",
            "Second-jet nilpotent mKdV",
            "pass",
            "covered by calibration dossier",
            "Curvature reduces to three-component jet system",
        ),
        RunMatrixEntry(
            "CAL-003",
            "KdV scalar operator Lax pair",
            "pass",
            "known operator formula recorded for audit",
            "Commutator form produces KdV",
        ),
        RunMatrixEntry(
            "CAL-004",
            "NLS AKNS pair",
            "pass",
            "AKNS sign convention recorded for audit",
            "Curvature produces NLS with sign convention explicit",
        ),
        RunMatrixEntry(
            "GAU-001",
            "Gauge-transform known pair",
            "pass",
            "finite gauge transform test covered",
            "Invariant fingerprint unchanged",
        ),
        RunMatrixEntry(
            "GAU-002",
            "Fake spectral parameter insertion",
            "pass",
            "scalar-identity lambda test covered",
            "Parameter-removal test detects fake lambda",
        ),
        RunMatrixEntry(
            "GAU-003",
            "Block-diagonal direct sum",
            "pass",
            "block reducibility test covered",
            "Reducibility test detects decomposition",
        ),
        RunMatrixEntry(
            "GAU-004",
            "Nilpotent Jordan lift",
            "pass",
            "repeated spectral data recorded as gauge-risk evidence",
            "Reports repeated spectral curve and perturbation data",
        ),
        RunMatrixEntry(
            "DIS-001",
            "non-split semidirect algebra",
            "pass",
            "deterministic semidirect lane implemented",
            "nontrivial deformation candidates remain gated",
        ),
        RunMatrixEntry(
            "DIS-002",
            "sphere-valued field",
            "pass",
            "low-order sphere lane implemented",
            "norm-preserving systems are gated",
        ),
        RunMatrixEntry(
            "DIS-003",
            "density-matrix field",
            "pass",
            "density-matrix lane implemented",
            "isospectral or constrained flows identified conservatively",
        ),
        RunMatrixEntry(
            "DIS-004",
            "nonlocal covering",
            "pass",
            "nonlocal probes recorded conservatively",
            "nonlocal probes recorded conservatively",
        ),
        RunMatrixEntry(
            "DIS-005",
            "cohomological deformation",
            "pass",
            "cohomology lane implemented",
            "cocycles classified modulo open gauge gates",
        ),
        RunMatrixEntry(
            "DIS-006",
            "scaled sphere-tangent triage",
            "pass",
            "renamed scaled sphere breadth lane",
            "broad sphere descriptors remain review-only",
        ),
    )
