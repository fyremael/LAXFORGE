import sympy as sp

from laxforge.core.conservation import (
    inherited_mkdv_conservation_laws,
    inherited_mkdv_conservation_report,
    open_conservation_report,
)
from laxforge.core.hamiltonian import (
    DX,
    compatibility_attempt_report,
    is_skew_adjoint_operator,
    mkdv_second_jet_hamiltonian_report,
    open_hamiltonian_report,
    simple_constant_operator_jacobi_check,
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


def test_conservation_report_records_method_level_evidence():
    x, t = sp.symbols("x t")
    report = inherited_mkdv_conservation_report(x, t)
    model = report.complete_model()

    assert model.status == "inherited_hierarchy_evidence"
    assert "inherited_scalar_hierarchy" in model.method_evidence
    assert model.method_evidence["trace_monodromy"].status == "open"
    assert model.num_conservation_laws_found >= 3


def test_open_conservation_and_hamiltonian_reports_are_explicit():
    conservation = open_conservation_report("no matrix pair")
    hamiltonian = open_hamiltonian_report("no variational form")

    assert conservation.complete_model().status == "open_gate"
    assert hamiltonian["status"] == "open_gate"
    assert not hamiltonian["verified"]


def test_constant_poisson_jacobi_and_compatibility_attempts_are_structured():
    operator = ((None, DX), (DX, None))
    jacobi = simple_constant_operator_jacobi_check(operator)
    compatibility = compatibility_attempt_report(operator)

    assert jacobi is True
    assert compatibility["status"] == "open_gate"
