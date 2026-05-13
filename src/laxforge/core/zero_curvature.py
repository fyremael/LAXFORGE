"""Zero-curvature utilities."""

from __future__ import annotations

import sympy as sp

from laxforge.algebra.truncated_poly import (
    TruncatedPoly,
    tp_matrix_add,
    tp_matrix_commutator,
    tp_matrix_diff,
    tp_matrix_sub,
)
from laxforge.core.reports import (
    CurvatureProofArtifact,
    CurvatureReport,
    build_curvature_proof_artifact,
    build_curvature_report,
)


def zero_curvature(
    U: list[list[TruncatedPoly]], V: list[list[TruncatedPoly]], x: sp.Symbol, t: sp.Symbol
) -> list[list[TruncatedPoly]]:
    """Compute U_t - V_x + [U,V]."""
    return tp_matrix_add(tp_matrix_sub(tp_matrix_diff(U, t), tp_matrix_diff(V, x)), tp_matrix_commutator(U, V))


def matrix_is_zero(mat: list[list[TruncatedPoly]]) -> bool:
    return all(entry.simplify().is_zero() for row in mat for entry in row)


def coefficient_report(mat: list[list[TruncatedPoly]]) -> dict[str, list[sp.Expr]]:
    """Return simplified coefficients for each matrix entry."""
    report: dict[str, list[sp.Expr]] = {}
    for i, row in enumerate(mat):
        for j, entry in enumerate(row):
            report[f"({i},{j})"] = [sp.simplify(c) for c in entry.coeffs]
    return report


def curvature_report(mat: list[list[TruncatedPoly]]) -> CurvatureReport:
    """Return a structured coefficient-splitting report for a curvature matrix."""
    return build_curvature_report(mat)


def markdown_curvature_report(mat: list[list[TruncatedPoly]]) -> str:
    """Return a Markdown coefficient-splitting report for a curvature matrix."""
    return curvature_report(mat).to_markdown()


def curvature_proof_artifact(
    mat: list[list[TruncatedPoly]], title: str = "Curvature Proof"
) -> CurvatureProofArtifact:
    """Return a Markdown-ready proof artifact for a curvature matrix."""
    return build_curvature_proof_artifact(mat, title=title)
