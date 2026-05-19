"""Candidate dossier scaffolding."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import sympy as sp

from laxforge.core.conservation import inherited_mkdv_conservation_report
from laxforge.core.hamiltonian import mkdv_second_jet_hamiltonian_report
from laxforge.core.models import (
    CandidateDossierModel,
    CandidatePDEModel,
    ConnectionSpec,
    FieldSpec,
    GateEvidence,
    open_gate,
)
from laxforge.core.prior_art import CandidateClassification, classify_candidate
from laxforge.examples.mkdv_second_jet import validate


def _as_dict_or_empty(value: Mapping[str, Any] | None) -> dict[str, Any]:
    return dict(value) if value else {}


def _default_spectral_report(gauge_report: Mapping[str, Any] | None) -> dict[str, Any]:
    spectral = _as_dict_or_empty(gauge_report).get("spectral_report")
    if isinstance(spectral, Mapping):
        return dict(spectral)
    return {
        "status": "untested",
        "lambda_present": None,
        "removable": None,
        "reason": "no spectral-parameter test has been run for this candidate",
    }


def _default_cyclic_report() -> dict[str, Any]:
    return {
        "status": "open_gate",
        "basis_dimension": None,
        "closure_relation": "not_computed",
        "fingerprint": None,
        "reason": "cyclic-basis fingerprint requires an explicit matrix pair",
    }


def _default_field_definition() -> FieldSpec:
    return FieldSpec(
        fields=[],
        base_variables=[],
        coefficient_algebra="not_recorded",
        constraints=[],
    )


@dataclass(frozen=True)
class CandidateDossier:
    """Structured evidence bundle for a candidate; never a novelty claim."""

    name: str
    classification: CandidateClassification
    curvature_summary: Mapping[str, Any]
    gauge_report: Mapping[str, Any] | None
    collision_report: Mapping[str, Any]
    conservation_report: Mapping[str, Any] | None
    hamiltonian_report: Mapping[str, Any] | None
    recommendation: str
    novelty_status: str = "unassessed"
    field_definition: FieldSpec | Mapping[str, Any] | None = None
    connection_pair: ConnectionSpec | Mapping[str, Any] | None = None
    generated_pde: CandidatePDEModel | Mapping[str, Any] | None = None
    cyclic_basis_report: Mapping[str, Any] | None = None
    spectral_parameter_report: Mapping[str, Any] | None = None
    publishability_classification: str | None = None
    falsifiability_statement: str | None = None

    def complete_model(self) -> CandidateDossierModel:
        """Return the canonical complete dossier model."""
        curvature = dict(self.curvature_summary)
        coefficient_proof = {
            "status": "available" if curvature.get("basis_split_complete") else "open_gate",
            "basis_split_complete": curvature.get("basis_split_complete", False),
            "curvature_terms_total": curvature.get("curvature_terms_total"),
            "curvature_terms_nonzero": curvature.get("curvature_terms_nonzero"),
            "entry_status_grid": curvature.get("entry_status_grid"),
        }
        gauge_report = _as_dict_or_empty(self.gauge_report) or {
            "status": "open_gate",
            "gauge_risk_score": None,
            "reason": "gauge/fake-pair assessment has not been run",
        }
        cyclic_report = _as_dict_or_empty(self.cyclic_basis_report) or _default_cyclic_report()
        spectral_report = _as_dict_or_empty(
            self.spectral_parameter_report
        ) or _default_spectral_report(self.gauge_report)
        conservation = _as_dict_or_empty(self.conservation_report) or {
            "status": "open_gate",
            "num_conservation_laws_found": 0,
            "method_evidence": {},
        }
        hamiltonian = _as_dict_or_empty(self.hamiltonian_report) or {
            "status": "open_gate",
            "verified": False,
            "reason": "Hamiltonian representation has not been attempted",
        }
        field_definition = (
            self.field_definition
            if isinstance(self.field_definition, FieldSpec)
            else FieldSpec(**self.field_definition)
            if self.field_definition
            else _default_field_definition()
        )
        connection_pair = (
            self.connection_pair
            if isinstance(self.connection_pair, ConnectionSpec)
            else ConnectionSpec(**self.connection_pair)
            if self.connection_pair
            else ConnectionSpec(status=str(curvature.get("status", "open_gate")))
        )
        generated_pde = (
            self.generated_pde
            if isinstance(self.generated_pde, CandidatePDEModel)
            else CandidatePDEModel(**self.generated_pde)
            if self.generated_pde
            else CandidatePDEModel(status="open_gate")
        )
        gate_evidence: list[GateEvidence] = [
            open_gate("gauge", "Gauge assessment is explicit or remains open", report=gauge_report),
            open_gate(
                "cyclic_basis",
                "Cyclic-basis fingerprint is explicit or remains open",
                report=cyclic_report,
            ),
            open_gate(
                "conservation",
                "Conservation-law mining is explicit or remains open",
                report=conservation,
            ),
            open_gate(
                "hamiltonian",
                "Hamiltonian evidence is explicit or remains open",
                report=hamiltonian,
            ),
        ]
        return CandidateDossierModel(
            name=self.name,
            classification=self.classification.value,
            recommendation=self.recommendation,
            novelty_status=self.novelty_status,
            field_definition=field_definition,
            connection_pair=connection_pair,
            generated_pde=generated_pde,
            curvature_expansion=curvature,
            coefficient_splitting_proof=coefficient_proof,
            gauge_report=gauge_report,
            cyclic_basis_report=cyclic_report,
            spectral_parameter_report=spectral_report,
            conservation_report=conservation,
            hamiltonian_report=hamiltonian,
            collision_report=dict(self.collision_report),
            publishability_classification=(
                self.publishability_classification
                or f"human_review_required:{self.recommendation}"
            ),
            falsifiability_statement=(
                self.falsifiability_statement
                or "Any unresolved gate can falsify or downgrade this candidate."
            ),
            gate_evidence=gate_evidence,
        )

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible dossier with legacy and complete-spec fields."""
        complete = self.complete_model().model_dump(mode="json")
        complete["curvature_summary"] = dict(self.curvature_summary)
        return complete

    def to_markdown(self) -> str:
        """Render a concise dossier summary."""
        lines = [
            f"# Candidate Dossier: {self.name}",
            "",
            f"- Classification: `{self.classification.value}`",
            f"- Novelty status: `{self.novelty_status}`",
            f"- Recommendation: `{self.recommendation}`",
            f"- Curvature residual zero: {self.curvature_summary.get('curvature_residual_zero')}",
            f"- Gauge risk score: {self.gauge_report.get('gauge_risk_score') if self.gauge_report else 'unknown'}",
            "",
            "## Collision Report",
            "",
            f"- Status: `{self.collision_report.get('novelty_status')}`",
            f"- Collisions: {self.collision_report.get('collisions')}",
            "",
        ]
        return "\n".join(lines).rstrip() + "\n"


def build_mkdv_second_jet_dossier() -> CandidateDossier:
    """Build the conservative calibration dossier for the nilpotent mKdV lift."""
    x, t = sp.symbols("x t")
    validation = validate()
    curvature_report = validation["curvature_report"]
    collision_report = classify_candidate(
        "second-jet nilpotent mKdV",
        metadata={"nilpotent_lift": True, "known_projection": "scalar mKdV AKNS"},
    )
    conservation_report = inherited_mkdv_conservation_report(x, t)
    hamiltonian_report = mkdv_second_jet_hamiltonian_report(x, t)
    return CandidateDossier(
        name="second-jet nilpotent mKdV",
        classification=collision_report.classification,
        curvature_summary=curvature_report.as_dict(),
        gauge_report=None,
        collision_report=collision_report.as_dict(),
        conservation_report=conservation_report.as_dict(),
        hamiltonian_report=hamiltonian_report.as_dict(),
        recommendation="calibration only; do not claim novelty",
        novelty_status=collision_report.novelty_status,
        field_definition=FieldSpec(
            fields=["u(x,t)", "v(x,t)", "w(x,t)"],
            base_variables=["x", "t", "lambda"],
            coefficient_algebra="R[eps]/(eps^3)",
            constraints=["eps^3 = 0"],
        ),
        connection_pair=ConnectionSpec(
            U="[[lambda, Q], [-Q, -lambda]]",
            V="AKNS/mKdV V with Q = u + eps*v + eps^2*w",
            representation="2x2 AKNS over truncated polynomial algebra",
            status="constructed",
        ),
        generated_pde=CandidatePDEModel(
            equation="Q_t + Q_xxx + 6*Q^2*Q_x = 0 expanded through eps^2",
            role="calibration target",
            status="validated",
        ),
        publishability_classification="calibration_known_mechanism_only",
        falsifiability_statement=(
            "The calibration would fail if any split coefficient differs from the expected "
            "second-jet mKdV flow."
        ),
    )
