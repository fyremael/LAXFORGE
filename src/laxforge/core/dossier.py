"""Candidate dossier scaffolding."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import sympy as sp

from laxforge.core.conservation import inherited_mkdv_conservation_laws
from laxforge.core.hamiltonian import mkdv_second_jet_hamiltonian_report
from laxforge.core.prior_art import CandidateClassification, classify_candidate
from laxforge.examples.mkdv_second_jet import validate


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

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible dossier."""
        return {
            "name": self.name,
            "classification": self.classification.value,
            "curvature_summary": dict(self.curvature_summary),
            "gauge_report": dict(self.gauge_report) if self.gauge_report else None,
            "collision_report": dict(self.collision_report),
            "conservation_report": dict(self.conservation_report) if self.conservation_report else None,
            "hamiltonian_report": dict(self.hamiltonian_report) if self.hamiltonian_report else None,
            "recommendation": self.recommendation,
            "novelty_status": self.novelty_status,
        }

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
    conservation_laws = inherited_mkdv_conservation_laws(x, t)
    hamiltonian_report = mkdv_second_jet_hamiltonian_report(x, t)
    return CandidateDossier(
        name="second-jet nilpotent mKdV",
        classification=collision_report.classification,
        curvature_summary=curvature_report.as_dict(),
        gauge_report=None,
        collision_report=collision_report.as_dict(),
        conservation_report={
            "num_conservation_laws_found": len(conservation_laws),
            "laws": [law.as_dict() for law in conservation_laws],
        },
        hamiltonian_report=hamiltonian_report.as_dict(),
        recommendation="calibration only; do not claim novelty",
        novelty_status=collision_report.novelty_status,
    )
