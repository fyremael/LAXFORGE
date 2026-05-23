"""Finite-dimensional symbolic coefficient algebras.

The objects here are deliberately small: a named basis, structure constants,
and componentwise symbolic coefficients. This is enough to construct and audit
non-split product probes without pretending to classify the algebra globally.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import sympy as sp


@dataclass(frozen=True)
class FiniteAlgebraSpec:
    """Multiplication table for a finite-dimensional algebra over SymPy expressions."""

    name: str
    basis: tuple[str, ...]
    structure_constants: tuple[tuple[tuple[sp.Expr, ...], ...], ...]
    unit_index: int = 0

    def __post_init__(self) -> None:
        if not self.basis:
            raise ValueError("Finite algebra basis must be non-empty")
        dim = len(self.basis)
        if not 0 <= self.unit_index < dim:
            raise ValueError("unit_index must refer to a basis entry")
        if len(self.structure_constants) != dim:
            raise ValueError("Structure constants must have one row per basis element")
        for row in self.structure_constants:
            if len(row) != dim:
                raise ValueError("Structure constants must be square in the basis")
            for product in row:
                if len(product) != dim:
                    raise ValueError("Each product must have one coefficient per basis element")

    @classmethod
    def from_products(
        cls,
        name: str,
        basis: Sequence[str],
        products: Mapping[tuple[str, str], Mapping[str, sp.Expr] | Sequence[sp.Expr]],
        unit: str = "1",
    ) -> "FiniteAlgebraSpec":
        """Build a finite algebra from sparse named products."""
        basis_tuple = tuple(basis)
        if unit not in basis_tuple:
            raise ValueError("unit must be one of the basis labels")
        dim = len(basis_tuple)
        index = {label: i for i, label in enumerate(basis_tuple)}
        unit_index = index[unit]
        table: list[list[list[sp.Expr]]] = [
            [[sp.Integer(0) for _ in range(dim)] for _ in range(dim)] for _ in range(dim)
        ]

        for i in range(dim):
            table[unit_index][i][i] = sp.Integer(1)
            table[i][unit_index][i] = sp.Integer(1)

        for (left, right), value in products.items():
            if left not in index or right not in index:
                raise ValueError("Product labels must come from the algebra basis")
            coeffs = [sp.Integer(0) for _ in range(dim)]
            if isinstance(value, Mapping):
                for label, coeff in value.items():
                    if label not in index:
                        raise ValueError("Product output labels must come from the algebra basis")
                    coeffs[index[label]] = sp.sympify(coeff)
            else:
                value_tuple = tuple(sp.sympify(coeff) for coeff in value)
                if len(value_tuple) != dim:
                    raise ValueError("Dense product rows must match the basis dimension")
                coeffs = list(value_tuple)
            table[index[left]][index[right]] = coeffs

        return cls(
            name=name,
            basis=basis_tuple,
            structure_constants=tuple(
                tuple(tuple(sp.sympify(coeff) for coeff in product) for product in row)
                for row in table
            ),
            unit_index=unit_index,
        )

    @property
    def dimension(self) -> int:
        """Return the number of basis elements."""
        return len(self.basis)

    def zero_coeffs(self) -> tuple[sp.Expr, ...]:
        """Return zero coefficients in basis order."""
        return tuple(sp.Integer(0) for _ in self.basis)

    def unit_coeffs(self) -> tuple[sp.Expr, ...]:
        """Return the unit element coefficients in basis order."""
        coeffs = [sp.Integer(0) for _ in self.basis]
        coeffs[self.unit_index] = sp.Integer(1)
        return tuple(coeffs)

    def product_coeffs(
        self, left: Sequence[sp.Expr], right: Sequence[sp.Expr]
    ) -> tuple[sp.Expr, ...]:
        """Multiply two coefficient tuples using the structure constants."""
        if len(left) != self.dimension or len(right) != self.dimension:
            raise ValueError("Coefficient tuples must match the algebra dimension")
        out = [sp.Integer(0) for _ in self.basis]
        for i, a_coeff in enumerate(left):
            for j, b_coeff in enumerate(right):
                if a_coeff == 0 or b_coeff == 0:
                    continue
                product = self.structure_constants[i][j]
                for k, structure_coeff in enumerate(product):
                    if structure_coeff != 0:
                        out[k] += a_coeff * b_coeff * structure_coeff
        return tuple(sp.expand(coeff) for coeff in out)

    def product_table(self) -> dict[str, dict[str, str]]:
        """Return a compact JSON-compatible multiplication table."""
        table: dict[str, dict[str, str]] = {}
        for i, left in enumerate(self.basis):
            row: dict[str, str] = {}
            for j, right in enumerate(self.basis):
                terms = []
                for coeff, label in zip(self.structure_constants[i][j], self.basis):
                    if coeff == 0:
                        continue
                    if coeff == 1:
                        terms.append(label)
                    else:
                        terms.append(f"{coeff}*{label}")
                row[right] = " + ".join(terms) if terms else "0"
            table[left] = row
        return table

    def associativity_residuals(self) -> tuple[sp.Expr, ...]:
        """Return all basis associator residual coefficients."""
        residuals: list[sp.Expr] = []
        basis_vectors = []
        for i in range(self.dimension):
            coeffs = [sp.Integer(0) for _ in self.basis]
            coeffs[i] = sp.Integer(1)
            basis_vectors.append(tuple(coeffs))
        for a in basis_vectors:
            for b in basis_vectors:
                for c in basis_vectors:
                    left = self.product_coeffs(self.product_coeffs(a, b), c)
                    right = self.product_coeffs(a, self.product_coeffs(b, c))
                    residuals.extend(sp.simplify(x - y) for x, y in zip(left, right))
        return tuple(residuals)

    def is_associative(self) -> bool:
        """Return whether all basis associators vanish."""
        return all(residual == 0 for residual in self.associativity_residuals())


@dataclass(frozen=True)
class FiniteAlgebraElement:
    """Element of a finite-dimensional symbolic coefficient algebra."""

    coeffs: tuple[sp.Expr, ...]
    algebra: FiniteAlgebraSpec

    def __post_init__(self) -> None:
        if len(self.coeffs) != self.algebra.dimension:
            raise ValueError("Element coefficients must match algebra dimension")
        object.__setattr__(self, "coeffs", tuple(sp.sympify(coeff) for coeff in self.coeffs))

    @classmethod
    def zero(cls, algebra: FiniteAlgebraSpec) -> "FiniteAlgebraElement":
        """Return the zero element."""
        return cls(algebra.zero_coeffs(), algebra)

    @classmethod
    def one(cls, algebra: FiniteAlgebraSpec) -> "FiniteAlgebraElement":
        """Return the unit element."""
        return cls(algebra.unit_coeffs(), algebra)

    @classmethod
    def from_coeffs(
        cls, coeffs: Sequence[sp.Expr], algebra: FiniteAlgebraSpec
    ) -> "FiniteAlgebraElement":
        """Create an element, padding or trimming coefficients to the algebra dimension."""
        values = tuple(sp.sympify(coeff) for coeff in coeffs)
        if len(values) > algebra.dimension:
            values = values[: algebra.dimension]
        elif len(values) < algebra.dimension:
            values = values + tuple(sp.Integer(0) for _ in range(algebra.dimension - len(values)))
        return cls(values, algebra)

    @property
    def basis_labels(self) -> tuple[str, ...]:
        """Return display labels for coefficient splitting."""
        return self.algebra.basis

    def _coerce(self, other: object) -> "FiniteAlgebraElement":
        if isinstance(other, FiniteAlgebraElement):
            if other.algebra != self.algebra:
                raise ValueError("Cannot mix finite coefficient algebras")
            return other
        scalar = sp.sympify(other)
        return FiniteAlgebraElement(
            tuple(scalar * coeff for coeff in self.algebra.unit_coeffs()),
            self.algebra,
        )

    def __add__(self, other: object) -> "FiniteAlgebraElement":
        rhs = self._coerce(other)
        return FiniteAlgebraElement(
            tuple(a + b for a, b in zip(self.coeffs, rhs.coeffs)),
            self.algebra,
        )

    def __radd__(self, other: object) -> "FiniteAlgebraElement":
        return self.__add__(other)

    def __neg__(self) -> "FiniteAlgebraElement":
        return FiniteAlgebraElement(tuple(-coeff for coeff in self.coeffs), self.algebra)

    def __sub__(self, other: object) -> "FiniteAlgebraElement":
        return self.__add__(-self._coerce(other))

    def __rsub__(self, other: object) -> "FiniteAlgebraElement":
        return self._coerce(other).__sub__(self)

    def __mul__(self, other: object) -> "FiniteAlgebraElement":
        rhs = self._coerce(other)
        return FiniteAlgebraElement(self.algebra.product_coeffs(self.coeffs, rhs.coeffs), self.algebra)

    def __rmul__(self, other: object) -> "FiniteAlgebraElement":
        return self._coerce(other).__mul__(self)

    def __pow__(self, n: int) -> "FiniteAlgebraElement":
        if n < 0:
            raise ValueError("Negative powers are not supported in finite algebra elements")
        result = FiniteAlgebraElement.one(self.algebra)
        for _ in range(n):
            result = result * self
        return result

    def diff(self, var: sp.Symbol) -> "FiniteAlgebraElement":
        """Differentiate every coefficient."""
        return FiniteAlgebraElement(tuple(sp.diff(coeff, var) for coeff in self.coeffs), self.algebra)

    def simplify(self) -> "FiniteAlgebraElement":
        """Simplify every coefficient."""
        return FiniteAlgebraElement(tuple(sp.simplify(coeff) for coeff in self.coeffs), self.algebra)

    def expand(self) -> "FiniteAlgebraElement":
        """Expand every coefficient."""
        return FiniteAlgebraElement(tuple(sp.expand(coeff) for coeff in self.coeffs), self.algebra)

    def is_zero(self) -> bool:
        """Return whether all coefficients simplify to zero."""
        return all(sp.simplify(coeff) == 0 for coeff in self.coeffs)

    def as_expr(self) -> sp.Expr:
        """Return a commutative display expression for reports and heuristics."""
        basis_symbols = [sp.Symbol(label) for label in self.algebra.basis]
        return sp.expand(sum(coeff * symbol for coeff, symbol in zip(self.coeffs, basis_symbols)))

    def coefficient(self, basis: int | str) -> sp.Expr:
        """Return one coefficient by index or basis label."""
        index = self.algebra.basis.index(basis) if isinstance(basis, str) else basis
        return self.coeffs[index]

    def __repr__(self) -> str:
        return f"FiniteAlgebraElement({self.as_expr()}, algebra={self.algebra.name!r})"


def upper_triangular_semidirect_algebra() -> FiniteAlgebraSpec:
    """Return a small associative non-split semidirect coefficient algebra."""
    return FiniteAlgebraSpec.from_products(
        name="upper-triangular non-split semidirect algebra",
        basis=("1", "p", "n"),
        products={
            ("p", "p"): {"p": 1},
            ("p", "n"): {"n": 1},
            ("n", "p"): {},
            ("n", "n"): {},
        },
    )


def _matrix_signature(
    mat: list[list[FiniteAlgebraElement]],
) -> tuple[int, int, FiniteAlgebraSpec]:
    if not mat or not mat[0]:
        raise ValueError("Matrices must be non-empty")

    rows = len(mat)
    cols = len(mat[0])
    first = mat[0][0]
    if not isinstance(first, FiniteAlgebraElement):
        raise TypeError("Matrix entries must be FiniteAlgebraElement instances")

    for row in mat:
        if len(row) != cols:
            raise ValueError("Matrices must be rectangular")
        for entry in row:
            if not isinstance(entry, FiniteAlgebraElement):
                raise TypeError("Matrix entries must be FiniteAlgebraElement instances")
            if entry.algebra != first.algebra:
                raise ValueError("Matrix entries must share one finite coefficient algebra")

    return rows, cols, first.algebra


def _check_same_shape_and_basis(
    a: list[list[FiniteAlgebraElement]], b: list[list[FiniteAlgebraElement]]
) -> tuple[int, int, FiniteAlgebraSpec]:
    rows_a, cols_a, algebra_a = _matrix_signature(a)
    rows_b, cols_b, algebra_b = _matrix_signature(b)
    if (rows_a, cols_a) != (rows_b, cols_b):
        raise ValueError("Matrix shapes must match")
    if algebra_a != algebra_b:
        raise ValueError("Matrices must share one finite coefficient algebra")
    return rows_a, cols_a, algebra_a


def fa_matrix_mul(
    a: list[list[FiniteAlgebraElement]], b: list[list[FiniteAlgebraElement]]
) -> list[list[FiniteAlgebraElement]]:
    """Matrix multiplication for finite-algebra entries."""
    rows, shared, algebra = _matrix_signature(a)
    shared_b, cols, algebra_b = _matrix_signature(b)
    if shared != shared_b:
        raise ValueError("Matrix dimensions are incompatible for multiplication")
    if algebra != algebra_b:
        raise ValueError("Matrices must share one finite coefficient algebra")

    out: list[list[FiniteAlgebraElement]] = []
    for i in range(rows):
        row: list[FiniteAlgebraElement] = []
        for j in range(cols):
            acc = FiniteAlgebraElement.zero(algebra)
            for k in range(shared):
                acc = acc + a[i][k] * b[k][j]
            row.append(acc.expand())
        out.append(row)
    return out


def fa_matrix_add(
    a: list[list[FiniteAlgebraElement]], b: list[list[FiniteAlgebraElement]]
) -> list[list[FiniteAlgebraElement]]:
    """Matrix addition for finite-algebra entries."""
    _check_same_shape_and_basis(a, b)
    return [[(x + y).expand() for x, y in zip(row_a, row_b)] for row_a, row_b in zip(a, b)]


def fa_matrix_sub(
    a: list[list[FiniteAlgebraElement]], b: list[list[FiniteAlgebraElement]]
) -> list[list[FiniteAlgebraElement]]:
    """Matrix subtraction for finite-algebra entries."""
    _check_same_shape_and_basis(a, b)
    return [[(x - y).expand() for x, y in zip(row_a, row_b)] for row_a, row_b in zip(a, b)]


def fa_matrix_diff(
    a: list[list[FiniteAlgebraElement]], var: sp.Symbol
) -> list[list[FiniteAlgebraElement]]:
    """Differentiate a finite-algebra matrix componentwise."""
    _matrix_signature(a)
    return [[entry.diff(var).expand() for entry in row] for row in a]


def fa_matrix_commutator(
    a: list[list[FiniteAlgebraElement]], b: list[list[FiniteAlgebraElement]]
) -> list[list[FiniteAlgebraElement]]:
    """Return the finite-algebra matrix commutator."""
    return fa_matrix_sub(fa_matrix_mul(a, b), fa_matrix_mul(b, a))


def fa_zero_curvature(
    U: list[list[FiniteAlgebraElement]],
    V: list[list[FiniteAlgebraElement]],
    x: sp.Symbol,
    t: sp.Symbol,
) -> list[list[FiniteAlgebraElement]]:
    """Compute U_t - V_x + [U,V] over finite-algebra matrix entries."""
    return fa_matrix_add(
        fa_matrix_sub(fa_matrix_diff(U, t), fa_matrix_diff(V, x)),
        fa_matrix_commutator(U, V),
    )
