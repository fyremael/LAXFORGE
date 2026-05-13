"""Small invariant summaries for explicit matrix pairs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import sympy as sp

from laxforge.core.gauge import detect_block_reducibility


@dataclass(frozen=True)
class MatrixInvariantReport:
    """Trace/determinant/block signatures for explicit matrices."""

    traces: tuple[sp.Expr, ...]
    determinants: tuple[sp.Expr, ...]
    block_reducible: bool
    spectral_parameter_present: bool
    fingerprint: str

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible invariant report."""
        return {
            "traces": [str(trace) for trace in self.traces],
            "determinants": [str(det) for det in self.determinants],
            "block_reducible": self.block_reducible,
            "spectral_parameter_present": self.spectral_parameter_present,
            "fingerprint": self.fingerprint,
        }


def matrix_pair_invariants(
    matrices: Sequence[sp.MatrixBase], lambda_symbol: sp.Symbol | None = None
) -> MatrixInvariantReport:
    """Compute deterministic low-cost invariants for explicit matrix pairs."""
    traces = tuple(sp.simplify(matrix.trace()) for matrix in matrices)
    determinants = tuple(sp.simplify(matrix.det()) for matrix in matrices)
    block_report = detect_block_reducibility(matrices)
    spectral_present = bool(lambda_symbol and any(matrix.has(lambda_symbol) for matrix in matrices))
    fingerprint = (
        f"tr={tuple(map(str, traces))};det={tuple(map(str, determinants))};"
        f"block={block_report.block_reducible};lambda={spectral_present}"
    )
    return MatrixInvariantReport(
        traces=traces,
        determinants=determinants,
        block_reducible=block_report.block_reducible,
        spectral_parameter_present=spectral_present,
        fingerprint=fingerprint,
    )
