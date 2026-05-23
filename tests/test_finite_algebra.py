import pytest
import sympy as sp

from laxforge.algebra.finite import (
    FiniteAlgebraElement,
    FiniteAlgebraSpec,
    fa_matrix_add,
    fa_matrix_commutator,
    fa_matrix_mul,
    fa_zero_curvature,
    upper_triangular_semidirect_algebra,
)
from laxforge.core.reports import build_curvature_report


def assert_fa_zero(element: FiniteAlgebraElement) -> None:
    assert element.simplify().is_zero()


def test_upper_triangular_semidirect_algebra_records_non_split_product():
    algebra = upper_triangular_semidirect_algebra()

    assert algebra.is_associative()
    assert algebra.product_table()["p"]["n"] == "n"
    assert algebra.product_table()["n"]["p"] == "0"


def test_finite_algebra_multiplication_is_associative_and_noncommutative():
    algebra = upper_triangular_semidirect_algebra()
    x = sp.Symbol("x")
    a = FiniteAlgebraElement.from_coeffs([1, x, 2], algebra)
    b = FiniteAlgebraElement.from_coeffs([0, 1, x], algebra)
    c = FiniteAlgebraElement.from_coeffs([x, 0, 1], algebra)
    p = FiniteAlgebraElement.from_coeffs([0, 1, 0], algebra)
    n = FiniteAlgebraElement.from_coeffs([0, 0, 1], algebra)

    assert_fa_zero((a * b) * c - a * (b * c))
    assert not (p * n - n * p).is_zero()
    assert (p * n).coefficient("n") == 1
    assert (n * p).is_zero()


def test_finite_algebra_derivative_and_matrix_commutator():
    algebra = upper_triangular_semidirect_algebra()
    x, t = sp.symbols("x t")
    u = sp.Function("u")(x, t)
    p = FiniteAlgebraElement.from_coeffs([0, u, x * t], algebra)
    zero = FiniteAlgebraElement.zero(algebra)
    matrix = [[p, zero], [zero, -p]]

    derivative = p.diff(x)
    commutator = fa_matrix_commutator(matrix, matrix)

    assert derivative.coeffs == (0, sp.diff(u, x), t)
    for row in commutator:
        for entry in row:
            assert_fa_zero(entry)


def test_finite_matrix_operations_reject_shape_and_basis_mismatch():
    algebra = upper_triangular_semidirect_algebra()
    one = FiniteAlgebraElement.one(algebra)
    zero = FiniteAlgebraElement.zero(algebra)
    other = FiniteAlgebraElement.from_coeffs(
        [1],
        FiniteAlgebraSpec.from_products(
            name="scalar",
            basis=("1",),
            products={},
        ),
    )

    with pytest.raises(ValueError, match="shapes"):
        fa_matrix_add([[one, zero]], [[one], [zero]])
    with pytest.raises(ValueError, match="incompatible"):
        fa_matrix_mul([[one, zero]], [[one, zero]])
    with pytest.raises(ValueError, match="finite coefficient algebra"):
        fa_matrix_add([[one]], [[other]])


def test_curvature_report_splits_finite_algebra_basis():
    algebra = upper_triangular_semidirect_algebra()
    x, t = sp.symbols("x t")
    u = sp.Function("u")(x, t)
    q = FiniteAlgebraElement.from_coeffs([0, u, 0], algebra)
    zero = FiniteAlgebraElement.zero(algebra)

    report = build_curvature_report(fa_zero_curvature([[q]], [[zero]], x, t))

    assert report.coefficient_basis == ("1", "p", "n")
    assert report.curvature_terms_total == 3
    assert report.curvature_terms_nonzero == 1
    assert report.entries["(0,0)"].simplified_coefficients[1] == sp.diff(u, t)
