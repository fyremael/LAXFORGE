"""Functional-completeness audit for current written specs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from laxforge.core.artifacts import required_artifact_filenames
from laxforge.core.dossier import build_mkdv_second_jet_dossier
from laxforge.core.prior_art import default_prior_art_registry
from laxforge.search.bulk import run_scaled_candidate_search
from laxforge.search.run_matrix import (
    run_density_matrix_search,
    run_matrix_catalog,
)
from laxforge.ui.dashboard import build_dashboard_payload


REQUIRED_RUN_IDS = {
    "CAL-001",
    "CAL-002",
    "CAL-003",
    "CAL-004",
    "GAU-001",
    "GAU-002",
    "GAU-003",
    "GAU-004",
    "DIS-001",
    "DIS-002",
    "DIS-003",
    "DIS-004",
    "DIS-005",
    "DIS-006",
}
REQUIRED_ARTIFACTS = {
    "candidate.json",
    "curvature_report.md",
    "proof_sketch.md",
    "gauge_report.md",
    "invariants.json",
    "conservation_report.md",
    "hamiltonian_report.md",
    "prior_art_report.md",
    "publishability_classification.md",
}
REQUIRED_DOSSIER_FIELDS = {
    "name",
    "classification",
    "curvature_expansion",
    "coefficient_splitting_proof",
    "gauge_report",
    "collision_report",
    "conservation_report",
    "hamiltonian_report",
    "recommendation",
    "field_definition",
    "connection_pair",
    "generated_pde",
    "cyclic_basis_report",
    "spectral_parameter_report",
    "publishability_classification",
    "falsifiability_statement",
}
REQUIRED_PRIOR_ART_TERMS = {
    "akns",
    "kdv",
    "mkdv",
    "nls",
    "sine-gordon",
    "toda",
    "kp",
    "gelfand-dickey",
    "drinfeld-sokolov",
    "vector",
    "matrix mkdv",
    "integrable couplings",
    "nilpotent",
    "supersymmetric",
    "graded",
    "nonlocal",
    "chiral",
    "heisenberg",
    "coadjoint",
    "symmetric-space",
}
FORBIDDEN_PROMOTION_TERMS = ("novel", "publishable", "publication")


@dataclass(frozen=True)
class FunctionalCompletenessCheck:
    """One spec-parity audit check."""

    check_id: str
    label: str
    status: str
    detail: str

    def as_dict(self) -> dict[str, str]:
        """Return a JSON-compatible check record."""
        return {
            "check_id": self.check_id,
            "label": self.label,
            "status": self.status,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class FunctionalCompletenessAuditReport:
    """Summary of full-spec parity checks."""

    report_id: str
    status: str
    checks: tuple[FunctionalCompletenessCheck, ...]

    @property
    def passed(self) -> bool:
        """Return whether every audit check passed."""
        return self.status == "pass"

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible audit report."""
        return {
            "report_id": self.report_id,
            "status": self.status,
            "checks": [check.as_dict() for check in self.checks],
        }

    def to_markdown(self) -> str:
        """Render a compact audit report."""
        lines = [
            f"# Functional Completeness Audit {self.report_id}",
            "",
            f"- Status: `{self.status}`",
            "",
            "| Check | Status | Detail |",
            "|---|---|---|",
        ]
        for check in self.checks:
            lines.append(f"| {check.check_id}: {check.label} | `{check.status}` | {check.detail} |")
        return "\n".join(lines).rstrip() + "\n"


def _check(check_id: str, label: str, ok: bool, pass_detail: str, fail_detail: str) -> FunctionalCompletenessCheck:
    return FunctionalCompletenessCheck(
        check_id=check_id,
        label=label,
        status="pass" if ok else "fail",
        detail=pass_detail if ok else fail_detail,
    )


def build_functional_completeness_audit_report() -> FunctionalCompletenessAuditReport:
    """Audit current implementation against the written run matrix and artifact spec."""
    dossier_model = build_mkdv_second_jet_dossier().complete_model()
    dossier_data = dossier_model.model_dump(mode="json")
    run_ids = {entry.run_id for entry in run_matrix_catalog()}
    registry_text = " ".join(
        " ".join((family.name.lower(), *family.fingerprints))
        for family in default_prior_art_registry()
    )
    artifact_names = set(required_artifact_filenames())
    density_report = run_density_matrix_search()
    scaled_report = run_scaled_candidate_search()
    dashboard_payload = build_dashboard_payload()
    dashboard_text = json.dumps(dashboard_payload, sort_keys=True).lower()
    forbidden_terms = [
        term for term in FORBIDDEN_PROMOTION_TERMS if term in dashboard_text
    ]

    missing_dossier_fields = sorted(REQUIRED_DOSSIER_FIELDS - set(dossier_data))
    missing_run_ids = sorted(REQUIRED_RUN_IDS - run_ids)
    missing_artifacts = sorted(REQUIRED_ARTIFACTS - artifact_names)
    extra_artifacts = sorted(artifact_names - REQUIRED_ARTIFACTS)
    missing_prior_art = sorted(
        term for term in REQUIRED_PRIOR_ART_TERMS if term not in registry_text
    )
    checks = (
        _check(
            "FC-001",
            "canonical dossier model",
            not missing_dossier_fields,
            "candidate dossier exposes all required canonical fields",
            f"missing dossier fields: {missing_dossier_fields}",
        ),
        _check(
            "FC-002",
            "dossier JSON serialization",
            bool(dossier_model.model_dump_json()),
            "canonical dossier serializes to JSON",
            "canonical dossier did not serialize to JSON",
        ),
        _check(
            "FC-003",
            "artifact bundle filenames",
            artifact_names == REQUIRED_ARTIFACTS,
            "artifact writer covers the required bundle files",
            f"missing={missing_artifacts}; extra={extra_artifacts}",
        ),
        _check(
            "FC-004",
            "run-matrix parity",
            not missing_run_ids,
            "CAL, GAU, and DIS run-matrix entries are present",
            f"missing run ids: {missing_run_ids}",
        ),
        _check(
            "FC-005",
            "density and scaled lane split",
            density_report.run_id == "DIS-003" and scaled_report.run_id == "DIS-006",
            "DIS-003 is density-matrix and DIS-006 is scaled sphere triage",
            f"got density={density_report.run_id}, scaled={scaled_report.run_id}",
        ),
        _check(
            "FC-006",
            "prior-art registry breadth",
            not missing_prior_art,
            "registry covers required known-family zones",
            f"missing prior-art terms: {missing_prior_art}",
        ),
        _check(
            "FC-007",
            "runtime language guard",
            not forbidden_terms,
            "dashboard payload contains no promotion-language terms",
            f"forbidden terms in dashboard payload: {forbidden_terms}",
        ),
    )
    status = "pass" if all(check.status == "pass" for check in checks) else "fail"
    return FunctionalCompletenessAuditReport(
        report_id="FUNC-COMP-001",
        status=status,
        checks=checks,
    )
