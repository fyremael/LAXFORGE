"""Second-jet nilpotent mKdV calibration example."""

from __future__ import annotations

import sympy as sp

from laxforge.algebra.truncated_poly import TruncatedPoly
from laxforge.core.zero_curvature import coefficient_report, curvature_report, zero_curvature


def build_pair(order: int = 3):
    """Build the algebra-valued AKNS/mKdV Lax pair over R[eps]/(eps^3)."""
    x, t, lam = sp.symbols("x t lambda")
    u = sp.Function("u")(x, t)
    v = sp.Function("v")(x, t)
    w = sp.Function("w")(x, t)

    Q = TruncatedPoly.from_coeffs([u, v, w], order=order)
    lam_tp = TruncatedPoly.from_coeffs([lam], order=order)
    minus_lam_tp = TruncatedPoly.from_coeffs([-lam], order=order)

    Qx = Q.diff(x)
    Qxx = Qx.diff(x)
    Q2 = Q**2
    Q3 = Q**3

    A = (-4 * lam**3) + (-2 * lam) * Q2
    B = (-4 * lam**2) * Q + (-2 * lam) * Qx - Qxx - 2 * Q3
    C = (4 * lam**2) * Q + (-2 * lam) * Qx + Qxx + 2 * Q3

    U = [[lam_tp, Q], [-Q, minus_lam_tp]]
    V = [[A, B], [C, -A]]
    return x, t, lam, (u, v, w), U, V


def expected_flow_components(x: sp.Symbol, t: sp.Symbol):
    u = sp.Function("u")(x, t)
    v = sp.Function("v")(x, t)
    w = sp.Function("w")(x, t)
    f0 = sp.diff(u, t) + sp.diff(u, x, 3) + 6 * u**2 * sp.diff(u, x)
    f1 = sp.diff(v, t) + sp.diff(v, x, 3) + 6 * u**2 * sp.diff(v, x) + 12 * u * sp.diff(u, x) * v
    f2 = (
        sp.diff(w, t)
        + sp.diff(w, x, 3)
        + 6 * u**2 * sp.diff(w, x)
        + 12 * u * v * sp.diff(v, x)
        + 6 * v**2 * sp.diff(u, x)
        + 12 * u * w * sp.diff(u, x)
    )
    return [sp.simplify(f0), sp.simplify(f1), sp.simplify(f2)]


def validate() -> dict[str, object]:
    x, t, _lam, _fields, U, V = build_pair(order=3)
    F = zero_curvature(U, V, x, t)
    report = coefficient_report(F)
    structured_report = curvature_report(F)
    expected = expected_flow_components(x, t)

    upper_right = [sp.simplify(c) for c in report["(0,1)"]]
    lower_left = [sp.simplify(c) for c in report["(1,0)"]]
    diag_00 = [sp.simplify(c) for c in report["(0,0)"]]
    diag_11 = [sp.simplify(c) for c in report["(1,1)"]]

    checks = {
        "diag_00_zero": all(sp.simplify(c) == 0 for c in diag_00),
        "diag_11_zero": all(sp.simplify(c) == 0 for c in diag_11),
        "upper_right_expected": all(sp.simplify(a - b) == 0 for a, b in zip(upper_right, expected)),
        "lower_left_negative_expected": all(sp.simplify(a + b) == 0 for a, b in zip(lower_left, expected)),
    }

    return {
        "checks": checks,
        "curvature_coefficients": report,
        "curvature_report": structured_report,
        "expected_flow_coefficients": expected,
    }
