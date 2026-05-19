import sympy as sp

from laxforge.core.ansatz import (
    WeightSpec,
    generate_homogeneous_monomials,
    polynomial_lambda_matrix_ansatz,
)
from laxforge.core.solver import (
    ConstraintSolveConfig,
    recover_scalar_mkdv_v_coefficients,
    solve_symbolic_constraints,
)


def test_homogeneous_monomials_include_expected_differential_terms():
    x, t = sp.symbols("x t")
    u = sp.Function("u")(x, t)
    spec = WeightSpec({"u": 1}, derivative_weight=1)

    monomials = generate_homogeneous_monomials(
        fields=(u,),
        x=x,
        spec=spec,
        total_weight=3,
        max_derivative_order=2,
    )

    assert u**3 in monomials
    assert sp.diff(u, x, 2) in monomials
    assert u * sp.diff(u, x) in monomials


def test_polynomial_lambda_matrix_ansatz_shape_and_coefficients():
    lam = sp.Symbol("lambda")
    ansatz = polynomial_lambda_matrix_ansatz(2, 2, lam, degree=2, coefficient_prefix="p")

    assert len(ansatz.matrix) == 2
    assert len(ansatz.matrix[0]) == 2
    assert len(ansatz.coefficients) == 12
    assert ansatz.matrix[0][0].coeffs[0].has(lam)


def test_scalar_mkdv_v_coefficients_are_recovered_as_constants():
    report = recover_scalar_mkdv_v_coefficients()

    assert report.solved
    assert report.solution == {
        sp.Symbol("a0"): -4,
        sp.Symbol("a1"): -2,
        sp.Symbol("b0"): -4,
        sp.Symbol("b1"): -2,
        sp.Symbol("b2"): -1,
        sp.Symbol("b3"): -2,
        sp.Symbol("c0"): 4,
        sp.Symbol("c1"): -2,
        sp.Symbol("c2"): 1,
        sp.Symbol("c3"): 2,
    }


def test_strategy_solver_handles_linear_constraints():
    a = sp.Symbol("a")

    report = solve_symbolic_constraints([a - 2], [a])

    assert report.solved
    assert report.status == "solved"
    assert report.strategy == "linear"
    assert report.solution[a] == 2


def test_strategy_solver_handles_nonlinear_constraints():
    x = sp.Symbol("x")

    report = solve_symbolic_constraints([x**2 - 4], [x])

    assert report.solved
    assert report.strategy == "nonlinear"
    assert sp.simplify(report.residuals[0]) == 0


def test_strategy_solver_uses_groebner_when_requested():
    x, y = sp.symbols("x y")

    report = solve_symbolic_constraints(
        [x**2 - y, y - 1],
        [x, y],
        ConstraintSolveConfig(allow_nonlinear=False),
    )

    assert report.solved
    assert report.strategy == "groebner"
    assert all(sp.simplify(residual) == 0 for residual in report.residuals)


def test_strategy_solver_reports_no_solution_and_size_limits():
    x = sp.Symbol("x")

    impossible = solve_symbolic_constraints([x, x - 1], [x])
    too_large = solve_symbolic_constraints(
        [x, x - 1],
        [x],
        ConstraintSolveConfig(max_equations=1),
    )

    assert impossible.status == "no_solution"
    assert not impossible.solved
    assert too_large.status == "skipped_size_limit"
