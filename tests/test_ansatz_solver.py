import sympy as sp

from laxforge.core.ansatz import (
    WeightSpec,
    generate_homogeneous_monomials,
    polynomial_lambda_matrix_ansatz,
)
from laxforge.core.solver import recover_scalar_mkdv_v_coefficients


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
