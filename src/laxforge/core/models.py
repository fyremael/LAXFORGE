"""Canonical evidence models for LAXFORGE.

The models deliberately describe evidence and open gates. They do not certify
mathematical originality or promotion readiness.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


GateStatus = Literal["pass", "fail", "warn", "open", "unsupported", "not_applicable"]


class EvidenceModel(BaseModel):
    """Base model with strict, JSON-friendly serialization defaults."""

    model_config = ConfigDict(extra="forbid")


class FieldSpec(EvidenceModel):
    """Field/base-variable definition for a candidate."""

    fields: list[str] = Field(default_factory=list)
    base_variables: list[str] = Field(default_factory=list)
    coefficient_algebra: str = "unspecified"
    constraints: list[str] = Field(default_factory=list)


class ConnectionSpec(EvidenceModel):
    """Connection pair evidence."""

    U: Any = None
    V: Any = None
    representation: str = "not_constructed"
    status: str = "open_gate"


class CandidatePDEModel(EvidenceModel):
    """Generated or target PDE evidence."""

    equation: str = "not_recorded"
    role: str = "target_or_generated"
    status: str = "open_gate"


class GateEvidence(EvidenceModel):
    """One named gate result."""

    name: str
    status: GateStatus
    summary: str
    details: dict[str, Any] = Field(default_factory=dict)


class ConservationReportModel(EvidenceModel):
    """Method-level conservation-law evidence."""

    status: str = "open_gate"
    num_conservation_laws_found: int = 0
    laws: list[dict[str, Any]] = Field(default_factory=list)
    method_evidence: dict[str, GateEvidence] = Field(default_factory=dict)


class HamiltonianReportModel(EvidenceModel):
    """Hamiltonian and operator evidence."""

    status: str = "open_gate"
    verified: bool = False
    variational_derivative: GateEvidence
    constant_poisson_operator: GateEvidence
    jacobi_check: GateEvidence
    compatibility_attempt: GateEvidence
    details: dict[str, Any] = Field(default_factory=dict)


class InvariantReportModel(EvidenceModel):
    """Candidate-comparison fingerprints."""

    cyclic_basis_data: dict[str, Any] | None = None
    spectral_parameter_essentiality: str = "untested"
    trace_invariants: list[str] = Field(default_factory=list)
    block_decomposition_signature: str = "untested"
    grading_signature: str = "untested"
    generated_pde_canonical_form: str = "untested"
    fingerprint: str = "open_gate"


class CandidateDossierModel(EvidenceModel):
    """Complete candidate dossier matching docs/SPEC.md core deliverables."""

    name: str
    classification: str
    recommendation: str
    novelty_status: str = "unassessed"
    field_definition: FieldSpec
    connection_pair: ConnectionSpec
    generated_pde: CandidatePDEModel
    curvature_expansion: dict[str, Any]
    coefficient_splitting_proof: dict[str, Any]
    gauge_report: dict[str, Any]
    cyclic_basis_report: dict[str, Any]
    spectral_parameter_report: dict[str, Any]
    conservation_report: dict[str, Any]
    hamiltonian_report: dict[str, Any]
    collision_report: dict[str, Any]
    publishability_classification: str
    falsifiability_statement: str
    gate_evidence: list[GateEvidence] = Field(default_factory=list)


class ArtifactBundleModel(EvidenceModel):
    """Expected explicit artifact bundle for a candidate."""

    candidate_json: str = "candidate.json"
    curvature_report_md: str = "curvature_report.md"
    proof_sketch_md: str = "proof_sketch.md"
    gauge_report_md: str = "gauge_report.md"
    invariants_json: str = "invariants.json"
    conservation_report_md: str = "conservation_report.md"
    hamiltonian_report_md: str = "hamiltonian_report.md"
    prior_art_report_md: str = "prior_art_report.md"
    publishability_classification_md: str = "publishability_classification.md"

    def filenames(self) -> tuple[str, ...]:
        """Return artifact filenames in stable order."""
        return tuple(str(value) for value in self.model_dump().values())


def open_gate(name: str, summary: str, **details: Any) -> GateEvidence:
    """Build a standardized open-gate evidence record."""
    return GateEvidence(name=name, status="open", summary=summary, details=details)

