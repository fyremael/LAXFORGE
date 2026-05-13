"""Cyclic-basis fingerprints for small explicit matrix spectral problems."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import sympy as sp

from laxforge.core.gauge import matrix_commutator


@dataclass(frozen=True)
class CyclicBasisReport:
    """Cyclic-basis closure summary."""

    basis_dimension: int
    closure_relation: str
    closure_coefficients: dict[str, sp.Expr]
    lambda_dependent_coefficients: bool
    fingerprint: str

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible cyclic-basis report."""
        return {
            "basis_dimension": self.basis_dimension,
            "closure_relation": self.closure_relation,
            "closure_coefficients": {
                key: str(value) for key, value in self.closure_coefficients.items()
            },
            "lambda_dependent_coefficients": self.lambda_dependent_coefficients,
            "fingerprint": self.fingerprint,
        }


def characteristic_matrix(X: sp.MatrixBase, field: sp.Expr) -> sp.Matrix:
    """Compute the characteristic matrix dX/dfield."""
    return X.applyfunc(lambda entry: sp.diff(entry, field))


def covariant_derivative(X: sp.MatrixBase, Y: sp.MatrixBase, x: sp.Symbol) -> sp.Matrix:
    """Compute nabla_x(Y) = D_x(Y) - [X,Y]."""
    return sp.simplify(Y.diff(x) - matrix_commutator(X, Y))


def _flatten(matrix: sp.MatrixBase) -> tuple[sp.Expr, ...]:
    return tuple(matrix[i, j] for i in range(matrix.rows) for j in range(matrix.cols))


def _closure_coefficients(
    target: sp.MatrixBase, basis: Sequence[sp.MatrixBase]
) -> dict[sp.Symbol, sp.Expr] | None:
    coefficients = sp.symbols(f"c0:{len(basis)}")
    linear_combination = sp.zeros(target.rows, target.cols)
    for coeff, basis_matrix in zip(coefficients, basis):
        linear_combination += coeff * basis_matrix
    equations = [sp.simplify(expr) for expr in _flatten(target - linear_combination)]
    solutions = sp.solve(equations, coefficients, dict=True, simplify=True)
    return dict(solutions[0]) if solutions else None


def compute_cyclic_basis(
    X: sp.MatrixBase,
    field: sp.Expr,
    x: sp.Symbol,
    lambda_symbol: sp.Symbol | None = None,
    max_steps: int = 8,
) -> CyclicBasisReport:
    """Compute a small cyclic basis and stop at the first closure relation."""
    basis: list[sp.Matrix] = []
    current = characteristic_matrix(X, field)

    for order in range(max_steps + 1):
        if basis:
            closure = _closure_coefficients(current, basis)
            if closure is not None:
                named_closure = {f"c{i}": sp.simplify(closure[sp.Symbol(f"c{i}")]) for i in range(len(basis))}
                lambda_dependent = bool(
                    lambda_symbol
                    and any(value.has(lambda_symbol) for value in named_closure.values())
                )
                fingerprint = (
                    f"dim={len(basis)};closure_order={order};"
                    f"lambda_dependent={lambda_dependent};"
                    f"coeffs={tuple((key, str(value)) for key, value in named_closure.items())}"
                )
                return CyclicBasisReport(
                    basis_dimension=len(basis),
                    closure_relation=f"nabla^{order} C closes on previous basis elements",
                    closure_coefficients=named_closure,
                    lambda_dependent_coefficients=lambda_dependent,
                    fingerprint=fingerprint,
                )

        basis.append(current)
        current = covariant_derivative(X, current, x)

    fingerprint = f"dim={len(basis)};closure_order=unresolved;lambda_dependent=unknown"
    return CyclicBasisReport(
        basis_dimension=len(basis),
        closure_relation="unresolved within max_steps",
        closure_coefficients={},
        lambda_dependent_coefficients=False,
        fingerprint=fingerprint,
    )
