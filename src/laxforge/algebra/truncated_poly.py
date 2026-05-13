"""Truncated polynomial coefficient algebra.

This module implements symbolic arithmetic in R[eps]/(eps^order), represented as
component tuples. It is intentionally small, auditable, and friendly to symbolic
zero-curvature calculations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple

import sympy as sp


@dataclass(frozen=True)
class TruncatedPoly:
    """Element of a truncated polynomial algebra R[eps]/(eps^order)."""

    coeffs: Tuple[sp.Expr, ...]
    order: int = 3
    symbol_name: str = "eps"

    def __post_init__(self) -> None:
        if self.order < 1:
            raise ValueError("Truncated polynomial order must be positive")
        values = tuple(sp.sympify(c) for c in self.coeffs)
        if len(values) != self.order:
            raise ValueError(f"Expected {self.order} coefficients, got {len(values)}")
        object.__setattr__(self, "coeffs", values)

    @classmethod
    def zero(cls, order: int = 3, symbol_name: str = "eps") -> "TruncatedPoly":
        return cls(tuple(sp.Integer(0) for _ in range(order)), order, symbol_name)

    @classmethod
    def one(cls, order: int = 3, symbol_name: str = "eps") -> "TruncatedPoly":
        return cls((sp.Integer(1),) + tuple(sp.Integer(0) for _ in range(order - 1)), order, symbol_name)

    @classmethod
    def from_coeffs(
        cls, coeffs: Iterable[sp.Expr], order: int = 3, symbol_name: str = "eps"
    ) -> "TruncatedPoly":
        values = tuple(sp.sympify(c) for c in coeffs)
        if len(values) > order:
            values = values[:order]
        elif len(values) < order:
            values = values + tuple(sp.Integer(0) for _ in range(order - len(values)))
        return cls(values, order, symbol_name)

    def _coerce(self, other: object) -> "TruncatedPoly":
        if isinstance(other, TruncatedPoly):
            if other.order != self.order:
                raise ValueError("Cannot mix truncated polynomial orders")
            if other.symbol_name != self.symbol_name:
                raise ValueError("Cannot mix truncated polynomial basis symbols")
            return other
        return TruncatedPoly.from_coeffs([sp.sympify(other)], self.order, self.symbol_name)

    def __add__(self, other: object) -> "TruncatedPoly":
        rhs = self._coerce(other)
        return TruncatedPoly(tuple(a + b for a, b in zip(self.coeffs, rhs.coeffs)), self.order, self.symbol_name)

    def __radd__(self, other: object) -> "TruncatedPoly":
        return self.__add__(other)

    def __neg__(self) -> "TruncatedPoly":
        return TruncatedPoly(tuple(-a for a in self.coeffs), self.order, self.symbol_name)

    def __sub__(self, other: object) -> "TruncatedPoly":
        return self.__add__(-self._coerce(other))

    def __rsub__(self, other: object) -> "TruncatedPoly":
        return self._coerce(other).__sub__(self)

    def __mul__(self, other: object) -> "TruncatedPoly":
        rhs = self._coerce(other)
        out = [sp.Integer(0) for _ in range(self.order)]
        for i, a in enumerate(self.coeffs):
            for j, b in enumerate(rhs.coeffs):
                if i + j < self.order:
                    out[i + j] += a * b
        return TruncatedPoly(tuple(sp.expand(c) for c in out), self.order, self.symbol_name)

    def __rmul__(self, other: object) -> "TruncatedPoly":
        return self.__mul__(other)

    def __pow__(self, n: int) -> "TruncatedPoly":
        if n < 0:
            raise ValueError("Negative powers are not supported in truncated algebra")
        result = TruncatedPoly.one(self.order, self.symbol_name)
        for _ in range(n):
            result = result * self
        return result

    def diff(self, var: sp.Symbol) -> "TruncatedPoly":
        return TruncatedPoly(tuple(sp.diff(c, var) for c in self.coeffs), self.order, self.symbol_name)

    def simplify(self) -> "TruncatedPoly":
        return TruncatedPoly(tuple(sp.simplify(c) for c in self.coeffs), self.order, self.symbol_name)

    def expand(self) -> "TruncatedPoly":
        return TruncatedPoly(tuple(sp.expand(c) for c in self.coeffs), self.order, self.symbol_name)

    def is_zero(self) -> bool:
        return all(sp.simplify(c) == 0 for c in self.coeffs)

    def as_expr(self) -> sp.Expr:
        eps = sp.Symbol(self.symbol_name)
        return sp.expand(sum(c * eps**i for i, c in enumerate(self.coeffs)))

    def coefficient(self, degree: int) -> sp.Expr:
        return self.coeffs[degree]

    def __repr__(self) -> str:
        return f"TruncatedPoly({self.as_expr()}, order={self.order})"


def _matrix_signature(mat: list[list[TruncatedPoly]]) -> tuple[int, int, int, str]:
    if not mat or not mat[0]:
        raise ValueError("Matrices must be non-empty")

    rows = len(mat)
    cols = len(mat[0])
    first = mat[0][0]
    if not isinstance(first, TruncatedPoly):
        raise TypeError("Matrix entries must be TruncatedPoly instances")

    for row in mat:
        if len(row) != cols:
            raise ValueError("Matrices must be rectangular")
        for entry in row:
            if not isinstance(entry, TruncatedPoly):
                raise TypeError("Matrix entries must be TruncatedPoly instances")
            if entry.order != first.order or entry.symbol_name != first.symbol_name:
                raise ValueError("Matrix entries must share one truncated-polynomial basis")

    return rows, cols, first.order, first.symbol_name


def _check_same_shape_and_basis(
    a: list[list[TruncatedPoly]], b: list[list[TruncatedPoly]]
) -> tuple[int, int, int, str]:
    rows_a, cols_a, order_a, symbol_a = _matrix_signature(a)
    rows_b, cols_b, order_b, symbol_b = _matrix_signature(b)
    if (rows_a, cols_a) != (rows_b, cols_b):
        raise ValueError("Matrix shapes must match")
    if (order_a, symbol_a) != (order_b, symbol_b):
        raise ValueError("Matrices must share one truncated-polynomial basis")
    return rows_a, cols_a, order_a, symbol_a


def tp_matrix_mul(a: list[list[TruncatedPoly]], b: list[list[TruncatedPoly]]) -> list[list[TruncatedPoly]]:
    """Matrix multiplication for truncated-polynomial entries."""
    rows, shared, order, symbol_name = _matrix_signature(a)
    shared_b, cols, order_b, symbol_b = _matrix_signature(b)
    if shared != shared_b:
        raise ValueError("Matrix dimensions are incompatible for multiplication")
    if (order, symbol_name) != (order_b, symbol_b):
        raise ValueError("Matrices must share one truncated-polynomial basis")

    out: list[list[TruncatedPoly]] = []
    for i in range(rows):
        row: list[TruncatedPoly] = []
        for j in range(cols):
            acc = TruncatedPoly.zero(order, symbol_name)
            for k in range(shared):
                acc = acc + a[i][k] * b[k][j]
            row.append(acc.expand())
        out.append(row)
    return out


def tp_matrix_add(a: list[list[TruncatedPoly]], b: list[list[TruncatedPoly]]) -> list[list[TruncatedPoly]]:
    _check_same_shape_and_basis(a, b)
    return [[(x + y).expand() for x, y in zip(row_a, row_b)] for row_a, row_b in zip(a, b)]


def tp_matrix_sub(a: list[list[TruncatedPoly]], b: list[list[TruncatedPoly]]) -> list[list[TruncatedPoly]]:
    _check_same_shape_and_basis(a, b)
    return [[(x - y).expand() for x, y in zip(row_a, row_b)] for row_a, row_b in zip(a, b)]


def tp_matrix_diff(a: list[list[TruncatedPoly]], var: sp.Symbol) -> list[list[TruncatedPoly]]:
    _matrix_signature(a)
    return [[x.diff(var).expand() for x in row] for row in a]


def tp_matrix_commutator(a: list[list[TruncatedPoly]], b: list[list[TruncatedPoly]]) -> list[list[TruncatedPoly]]:
    return tp_matrix_sub(tp_matrix_mul(a, b), tp_matrix_mul(b, a))
