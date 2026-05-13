import sympy as sp

from laxforge.core.conservation import inherited_mkdv_conservation_laws
from laxforge.core.hamiltonian import (
    DX,
    is_skew_adjoint_operator,
    mkdv_second_jet_hamiltonian_report,
    variational_derivative,
)


def test_variational_derivative_for_simple_density():
    x, t = sp.symbols("x t")
    u = sp.Function("u")(x, t)
    density = sp.Rational(1, 2) * sp.diff(u, x) ** 2 - sp.Rational(1, 2) * u**4

    derivative = variational_derivative(density, u, x)

    assert sp.simplify(derivative + sp.diff(u, x, 2) + 2 * u**3) == 0


def test_dx_operator_matrix_is_skew_adjoint_when_symmetric():
    operator = ((None, DX), (DX, None))

    assert is_skew_adjoint_operator(operator)


def test_second_jet_mkdv_hamiltonian_representation_verifies():
    x, t = sp.symbols("x t")
    report = mkdv_second_jet_hamiltonian_report(x, t)

    assert report.operator_skew_adjoint
    assert report.verified


def test_inherited_conservation_law_expansion_returns_at_least_three_laws():
    x, t = sp.symbols("x t")
    laws = inherited_mkdv_conservation_laws(x, t)

    assert len(laws) >= 3
    assert laws[0].name == "Q:eps^0"
