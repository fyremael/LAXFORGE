"""Small ansatz-generation helpers for symbolic calibration runs."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations_with_replacement
from typing import Mapping, Sequence

import sympy as sp

from laxforge.algebra.truncated_poly import TruncatedPoly


@dataclass(frozen=True)
class WeightSpec:
    """Weights for fields, derivatives, and spectral-parameter powers."""

    field_weights: Mapping[str, int]
    derivative_weight: int = 1
    lambda_weight: int = 1

    def weight_for_field(self, field: sp.Expr) -> int:
        """Return the configured weight for a field expression."""
        name = getattr(field.func, "__name__", str(field))
        if name not in self.field_weights:
            raise KeyError(f"No weight configured for field {name!r}")
        return self.field_weights[name]


@dataclass(frozen=True)
class MatrixAnsatz:
    """Polynomial-in-lambda matrix ansatz with symbolic coefficients."""

    matrix: list[list[TruncatedPoly]]
    coefficients: tuple[sp.Symbol, ...]
    lambda_symbol: sp.Symbol
    degree: int


def differential_factors(
    fields: Sequence[sp.Expr], x: sp.Symbol, max_derivative_order: int
) -> tuple[sp.Expr, ...]:
    """Return fields and x-derivatives up to the requested order."""
    factors = []
    for field in fields:
        factors.append(field)
        factors.extend(sp.diff(field, x, order) for order in range(1, max_derivative_order + 1))
    return tuple(factors)


def expression_weight(
    expr: sp.Expr, spec: WeightSpec, x: sp.Symbol, lambda_symbol: sp.Symbol | None = None
) -> int:
    """Compute the additive symbolic weight of a monomial expression."""
    expr = sp.sympify(expr)
    if expr == 1:
        return 0
    if lambda_symbol is not None and expr == lambda_symbol:
        return spec.lambda_weight
    if isinstance(expr, sp.Derivative):
        derivative_order = sum(count for var, count in expr.variable_count if var == x)
        return spec.weight_for_field(expr.expr) + spec.derivative_weight * derivative_order
    if expr.is_Function:
        return spec.weight_for_field(expr)
    if isinstance(expr, sp.Pow):
        base, exponent = expr.args
        if not exponent.is_integer or exponent < 0:
            raise ValueError(f"Unsupported non-polynomial factor: {expr}")
        return int(exponent) * expression_weight(base, spec, x, lambda_symbol)
    if isinstance(expr, sp.Mul):
        return sum(expression_weight(arg, spec, x, lambda_symbol) for arg in expr.args)
    if expr.is_Number:
        return 0
    raise ValueError(f"Cannot assign a symbolic weight to {expr!r}")


def generate_homogeneous_monomials(
    fields: Sequence[sp.Expr],
    x: sp.Symbol,
    spec: WeightSpec,
    total_weight: int,
    max_derivative_order: int,
    max_factors: int | None = None,
) -> tuple[sp.Expr, ...]:
    """Generate deterministic commutative differential monomials of one weight."""
    if total_weight < 0:
        raise ValueError("total_weight must be non-negative")
    if total_weight == 0:
        return (sp.Integer(1),)

    factors = differential_factors(fields, x, max_derivative_order)
    weighted_factors = tuple((factor, expression_weight(factor, spec, x)) for factor in factors)
    min_weight = min(weight for _factor, weight in weighted_factors)
    if max_factors is None:
        max_factors = max(1, total_weight // min_weight)

    monomials: set[sp.Expr] = set()
    for length in range(1, max_factors + 1):
        for combo in combinations_with_replacement(weighted_factors, length):
            weight = sum(item_weight for _item, item_weight in combo)
            if weight == total_weight:
                monomials.add(sp.prod(item for item, _item_weight in combo))

    return tuple(sorted((sp.expand(monomial) for monomial in monomials), key=str))


def polynomial_lambda_matrix_ansatz(
    rows: int,
    cols: int,
    lambda_symbol: sp.Symbol,
    degree: int,
    coefficient_prefix: str = "a",
    algebra_order: int = 1,
) -> MatrixAnsatz:
    """Build a matrix ansatz whose entries are scalar polynomials in lambda."""
    coefficients: list[sp.Symbol] = []
    matrix: list[list[TruncatedPoly]] = []
    for i in range(rows):
        row: list[TruncatedPoly] = []
        for j in range(cols):
            entry = sp.Integer(0)
            for power in range(degree + 1):
                coeff = sp.Symbol(f"{coefficient_prefix}_{i}_{j}_{power}")
                coefficients.append(coeff)
                entry += coeff * lambda_symbol**power
            row.append(TruncatedPoly.from_coeffs([entry], order=algebra_order))
        matrix.append(row)
    return MatrixAnsatz(
        matrix=matrix,
        coefficients=tuple(coefficients),
        lambda_symbol=lambda_symbol,
        degree=degree,
    )
