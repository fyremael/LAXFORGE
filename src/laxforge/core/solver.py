"""Linear symbolic solver helpers for small zero-curvature ansatzes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

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


@dataclass(frozen=True)
class ConstraintSolveConfig:
    """Safety limits for symbolic constraint solving."""

    max_equations: int = 64
    max_unknowns: int = 16
    groebner_max_equations: int = 8
    groebner_max_unknowns: int = 4
    allow_nonlinear: bool = True
    allow_groebner: bool = True


@dataclass(frozen=True)
class ConstraintSolveReport:
    """Serializable strategy-based symbolic solve result."""

    unknowns: tuple[sp.Symbol, ...]
    equations: tuple[sp.Expr, ...]
    solution: dict[sp.Symbol, sp.Expr]
    residuals: tuple[sp.Expr, ...]
    solved: bool
    status: str
    strategy: str

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible solve summary."""
        return {
            "unknowns": [str(unknown) for unknown in self.unknowns],
            "equations": [str(equation) for equation in self.equations],
            "solution": {str(key): str(value) for key, value in self.solution.items()},
            "residuals": [str(residual) for residual in self.residuals],
            "solved": self.solved,
            "status": self.status,
            "strategy": self.strategy,
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


def _is_linear_in_unknowns(expr: sp.Expr, unknowns: Sequence[sp.Symbol]) -> bool:
    try:
        poly = sp.Poly(sp.expand(expr), *unknowns)
    except sp.PolynomialError:
        return False
    return poly.total_degree() <= 1


def _residuals(
    equations: Sequence[sp.Expr], solution: Mapping[sp.Symbol, sp.Expr]
) -> tuple[sp.Expr, ...]:
    return tuple(sp.simplify(equation.subs(solution)) for equation in equations)


def _report_from_solution(
    *,
    equations: tuple[sp.Expr, ...],
    unknowns: tuple[sp.Symbol, ...],
    solutions: list[dict[sp.Symbol, sp.Expr]],
    strategy: str,
) -> ConstraintSolveReport | None:
    if not solutions:
        return None
    solution = dict(solutions[0])
    residuals = _residuals(equations, solution)
    solved = all(residual == 0 for residual in residuals)
    return ConstraintSolveReport(
        unknowns=unknowns,
        equations=equations,
        solution=solution,
        residuals=residuals,
        solved=solved,
        status="solved" if solved else "residuals_remain",
        strategy=strategy,
    )


def solve_symbolic_constraints(
    equations: Sequence[sp.Expr],
    unknowns: Sequence[sp.Symbol],
    config: ConstraintSolveConfig | None = None,
) -> ConstraintSolveReport:
    """Solve constraints with linear, nonlinear, then bounded Gröbner strategies."""
    config = config or ConstraintSolveConfig()
    unknowns_tuple = tuple(unknowns)
    simplified = tuple(sp.simplify(equation) for equation in equations)
    nonzero = tuple(equation for equation in simplified if equation != 0)

    if len(nonzero) > config.max_equations or len(unknowns_tuple) > config.max_unknowns:
        return ConstraintSolveReport(
            unknowns=unknowns_tuple,
            equations=simplified,
            solution={},
            residuals=nonzero,
            solved=False,
            status="skipped_size_limit",
            strategy="size_guard",
        )
    if not nonzero:
        return ConstraintSolveReport(
            unknowns=unknowns_tuple,
            equations=simplified,
            solution={},
            residuals=(),
            solved=True,
            status="solved",
            strategy="empty_system",
        )
    if all(_is_linear_in_unknowns(equation, unknowns_tuple) for equation in nonzero):
        linear = solve_linear_constraints(nonzero, unknowns_tuple)
        if linear.solved:
            return ConstraintSolveReport(
                unknowns=linear.unknowns,
                equations=simplified,
                solution=linear.solution,
                residuals=linear.residuals,
                solved=True,
                status="solved",
                strategy="linear",
            )

    if config.allow_nonlinear:
        try:
            nonlinear = sp.solve(nonzero, unknowns_tuple, dict=True, simplify=True)
        except (NotImplementedError, TypeError, ValueError):
            nonlinear = []
        nonlinear_report = _report_from_solution(
            equations=simplified,
            unknowns=unknowns_tuple,
            solutions=nonlinear,
            strategy="nonlinear",
        )
        if nonlinear_report and nonlinear_report.solved:
            return nonlinear_report

    if (
        config.allow_groebner
        and len(nonzero) <= config.groebner_max_equations
        and len(unknowns_tuple) <= config.groebner_max_unknowns
    ):
        try:
            basis = sp.groebner(nonzero, *unknowns_tuple)
            if len(basis.polys) == 1 and sp.simplify(basis.polys[0].as_expr() - 1) == 0:
                return ConstraintSolveReport(
                    unknowns=unknowns_tuple,
                    equations=simplified,
                    solution={},
                    residuals=nonzero,
                    solved=False,
                    status="no_solution",
                    strategy="groebner",
                )
            groebner_solutions = sp.solve([poly.as_expr() for poly in basis.polys], unknowns_tuple, dict=True)
        except (sp.PolynomialError, NotImplementedError, TypeError, ValueError):
            groebner_solutions = []
        groebner_report = _report_from_solution(
            equations=simplified,
            unknowns=unknowns_tuple,
            solutions=groebner_solutions,
            strategy="groebner",
        )
        if groebner_report and groebner_report.solved:
            return groebner_report

    return ConstraintSolveReport(
        unknowns=unknowns_tuple,
        equations=simplified,
        solution={},
        residuals=nonzero,
        solved=False,
        status="no_solution",
        strategy="exhausted",
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
