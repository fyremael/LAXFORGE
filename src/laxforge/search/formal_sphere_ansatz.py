"""Formal local-vector ansatz solver for sphere-valued candidates."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Iterable

import sympy as sp

from laxforge.search.overnight import OvernightCandidate


@dataclass(frozen=True, order=True)
class Atom:
    """Formal vector atom built from sphere derivatives."""

    kind: str
    i: int
    j: int = -1

    def label(self) -> str:
        """Return a compact label."""
        if self.kind == "S":
            return "s" + ("x" * self.i)
        return f"{'s' + ('x' * self.i)}_cross_{'s' + ('x' * self.j)}"


@dataclass(frozen=True)
class FormalVector:
    """Linear combination of formal vector atoms over scalar-invariant polynomials."""

    terms: dict[Atom, sp.Expr]

    @staticmethod
    def zero() -> "FormalVector":
        return FormalVector({})

    @staticmethod
    def atom(atom: Atom, coeff: sp.Expr = sp.Integer(1)) -> "FormalVector":
        return FormalVector({atom: sp.sympify(coeff)})

    def simplify(self) -> "FormalVector":
        simplified = {
            atom: sp.expand(coeff)
            for atom, coeff in self.terms.items()
            if sp.expand(coeff) != 0
        }
        return FormalVector(dict(sorted(simplified.items())))

    def __add__(self, other: "FormalVector") -> "FormalVector":
        terms = dict(self.terms)
        for atom, coeff in other.terms.items():
            terms[atom] = terms.get(atom, sp.Integer(0)) + coeff
        return FormalVector(terms).simplify()

    def __sub__(self, other: "FormalVector") -> "FormalVector":
        return self + (-other)

    def __neg__(self) -> "FormalVector":
        return FormalVector({atom: -coeff for atom, coeff in self.terms.items()}).simplify()

    def scale(self, scalar: sp.Expr) -> "FormalVector":
        scalar = sp.sympify(scalar)
        return FormalVector({atom: scalar * coeff for atom, coeff in self.terms.items()}).simplify()

    def labels(self) -> dict[str, str]:
        return {atom.label(): str(coeff) for atom, coeff in self.terms.items()}


def invariant_symbol(i: int, j: int) -> sp.Symbol:
    """Return a canonical scalar product symbol I_i_j = <s_i, s_j>."""
    if i > j:
        i, j = j, i
    return sp.Symbol(f"I_{i}_{j}")


def _invariant_expr(i: int, j: int) -> sp.Expr:
    if i > j:
        i, j = j, i
    if i == 0 and j == 0:
        return sp.Integer(1)
    if i == 0:
        if j == 1:
            return sp.Integer(0)
        total = sp.Integer(0)
        for k in range(1, j):
            total += math.comb(j, k) * _invariant_expr(k, j - k)
        return sp.expand(-sp.Rational(1, 2) * total)
    return invariant_symbol(i, j)


def _invariant_symbols(exprs: Iterable[sp.Expr]) -> tuple[sp.Symbol, ...]:
    symbols: set[sp.Symbol] = set()
    for expr in exprs:
        symbols.update(
            symbol
            for symbol in sp.sympify(expr).free_symbols
            if symbol.name.startswith("I_")
        )
    return tuple(sorted(symbols, key=str))


def _d_scalar(expr: sp.Expr) -> sp.Expr:
    expr = sp.sympify(expr)
    result = sp.Integer(0)
    for symbol in sorted(expr.free_symbols, key=str):
        if not symbol.name.startswith("I_"):
            continue
        _, left, right = symbol.name.split("_")
        derivative = _invariant_expr(int(left) + 1, int(right)) + _invariant_expr(
            int(left), int(right) + 1
        )
        result += sp.diff(expr, symbol) * derivative
    return sp.expand(result)


def _canonical_cross(i: int, j: int) -> tuple[int, Atom | None]:
    if i == j:
        return 1, None
    if i < j:
        return 1, Atom("C", i, j)
    return -1, Atom("C", j, i)


def _d_atom(atom: Atom) -> FormalVector:
    if atom.kind == "S":
        return FormalVector.atom(Atom("S", atom.i + 1))
    left_sign, left = _canonical_cross(atom.i + 1, atom.j)
    right_sign, right = _canonical_cross(atom.i, atom.j + 1)
    out = FormalVector.zero()
    if left is not None:
        out += FormalVector.atom(left, left_sign)
    if right is not None:
        out += FormalVector.atom(right, right_sign)
    return out


def derivative(vector: FormalVector) -> FormalVector:
    """Apply D_x to a formal vector."""
    out = FormalVector.zero()
    for atom, coeff in vector.terms.items():
        out += FormalVector.atom(atom, _d_scalar(coeff))
        out += _d_atom(atom).scale(coeff)
    return out.simplify()


def cross_s(vector: FormalVector) -> FormalVector:
    """Apply s cross vector using unit-sphere reductions."""
    out = FormalVector.zero()
    for atom, coeff in vector.terms.items():
        if atom.kind == "S":
            sign, cross_atom = _canonical_cross(0, atom.i)
            if cross_atom is not None:
                out += FormalVector.atom(cross_atom, coeff * sign)
            continue
        i, j = atom.i, atom.j
        out += FormalVector.atom(Atom("S", i), coeff * _invariant_expr(0, j))
        out += FormalVector.atom(Atom("S", j), -coeff * _invariant_expr(0, i))
    return out.simplify()


def _order_from_key(key: str) -> int:
    if key == "s":
        return 0
    if re.fullmatch(r"sx+", key):
        return len(key) - 1
    raise ValueError(f"Unsupported derivative atom key: {key}")


def atom_from_key(key: str) -> Atom:
    """Parse an overnight vector-atom key into a formal atom."""
    if "_cross_" in key:
        left, right = key.split("_cross_", 1)
        sign, atom = _canonical_cross(_order_from_key(left), _order_from_key(right))
        if atom is None or sign < 0:
            raise ValueError(f"Unsupported cross atom key: {key}")
        return atom
    return Atom("S", _order_from_key(key))


def scalar_from_key(key: str) -> sp.Expr:
    """Parse an overnight scalar-factor key into a formal scalar expression."""
    if key == "unit":
        return sp.Integer(1)
    if key.startswith("ip_"):
        left, right = key.removeprefix("ip_").split("_", 1)
        return _invariant_expr(_order_from_key(left), _order_from_key(right))
    if key == "energy_12":
        return invariant_symbol(1, 1) + invariant_symbol(2, 2)
    if key == "energy_23":
        return invariant_symbol(2, 2) + invariant_symbol(3, 3)
    if key == "energy_34":
        return invariant_symbol(3, 3) + invariant_symbol(4, 4)
    if key == "mixed_energy_13":
        return invariant_symbol(1, 3) + invariant_symbol(2, 2)
    raise ValueError(f"Unsupported scalar factor key: {key}")


def target_from_candidate(candidate: OvernightCandidate) -> FormalVector:
    """Return the formal target flow for an overnight candidate."""
    scalar = scalar_from_key(candidate.scalar_factor)
    if "+" in candidate.vector_atom:
        left, right = candidate.vector_atom.split("+", 1)
        return cross_s(FormalVector.atom(atom_from_key(left), scalar)) + cross_s(
            FormalVector.atom(atom_from_key(right))
        )
    return cross_s(FormalVector.atom(atom_from_key(candidate.vector_atom), scalar))


def _basis_vectors(candidate: OvernightCandidate, max_order: int) -> tuple[FormalVector, ...]:
    atoms: set[Atom] = {Atom("S", 0)}
    for order in range(1, max_order + 1):
        atoms.add(Atom("S", order))
        atoms.add(Atom("C", 0, order))
    for part in candidate.vector_atom.split("+"):
        atom = atom_from_key(part)
        atoms.add(atom)
        if atom.kind == "C":
            atoms.add(Atom("S", atom.i))
            atoms.add(Atom("S", atom.j))
    scalar = scalar_from_key(candidate.scalar_factor)
    scalars = [sp.Integer(1)]
    if scalar != 1:
        scalars.append(scalar)
    vectors = []
    for scalar_expr in scalars:
        for atom in sorted(atoms):
            vectors.append(FormalVector.atom(atom, scalar_expr))
    return tuple(vectors)


@dataclass(frozen=True)
class FormalSphereAnsatzReport:
    """Result of a formal local-vector ansatz attempt."""

    candidate_name: str
    degree: int
    basis_size: int
    unknown_count: int
    equation_count: int
    solved: bool
    status: str
    solution: dict[str, str]
    residual_basis: dict[str, dict[str, str]]
    obstruction_basis: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "candidate_name": self.candidate_name,
            "degree": self.degree,
            "basis_size": self.basis_size,
            "unknown_count": self.unknown_count,
            "equation_count": self.equation_count,
            "solved": self.solved,
            "status": self.status,
            "solution": self.solution,
            "residual_basis": self.residual_basis,
            "obstruction_basis": list(self.obstruction_basis),
        }


def solve_formal_sphere_ansatz(
    candidate: OvernightCandidate,
    *,
    degree: int = 3,
    basis_order_slack: int = 1,
    max_unknowns: int = 220,
) -> FormalSphereAnsatzReport:
    """Attempt a formal local-vector ansatz for one sphere candidate.

    The ansatz keeps U = lambda*hat(s) and solves for a polynomial vector
    V = hat(sum lambda^k v_k). It is local and formal: scalar products are
    represented as invariant symbols with unit-sphere reductions for <s,s_k>.
    """
    target = target_from_candidate(candidate)
    basis = _basis_vectors(candidate, candidate.order + basis_order_slack)
    unknowns: list[sp.Symbol] = []
    vectors: dict[int, FormalVector] = {}
    for power in range(1, degree + 1):
        vector = FormalVector.zero()
        for index, basis_vector in enumerate(basis):
            unknown = sp.Symbol(f"c_{power}_{index}")
            unknowns.append(unknown)
            vector += basis_vector.scale(unknown)
        vectors[power] = vector

    if len(unknowns) > max_unknowns:
        return FormalSphereAnsatzReport(
            candidate_name=candidate.name,
            degree=degree,
            basis_size=len(basis),
            unknown_count=len(unknowns),
            equation_count=0,
            solved=False,
            status="skipped_too_many_unknowns",
            solution={},
            residual_basis={},
            obstruction_basis=(
                f"generated {len(unknowns)} unknowns, above configured limit {max_unknowns}",
            ),
        )

    residuals: dict[str, FormalVector] = {}
    zero = FormalVector.zero()
    vectors[0] = zero
    for power in range(0, degree + 2):
        current = zero
        if power == 1:
            current += target
        if power <= degree:
            current -= derivative(vectors[power])
        if power - 1 >= 0:
            current += cross_s(vectors.get(power - 1, zero))
        residuals[f"lambda^{power}"] = current.simplify()

    scalar_exprs = [
        coeff
        for residual in residuals.values()
        for coeff in residual.terms.values()
    ]
    invariant_symbols = _invariant_symbols(scalar_exprs)
    equations: list[sp.Expr] = []
    for expr in scalar_exprs:
        expanded = sp.expand(expr)
        if invariant_symbols:
            try:
                equations.extend(sp.Poly(expanded, *invariant_symbols).coeffs())
            except sp.PolynomialError:
                equations.append(expanded)
        else:
            equations.append(expanded)
    equations = [sp.expand(equation) for equation in equations if sp.expand(equation) != 0]
    solutions = sp.solve(equations, unknowns, dict=True, simplify=False)
    solution = dict(solutions[0]) if solutions else {}
    reduced = {
        power: FormalVector(
            {
                atom: sp.expand(coeff.subs(solution))
                for atom, coeff in residual.terms.items()
            }
        ).simplify()
        for power, residual in residuals.items()
    }
    solved = bool(solution) and all(not residual.terms for residual in reduced.values())
    nonzero = {
        power: residual.labels()
        for power, residual in reduced.items()
        if residual.terms
    }
    if solved:
        status = "validated_formal_zcr_candidate"
        obstruction_basis = ()
    elif solution:
        status = "residuals_remain_after_formal_solve"
        obstruction_basis = tuple(f"{power}: {labels}" for power, labels in nonzero.items())
    else:
        status = "no_formal_solution"
        obstruction_basis = tuple(f"{power}: {labels}" for power, labels in nonzero.items())

    return FormalSphereAnsatzReport(
        candidate_name=candidate.name,
        degree=degree,
        basis_size=len(basis),
        unknown_count=len(unknowns),
        equation_count=len(equations),
        solved=solved,
        status=status,
        solution={str(key): str(value) for key, value in solution.items()},
        residual_basis=nonzero,
        obstruction_basis=obstruction_basis[:20],
    )
