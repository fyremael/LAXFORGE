"""Structured report objects for auditable symbolic calculations."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import sympy as sp

from laxforge.algebra.finite import FiniteAlgebraElement
from laxforge.algebra.truncated_poly import TruncatedPoly


def coefficient_basis(order: int, symbol_name: str = "eps") -> tuple[str, ...]:
    """Return display labels for the coefficient basis of R[symbol]/(symbol^order)."""
    labels = ["1"]
    labels.extend(symbol_name if i == 1 else f"{symbol_name}^{i}" for i in range(1, order))
    return tuple(labels)


@dataclass(frozen=True)
class CoefficientTermReport:
    """One coefficient-equation term after splitting by the algebra basis."""

    basis: str
    raw: sp.Expr
    simplified: sp.Expr
    is_zero: bool

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible view of this coefficient term."""
        return {
            "basis": self.basis,
            "raw": str(self.raw),
            "simplified": str(self.simplified),
            "is_zero": self.is_zero,
        }


@dataclass(frozen=True)
class MatrixEntryReport:
    """Coefficient-splitting report for a single matrix entry."""

    position: tuple[int, int]
    terms: tuple[CoefficientTermReport, ...]

    @property
    def key(self) -> str:
        """Return the stable string key used by legacy coefficient reports."""
        row, col = self.position
        return f"({row},{col})"

    @property
    def raw_coefficients(self) -> tuple[sp.Expr, ...]:
        """Return unsimplified coefficients in basis order."""
        return tuple(term.raw for term in self.terms)

    @property
    def simplified_coefficients(self) -> tuple[sp.Expr, ...]:
        """Return simplified coefficients in basis order."""
        return tuple(term.simplified for term in self.terms)

    @property
    def zero_flags(self) -> tuple[bool, ...]:
        """Return zero status for every split coefficient."""
        return tuple(term.is_zero for term in self.terms)

    @property
    def unresolved_terms(self) -> tuple[CoefficientTermReport, ...]:
        """Return all nonzero coefficient terms for this entry."""
        return tuple(term for term in self.terms if not term.is_zero)

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible view of this matrix-entry report."""
        return {
            "position": self.position,
            "terms": [term.as_dict() for term in self.terms],
            "zero_flags": list(self.zero_flags),
            "unresolved_terms": [term.as_dict() for term in self.unresolved_terms],
        }


@dataclass(frozen=True)
class CurvatureReport:
    """Structured zero-curvature coefficient report."""

    matrix_shape: tuple[int, int]
    coefficient_basis: tuple[str, ...]
    entries: dict[str, MatrixEntryReport]

    @property
    def curvature_residual_zero(self) -> bool:
        """Return whether every split coefficient simplified to zero."""
        return all(term.is_zero for entry in self.entries.values() for term in entry.terms)

    @property
    def curvature_terms_total(self) -> int:
        """Return the number of split coefficient equations."""
        return sum(len(entry.terms) for entry in self.entries.values())

    @property
    def curvature_terms_nonzero(self) -> int:
        """Return the number of unresolved split coefficient equations."""
        return sum(len(entry.unresolved_terms) for entry in self.entries.values())

    @property
    def basis_split_complete(self) -> bool:
        """Return whether every matrix entry was split against the full basis."""
        return all(len(entry.terms) == len(self.coefficient_basis) for entry in self.entries.values())

    @property
    def unresolved_terms(self) -> dict[str, tuple[CoefficientTermReport, ...]]:
        """Return unresolved coefficient terms by matrix entry."""
        return {
            key: entry.unresolved_terms
            for key, entry in self.entries.items()
            if entry.unresolved_terms
        }

    def entry_status_grid(self) -> tuple[tuple[str, ...], ...]:
        """Return a compact visual status grid for matrix entries."""
        rows, cols = self.matrix_shape
        grid: list[tuple[str, ...]] = []
        for i in range(rows):
            row = []
            for j in range(cols):
                unresolved_count = len(self.entries[f"({i},{j})"].unresolved_terms)
                row.append("OK" if unresolved_count == 0 else f"NONZERO({unresolved_count})")
            grid.append(tuple(row))
        return tuple(grid)

    def visual_summary_markdown(self) -> str:
        """Render a compact visual summary for quick residual inspection."""
        lines = [
            "## Visual Residual Summary",
            "",
            "Entry grid values are `OK` when all split coefficients vanish, or `NONZERO(n)` "
            "when `n` split coefficients remain unresolved.",
            "",
        ]

        rows, cols = self.matrix_shape
        header = "| row | " + " | ".join(f"col {j}" for j in range(cols)) + " |"
        separator = "|---" + "|---" * cols + "|"
        lines.extend([header, separator])
        for i, row in enumerate(self.entry_status_grid()):
            lines.append(f"| {i} | " + " | ".join(f"`{status}`" for status in row) + " |")

        lines.extend(
            [
                "",
                "| Entry | Zero? | Unresolved count |",
                "|---|---:|---:|",
            ]
        )
        for key in sorted(self.entries):
            entry = self.entries[key]
            unresolved_count = len(entry.unresolved_terms)
            lines.append(f"| `{key}` | {unresolved_count == 0} | {unresolved_count} |")

        return "\n".join(lines).rstrip() + "\n"

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible view of the curvature report."""
        return {
            "matrix_shape": self.matrix_shape,
            "coefficient_basis": list(self.coefficient_basis),
            "curvature_residual_zero": self.curvature_residual_zero,
            "curvature_terms_total": self.curvature_terms_total,
            "curvature_terms_nonzero": self.curvature_terms_nonzero,
            "basis_split_complete": self.basis_split_complete,
            "entry_status_grid": [list(row) for row in self.entry_status_grid()],
            "entries": {key: entry.as_dict() for key, entry in self.entries.items()},
        }

    def to_markdown(self) -> str:
        """Render the curvature report as a deterministic Markdown proof aid."""
        lines = [
            "# Curvature Report",
            "",
            f"- Matrix shape: {self.matrix_shape[0]} x {self.matrix_shape[1]}",
            f"- Coefficient basis: {', '.join(self.coefficient_basis)}",
            f"- Basis split complete: {self.basis_split_complete}",
            f"- Residual zero: {self.curvature_residual_zero}",
            f"- Total coefficient terms: {self.curvature_terms_total}",
            f"- Unresolved coefficient terms: {self.curvature_terms_nonzero}",
            "",
            self.visual_summary_markdown(),
            "",
        ]

        for key in sorted(self.entries):
            entry = self.entries[key]
            lines.extend(
                [
                    f"## Entry {key}",
                    "",
                    "| Basis | Raw coefficient | Simplified coefficient | Zero? |",
                    "|---|---|---|---|",
                ]
            )
            for term in entry.terms:
                lines.append(
                    f"| `{term.basis}` | `{term.raw}` | `{term.simplified}` | {term.is_zero} |"
                )
            lines.append("")

        if self.unresolved_terms:
            lines.extend(["## Unresolved Terms", ""])
            for key in sorted(self.unresolved_terms):
                for term in self.unresolved_terms[key]:
                    lines.append(f"- `{key}` `{term.basis}`: `{term.simplified}`")
            lines.append("")

        return "\n".join(lines).rstrip() + "\n"


@dataclass(frozen=True)
class CurvatureProofArtifact:
    """Auditable proof artifact for a zero-curvature calculation."""

    title: str
    report: CurvatureReport
    equation: str = "U_t - V_x + [U,V]"

    def to_markdown(self) -> str:
        """Render the proof artifact as deterministic Markdown."""
        lines = [
            f"# {self.title}",
            "",
            f"- Curvature convention: `{self.equation}`",
            f"- Matrix shape: {self.report.matrix_shape[0]} x {self.report.matrix_shape[1]}",
            f"- Coefficient basis: {', '.join(self.report.coefficient_basis)}",
            f"- Basis split complete: {self.report.basis_split_complete}",
            f"- Residual zero: {self.report.curvature_residual_zero}",
            f"- Total coefficient terms: {self.report.curvature_terms_total}",
            f"- Unresolved coefficient terms: {self.report.curvature_terms_nonzero}",
            "",
            self.report.to_markdown(),
        ]
        return "\n".join(lines).rstrip() + "\n"

    def write_markdown(self, path: str | Path, overwrite: bool = True) -> Path:
        """Write this proof artifact to a UTF-8 Markdown file."""
        output_path = Path(path)
        if output_path.exists() and not overwrite:
            raise FileExistsError(f"Refusing to overwrite existing proof artifact: {output_path}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.to_markdown(), encoding="utf-8")
        return output_path


def _entry_basis(entry: Any) -> tuple[str, ...]:
    if isinstance(entry, TruncatedPoly):
        return coefficient_basis(entry.order, entry.symbol_name)
    if isinstance(entry, FiniteAlgebraElement):
        return entry.basis_labels
    raise TypeError("Curvature matrix entries must be supported coefficient-algebra elements")


def _entry_basis_key(entry: Any) -> object:
    if isinstance(entry, TruncatedPoly):
        return ("truncated", entry.order, entry.symbol_name)
    if isinstance(entry, FiniteAlgebraElement):
        return ("finite", entry.algebra)
    raise TypeError("Curvature matrix entries must be supported coefficient-algebra elements")


def build_curvature_report(mat: list[list[Any]]) -> CurvatureReport:
    """Build a structured report from a zero-curvature matrix."""
    if not mat or not mat[0]:
        raise ValueError("Curvature matrix must be non-empty")

    rows = len(mat)
    cols = len(mat[0])
    first = mat[0][0]
    basis = _entry_basis(first)
    basis_key = _entry_basis_key(first)
    entries: dict[str, MatrixEntryReport] = {}

    for i, row in enumerate(mat):
        if len(row) != cols:
            raise ValueError("Curvature matrix must be rectangular")
        for j, entry in enumerate(row):
            if _entry_basis_key(entry) != basis_key:
                raise ValueError("Curvature matrix entries must share one coefficient basis")

            terms = []
            for label, raw in zip(basis, entry.coeffs):
                simplified = sp.simplify(raw)
                terms.append(
                    CoefficientTermReport(
                        basis=label,
                        raw=raw,
                        simplified=simplified,
                        is_zero=simplified == 0,
                    )
                )

            entry_report = MatrixEntryReport(position=(i, j), terms=tuple(terms))
            entries[entry_report.key] = entry_report

    return CurvatureReport(matrix_shape=(rows, cols), coefficient_basis=basis, entries=entries)


def build_curvature_proof_artifact(
    mat: list[list[TruncatedPoly]], title: str = "Curvature Proof"
) -> CurvatureProofArtifact:
    """Build a Markdown-ready proof artifact from a zero-curvature matrix."""
    return CurvatureProofArtifact(title=title, report=build_curvature_report(mat))
