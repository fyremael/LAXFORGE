"""Initial conservation-law helpers for truncated mKdV calibration."""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from laxforge.algebra.truncated_poly import TruncatedPoly


@dataclass(frozen=True)
class ConservationLaw:
    """A candidate conserved density with provenance."""

    name: str
    density: sp.Expr
    source: str

    def as_dict(self) -> dict[str, str]:
        """Return a JSON-compatible conservation-law summary."""
        return {"name": self.name, "density": str(self.density), "source": self.source}


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
