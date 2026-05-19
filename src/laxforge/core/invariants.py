"""Small invariant summaries for explicit matrix pairs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import sympy as sp

from laxforge.core.gauge import detect_block_reducibility
from laxforge.core.models import InvariantReportModel


@dataclass(frozen=True)
class MatrixInvariantReport:
    """Trace/determinant/block signatures for explicit matrices."""

    traces: tuple[sp.Expr, ...]
    determinants: tuple[sp.Expr, ...]
    block_reducible: bool
    spectral_parameter_present: bool
    fingerprint: str
    spectral_parameter_essentiality: str = "untested"
    block_decomposition_signature: str = "none_detected"
    grading_signature: str = "untested"
    generated_pde_canonical_form: str = "untested"

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible invariant report."""
        return {
            "traces": [str(trace) for trace in self.traces],
            "determinants": [str(det) for det in self.determinants],
            "block_reducible": self.block_reducible,
            "spectral_parameter_present": self.spectral_parameter_present,
            "fingerprint": self.fingerprint,
            "spectral_parameter_essentiality": self.spectral_parameter_essentiality,
            "block_decomposition_signature": self.block_decomposition_signature,
            "grading_signature": self.grading_signature,
            "generated_pde_canonical_form": self.generated_pde_canonical_form,
        }

    def complete_model(self) -> InvariantReportModel:
        """Return the canonical invariant report model."""
        return InvariantReportModel(
            cyclic_basis_data=None,
            spectral_parameter_essentiality=self.spectral_parameter_essentiality,
            trace_invariants=[str(trace) for trace in self.traces],
            block_decomposition_signature=self.block_decomposition_signature,
            grading_signature=self.grading_signature,
            generated_pde_canonical_form=self.generated_pde_canonical_form,
            fingerprint=self.fingerprint,
        )


def matrix_pair_invariants(
    matrices: Sequence[sp.MatrixBase], lambda_symbol: sp.Symbol | None = None
) -> MatrixInvariantReport:
    """Compute deterministic low-cost invariants for explicit matrix pairs."""
    traces = tuple(sp.simplify(matrix.trace()) for matrix in matrices)
    determinants = tuple(sp.simplify(matrix.det()) for matrix in matrices)
    block_report = detect_block_reducibility(matrices)
    spectral_present = bool(lambda_symbol and any(matrix.has(lambda_symbol) for matrix in matrices))
    block_signature = (
        f"coordinate_block:{block_report.split_index}:"
        f"{block_report.permutation or 'contiguous'}"
        if block_report.block_reducible
        else "none_detected"
    )
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
        spectral_parameter_essentiality="untested" if spectral_present else "absent",
        block_decomposition_signature=block_signature,
    )


def open_invariant_report(reason: str) -> InvariantReportModel:
    """Return an explicit open-gate invariant report."""
    return InvariantReportModel(
        spectral_parameter_essentiality="untested",
        block_decomposition_signature="untested",
        grading_signature="untested",
        generated_pde_canonical_form="untested",
        fingerprint=f"open_gate:{reason}",
    )
