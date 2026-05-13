"""Gauge transformation and risk-report helpers for explicit matrix pairs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import sympy as sp


@dataclass(frozen=True)
class BlockReducibilityReport:
    """Conservative block-reducibility result for explicit matrices."""

    block_reducible: bool
    split_index: int | None
    reason: str

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible block-reducibility summary."""
        return {
            "block_reducible": self.block_reducible,
            "split_index": self.split_index,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class SpectralParameterReport:
    """Restricted spectral-parameter removal heuristic result."""

    lambda_symbol: str
    lambda_present: bool
    removable: bool | None
    status: str
    reason: str

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible spectral-parameter summary."""
        return {
            "lambda_symbol": self.lambda_symbol,
            "lambda_present": self.lambda_present,
            "removable": self.removable,
            "status": self.status,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class GaugeReport:
    """Gauge-risk report; never certifies novelty."""

    block_report: BlockReducibilityReport
    spectral_report: SpectralParameterReport | None
    gauge_risk_score: float
    novelty_status: str = "unassessed"

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible gauge report."""
        return {
            "block_report": self.block_report.as_dict(),
            "spectral_report": self.spectral_report.as_dict() if self.spectral_report else None,
            "gauge_risk_score": self.gauge_risk_score,
            "novelty_status": self.novelty_status,
        }


def as_matrix(matrix: sp.MatrixBase | Sequence[Sequence[sp.Expr]]) -> sp.Matrix:
    """Convert an explicit matrix-like object to a SymPy Matrix."""
    return matrix if isinstance(matrix, sp.MatrixBase) else sp.Matrix(matrix)


def matrix_commutator(a: sp.MatrixBase, b: sp.MatrixBase) -> sp.Matrix:
    """Return the matrix commutator [a,b]."""
    return sp.simplify(a * b - b * a)


def matrix_derivative(matrix: sp.MatrixBase, var: sp.Symbol) -> sp.Matrix:
    """Differentiate every matrix entry with respect to one variable."""
    return matrix.applyfunc(lambda entry: sp.diff(entry, var))


def zero_curvature_matrix(
    U: sp.MatrixBase, V: sp.MatrixBase, x: sp.Symbol, t: sp.Symbol
) -> sp.Matrix:
    """Compute U_t - V_x + [U,V] for explicit SymPy matrices."""
    return sp.simplify(matrix_derivative(U, t) - matrix_derivative(V, x) + matrix_commutator(U, V))


def matrix_is_zero(matrix: sp.MatrixBase) -> bool:
    """Return whether every explicit matrix entry simplifies to zero."""
    return all(sp.simplify(entry) == 0 for entry in matrix)


def gauge_transform(
    U: sp.MatrixBase, V: sp.MatrixBase, G: sp.MatrixBase, x: sp.Symbol, t: sp.Symbol
) -> tuple[sp.Matrix, sp.Matrix]:
    """Apply U -> GUG^-1 + G_xG^-1 and V -> GVG^-1 + G_tG^-1."""
    G_inv = sp.simplify(G.inv())
    transformed_U = sp.simplify(G * U * G_inv + matrix_derivative(G, x) * G_inv)
    transformed_V = sp.simplify(G * V * G_inv + matrix_derivative(G, t) * G_inv)
    return transformed_U, transformed_V


def detect_block_reducibility(matrices: Sequence[sp.MatrixBase]) -> BlockReducibilityReport:
    """Detect an explicit common contiguous block decomposition."""
    if not matrices:
        return BlockReducibilityReport(False, None, "no matrices supplied")

    size = matrices[0].rows
    if any(matrix.rows != size or matrix.cols != size for matrix in matrices):
        raise ValueError("Block-reducibility checks require square matrices of one size")

    for split in range(1, size):
        off_block_entries = []
        for matrix in matrices:
            off_block_entries.extend(matrix[:split, split:])
            off_block_entries.extend(matrix[split:, :split])
        if all(sp.simplify(entry) == 0 for entry in off_block_entries):
            return BlockReducibilityReport(True, split, "common contiguous block split detected")

    return BlockReducibilityReport(False, None, "no common contiguous block split detected")


def _is_scalar_identity(matrix: sp.MatrixBase) -> bool:
    if matrix.rows != matrix.cols:
        return False
    diagonal = [sp.simplify(matrix[i, i]) for i in range(matrix.rows)]
    off_diagonal = [
        sp.simplify(matrix[i, j])
        for i in range(matrix.rows)
        for j in range(matrix.cols)
        if i != j
    ]
    return all(entry == 0 for entry in off_diagonal) and all(
        sp.simplify(entry - diagonal[0]) == 0 for entry in diagonal
    )


def spectral_parameter_removal_heuristic(
    U: sp.MatrixBase, V: sp.MatrixBase, lambda_symbol: sp.Symbol
) -> SpectralParameterReport:
    """Flag only very restricted fake scalar-identity lambda insertions."""
    lambda_present = U.has(lambda_symbol) or V.has(lambda_symbol)
    if not lambda_present:
        return SpectralParameterReport(
            lambda_symbol=str(lambda_symbol),
            lambda_present=False,
            removable=False,
            status="absent",
            reason="spectral parameter does not occur",
        )

    dU = U.diff(lambda_symbol)
    dV = V.diff(lambda_symbol)
    if _is_scalar_identity(dU) and _is_scalar_identity(dV):
        return SpectralParameterReport(
            lambda_symbol=str(lambda_symbol),
            lambda_present=True,
            removable=True,
            status="fake_scalar_identity_lambda",
            reason="lambda dependence is restricted to scalar identity terms",
        )

    return SpectralParameterReport(
        lambda_symbol=str(lambda_symbol),
        lambda_present=True,
        removable=None,
        status="unresolved",
        reason="restricted heuristic cannot remove non-scalar lambda dependence",
    )


def analyze_gauge_risk(
    U: sp.MatrixBase, V: sp.MatrixBase, lambda_symbol: sp.Symbol | None = None
) -> GaugeReport:
    """Emit a conservative gauge-risk report for an explicit pair."""
    block_report = detect_block_reducibility((U, V))
    spectral_report = (
        spectral_parameter_removal_heuristic(U, V, lambda_symbol) if lambda_symbol is not None else None
    )
    risk = 0.0
    if block_report.block_reducible:
        risk += 0.4
    if spectral_report and spectral_report.removable:
        risk += 0.5
    if matrix_is_zero(U) and matrix_is_zero(V):
        risk = 1.0
    return GaugeReport(
        block_report=block_report,
        spectral_report=spectral_report,
        gauge_risk_score=min(1.0, risk),
    )
