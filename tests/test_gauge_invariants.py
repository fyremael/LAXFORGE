import sympy as sp

from laxforge.core.gauge import (
    analyze_gauge_risk,
    detect_block_reducibility,
    gauge_transform,
    matrix_is_zero,
    spectral_parameter_removal_heuristic,
    zero_curvature_matrix,
)
from laxforge.core.invariants import matrix_pair_invariants


def test_gauge_transform_preserves_curvature_for_commuting_diagonal_pair():
    x, t = sp.symbols("x t")
    a = sp.Function("a")(x, t)
    b = sp.Function("b")(x, t)
    phi = sp.Function("phi")(x, t)
    U = sp.diag(a, -a)
    V = sp.diag(b, -b)
    G = sp.diag(sp.exp(phi), sp.exp(-phi))

    transformed_U, transformed_V = gauge_transform(U, V, G, x, t)
    transformed_curvature = zero_curvature_matrix(transformed_U, transformed_V, x, t)
    expected_curvature = sp.simplify(G * zero_curvature_matrix(U, V, x, t) * G.inv())

    assert matrix_is_zero(sp.simplify(transformed_curvature - expected_curvature))


def test_detects_direct_block_sum_reducibility():
    U = sp.diag(1, 2)
    V = sp.diag(3, 4)

    report = detect_block_reducibility((U, V))

    assert report.block_reducible
    assert report.split_index == 1


def test_flags_fake_scalar_identity_lambda():
    lam = sp.Symbol("lambda")
    U = lam * sp.eye(2)
    V = sp.zeros(2)

    report = spectral_parameter_removal_heuristic(U, V, lam)

    assert report.lambda_present
    assert report.removable
    assert report.status == "fake_scalar_identity_lambda"


def test_gauge_risk_report_never_claims_novelty():
    lam = sp.Symbol("lambda")
    report = analyze_gauge_risk(lam * sp.eye(2), sp.zeros(2), lambda_symbol=lam)

    assert report.gauge_risk_score > 0
    assert report.novelty_status == "unassessed"


def test_matrix_pair_invariant_fingerprint_is_stable():
    lam = sp.Symbol("lambda")
    U = sp.diag(lam, -lam)
    V = sp.zeros(2)

    report = matrix_pair_invariants((U, V), lambda_symbol=lam)

    assert report.traces == (0, 0)
    assert report.block_reducible
    assert report.spectral_parameter_present
    assert "lambda=True" in report.fingerprint
