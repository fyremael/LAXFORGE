"""Linear symbolic solver helpers for small zero-curvature ansatzes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import sympy as sp

from laxforge.algebra.truncated_poly import TruncatedPoly
from laxforge.core.zero_curvature import zero_curvature


@dataclass(frozen=True)
class LinearSolveReport:
    """Serializable summary of a linear symbolic solve."""

    unknowns: tuple[sp.Symbol, ...]
    equations: tuple[sp.Expr, ...]
    solution: dict[sp.Symbol, sp.Expr]
    residuals: tuple[sp.Expr, ...]
    solved: bool
    status: str

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible solve summary."""
        return {
            "unknowns": [str(unknown) for unknown in self.unknowns],
            "equations": [str(equation) for equation in self.equations],
            "solution": {str(key): str(value) for key, value in self.solution.items()},
            "residuals": [str(residual) for residual in self.residuals],
            "solved": self.solved,
            "status": self.status,
        }


def split_polynomial_coefficients(
    expr: sp.Expr, polynomial_symbols: Sequence[sp.Symbol]
) -> tuple[sp.Expr, ...]:
    """Split an expression into polynomial coefficients when possible."""
    expr = sp.expand(expr)
    if not polynomial_symbols:
        return (sp.simplify(expr),)
    try:
        poly = sp.Poly(expr, *polynomial_symbols)
    except sp.PolynomialError:
        return (sp.simplify(expr),)
    return tuple(sp.simplify(coeff) for coeff in poly.coeffs())


def split_truncated_matrix_constraints(
    mat: list[list[TruncatedPoly]], polynomial_symbols: Sequence[sp.Symbol] = ()
) -> tuple[sp.Expr, ...]:
    """Split a truncated-polynomial matrix into scalar symbolic constraints."""
    constraints: list[sp.Expr] = []
    for row in mat:
        for entry in row:
            for coeff in entry.coeffs:
                constraints.extend(split_polynomial_coefficients(coeff, polynomial_symbols))
    return tuple(sp.simplify(constraint) for constraint in constraints)


def solve_linear_constraints(
    equations: Sequence[sp.Expr], unknowns: Sequence[sp.Symbol]
) -> LinearSolveReport:
    """Solve equations that are expected to be linear in the given unknowns."""
    simplified_equations = tuple(sp.simplify(equation) for equation in equations)
    nonzero_equations = tuple(equation for equation in simplified_equations if equation != 0)
    solutions = sp.solve(nonzero_equations, tuple(unknowns), dict=True, simplify=True)
    if not solutions:
        return LinearSolveReport(
            unknowns=tuple(unknowns),
            equations=simplified_equations,
            solution={},
            residuals=nonzero_equations,
            solved=False,
            status="no_solution",
        )

    solution = dict(solutions[0])
    residuals = tuple(sp.simplify(equation.subs(solution)) for equation in simplified_equations)
    solved = all(residual == 0 for residual in residuals)
    return LinearSolveReport(
        unknowns=tuple(unknowns),
        equations=simplified_equations,
        solution=solution,
        residuals=residuals,
        solved=solved,
        status="solved" if solved else "residuals_remain",
    )


def recover_scalar_mkdv_v_coefficients() -> LinearSolveReport:
    """Recover the scalar mKdV AKNS V coefficients from a fixed U template."""
    x, t, lam = sp.symbols("x t lambda")
    q = sp.Function("q")(x, t)
    q_tp = TruncatedPoly.from_coeffs([q], order=1)
    lam_tp = TruncatedPoly.from_coeffs([lam], order=1)

    a0, a1, b0, b1, b2, b3, c0, c1, c2, c3 = sp.symbols(
        "a0 a1 b0 b1 b2 b3 c0 c1 c2 c3"
    )
    qx = q_tp.diff(x)
    qxx = qx.diff(x)
    q2 = q_tp**2
    q3 = q_tp**3

    a_entry = a0 * lam**3 + a1 * lam * q2
    b_entry = b0 * lam**2 * q_tp + b1 * lam * qx + b2 * qxx + b3 * q3
    c_entry = c0 * lam**2 * q_tp + c1 * lam * qx + c2 * qxx + c3 * q3

    U = [[lam_tp, q_tp], [-q_tp, -lam_tp]]
    V = [[a_entry, b_entry], [c_entry, -a_entry]]
    curvature = zero_curvature(U, V, x, t)
    expected = sp.diff(q, t) + sp.diff(q, x, 3) + 6 * q**2 * sp.diff(q, x)

    scalar_constraints = [
        curvature[0][0].coeffs[0],
        curvature[1][1].coeffs[0],
        curvature[0][1].coeffs[0] - expected,
        curvature[1][0].coeffs[0] + expected,
    ]
    q0, q1, q2, q3, qt = sp.symbols("q0 q1 q2 q3 qt")
    jet_substitutions = {
        q: q0,
        sp.diff(q, x): q1,
        sp.diff(q, x, 2): q2,
        sp.diff(q, x, 3): q3,
        sp.diff(q, t): qt,
    }
    polynomial_symbols = (lam, q0, q1, q2, q3, qt)
    equations: list[sp.Expr] = []
    for constraint in scalar_constraints:
        polynomial_constraint = sp.expand(constraint.xreplace(jet_substitutions))
        equations.extend(split_polynomial_coefficients(polynomial_constraint, polynomial_symbols))

    unknowns = (a0, a1, b0, b1, b2, b3, c0, c1, c2, c3)
    return solve_linear_constraints(equations, unknowns)
