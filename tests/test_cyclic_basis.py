import sympy as sp

from laxforge.core.cyclic_basis import compute_cyclic_basis, covariant_derivative


def test_covariant_derivative_uses_commutator_sign_convention():
    x, t, lam = sp.symbols("x t lambda")
    u = sp.Function("u")(x, t)
    X = sp.Matrix([[lam, u], [0, -lam]])
    C = sp.Matrix([[0, 1], [0, 0]])

    nabla_c = covariant_derivative(X, C, x)

    assert sp.simplify(nabla_c[0, 1] + 2 * lam) == 0


def test_cyclic_basis_fingerprint_detects_lambda_dependent_closure():
    x, t, lam = sp.symbols("x t lambda")
    u = sp.Function("u")(x, t)
    X = sp.Matrix([[lam, u], [0, -lam]])

    report = compute_cyclic_basis(X, u, x, lambda_symbol=lam)

    assert report.basis_dimension == 1
    assert report.lambda_dependent_coefficients
    assert sp.simplify(report.closure_coefficients["c0"] + 2 * lam) == 0
    assert "dim=1" in report.fingerprint
