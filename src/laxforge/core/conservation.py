"""Initial conservation-law helpers for truncated mKdV calibration."""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from laxforge.algebra.truncated_poly import TruncatedPoly
from laxforge.core.models import ConservationReportModel, GateEvidence, open_gate


@dataclass(frozen=True)
class ConservationLaw:
    """A candidate conserved density with provenance."""

    name: str
    density: sp.Expr
    source: str

    def as_dict(self) -> dict[str, str]:
        """Return a JSON-compatible conservation-law summary."""
        return {"name": self.name, "density": str(self.density), "source": self.source}


@dataclass(frozen=True)
class ConservationReport:
    """Conservation-law mining report with method-level evidence."""

    status: str
    laws: tuple[ConservationLaw, ...]
    method_evidence: dict[str, GateEvidence]

    @property
    def num_conservation_laws_found(self) -> int:
        return len(self.laws)

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible conservation report."""
        return self.complete_model().model_dump(mode="json")

    def complete_model(self) -> ConservationReportModel:
        """Return the canonical conservation report model."""
        return ConservationReportModel(
            status=self.status,
            num_conservation_laws_found=len(self.laws),
            laws=[law.as_dict() for law in self.laws],
            method_evidence=self.method_evidence,
        )


def inherited_mkdv_conservation_laws(
    x: sp.Symbol, t: sp.Symbol, order: int = 3
) -> tuple[ConservationLaw, ...]:
    """Expand basic scalar mKdV conserved densities through R[eps]/(eps^order)."""
    fields = [sp.Function(name)(x, t) for name in ("u", "v", "w")[:order]]
    Q = TruncatedPoly.from_coeffs(fields, order=order)
    Qx = Q.diff(x)
    scalar_densities = (
        ("Q", Q),
        ("Q^2", Q**2),
        ("1/2 Q_x^2 - 1/2 Q^4", sp.Rational(1, 2) * (Qx**2) - sp.Rational(1, 2) * (Q**4)),
    )

    laws: list[ConservationLaw] = []
    for density_name, density in scalar_densities:
        for degree, coefficient in enumerate(density.coeffs):
            laws.append(
                ConservationLaw(
                    name=f"{density_name}:eps^{degree}",
                    density=sp.simplify(coefficient),
                    source="inherited scalar mKdV density expanded in truncated algebra",
                )
            )
    return tuple(laws)


def inherited_mkdv_conservation_report(
    x: sp.Symbol, t: sp.Symbol, order: int = 3
) -> ConservationReport:
    """Return the calibration conservation report."""
    laws = inherited_mkdv_conservation_laws(x, t, order=order)
    return ConservationReport(
        status="inherited_hierarchy_evidence",
        laws=laws,
        method_evidence={
            "inherited_scalar_hierarchy": GateEvidence(
                name="inherited_scalar_hierarchy",
                status="pass",
                summary="Scalar mKdV densities expanded through the truncated algebra.",
                details={"order": order},
            ),
            "trace_monodromy": open_gate(
                "trace_monodromy",
                "Trace/monodromy expansion not implemented for this calibration report.",
            ),
            "riccati": open_gate(
                "riccati",
                "Riccati expansion not implemented for this calibration report.",
            ),
            "homotopy": open_gate(
                "homotopy",
                "Homotopy-operator mining not implemented for this calibration report.",
            ),
        },
    )


def open_conservation_report(reason: str) -> ConservationReport:
    """Return an explicit open-gate conservation report."""
    return ConservationReport(
        status="open_gate",
        laws=(),
        method_evidence={
            "inherited_scalar_hierarchy": open_gate("inherited_scalar_hierarchy", reason),
            "trace_monodromy": open_gate("trace_monodromy", reason),
            "riccati": open_gate("riccati", reason),
            "homotopy": open_gate("homotopy", reason),
        },
    )
