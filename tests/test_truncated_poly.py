import pytest
import sympy as sp

from laxforge.algebra.truncated_poly import (
    TruncatedPoly,
    tp_matrix_add,
    tp_matrix_commutator,
    tp_matrix_mul,
)


def assert_tp_zero(poly: TruncatedPoly) -> None:
    assert poly.simplify().is_zero()


def test_multiplication_is_associative():
    x = sp.Symbol("x")
    a = TruncatedPoly.from_coeffs([1, x, x**2])
    b = TruncatedPoly.from_coeffs([x - 1, 2, 3])
    c = TruncatedPoly.from_coeffs([2, x + 1, x])

    assert_tp_zero((a * b) * c - a * (b * c))


def test_multiplication_distributes_over_addition():
    x = sp.Symbol("x")
    a = TruncatedPoly.from_coeffs([x, 1, 0])
    b = TruncatedPoly.from_coeffs([2, x, 1])
    c = TruncatedPoly.from_coeffs([1, x**2, x])

    assert_tp_zero(a * (b + c) - (a * b + a * c))


def test_eps_power_at_order_is_zero():
    eps = TruncatedPoly.from_coeffs([0, 1, 0], order=3)

    assert not (eps**2).is_zero()
    assert (eps**3).is_zero()


def test_derivative_acts_componentwise():
    x, t = sp.symbols("x t")
    u = sp.Function("u")(x, t)
    v = sp.Function("v")(x, t)
    poly = TruncatedPoly.from_coeffs([u**2, v, x * t])

    derivative = poly.diff(x)

    assert derivative.coeffs == (
        sp.diff(u**2, x),
        sp.diff(v, x),
        t,
    )


def test_matrix_commutator_is_zero_for_identical_matrices():
    x = sp.Symbol("x")
    a = TruncatedPoly.from_coeffs([1, x, 0])
    b = TruncatedPoly.from_coeffs([x, 0, 1])
    c = TruncatedPoly.from_coeffs([0, x**2, 1])
    d = TruncatedPoly.from_coeffs([2, 0, x])
    matrix = [[a, b], [c, d]]

    commutator = tp_matrix_commutator(matrix, matrix)

    for row in commutator:
        for entry in row:
            assert_tp_zero(entry)


def test_rejects_mixed_polynomial_orders_and_basis_symbols():
    eps_poly = TruncatedPoly.from_coeffs([1, 2, 3], order=3, symbol_name="eps")
    eta_poly = TruncatedPoly.from_coeffs([1, 2, 3], order=3, symbol_name="eta")
    order_four_poly = TruncatedPoly.from_coeffs([1, 2, 3, 4], order=4)

    with pytest.raises(ValueError, match="orders"):
        _ = eps_poly + order_four_poly
    with pytest.raises(ValueError, match="basis symbols"):
        _ = eps_poly + eta_poly


def test_matrix_operations_reject_shape_mismatch():
    one = TruncatedPoly.one()
    zero = TruncatedPoly.zero()

    with pytest.raises(ValueError, match="shapes"):
        tp_matrix_add([[one, zero]], [[one], [zero]])

    with pytest.raises(ValueError, match="incompatible"):
        tp_matrix_mul([[one, zero]], [[one, zero]])
