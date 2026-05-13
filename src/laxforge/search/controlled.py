"""Controlled discovery runs that record failures instead of hiding them."""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from laxforge.core.dossier import CandidateDossier


@dataclass(frozen=True)
class DiscoveryCandidateRecord:
    """One controlled-search candidate, including failed or discarded cases."""

    name: str
    tangent_condition: sp.Expr
    dossier: CandidateDossier
    failure_reasons: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible discovery-candidate record."""
        return {
            "name": self.name,
            "tangent_condition": str(self.tangent_condition),
            "dossier": self.dossier.as_dict(),
            "failure_reasons": list(self.failure_reasons),
        }


@dataclass(frozen=True)
class DiscoveryRunReport:
    """Summary for a controlled discovery run."""

    run_id: str
    arena: str
    candidates: tuple[DiscoveryCandidateRecord, ...]
    ranking_basis: str = "validation status, not excitement"

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible discovery-run report."""
        return {
            "run_id": self.run_id,
            "arena": self.arena,
            "ranking_basis": self.ranking_basis,
            "candidates": [candidate.as_dict() for candidate in self.candidates],
        }


def run_sphere_tangent_projection_search() -> DiscoveryRunReport:
    """Run a minimal sphere-valued tangent-flow control experiment.

    The generated control candidate uses a trivial zero connection, so it is
    deliberately classified as fake and recommended for discard. Its purpose is
    to exercise the dossier, curvature, gauge-risk, and collision machinery.
    """
    from laxforge.search.sphere import SphereSearchConfig, run_sphere_low_order_search

    dis002_report = run_sphere_low_order_search(
        SphereSearchConfig(
            max_order=0,
            include_zero_control=True,
            include_heisenberg_template=False,
        )
    )
    return DiscoveryRunReport(
        run_id="DIS-002-control",
        arena="sphere-valued tangent-projected flow ansatz",
        candidates=dis002_report.candidates,
    )
