import sympy as sp

from laxforge.algebra.truncated_poly import TruncatedPoly
from laxforge.core.zero_curvature import (
    curvature_proof_artifact,
    curvature_report,
    markdown_curvature_report,
    matrix_is_zero,
    zero_curvature,
)
from laxforge.examples.mkdv_second_jet import build_pair, expected_flow_components, validate


def test_curvature_report_marks_zero_matrix_residual_zero():
    zero = TruncatedPoly.zero(order=3)
    report = curvature_report([[zero, zero], [zero, zero]])

    assert report.matrix_shape == (2, 2)
    assert report.coefficient_basis == ("1", "eps", "eps^2")
    assert report.basis_split_complete
    assert report.curvature_residual_zero
    assert report.curvature_terms_total == 12
    assert report.curvature_terms_nonzero == 0
    assert report.entry_status_grid() == (("OK", "OK"), ("OK", "OK"))


def test_mkdv_validation_includes_structured_curvature_report():
    result = validate()
    report = result["curvature_report"]

    assert report.matrix_shape == (2, 2)
    assert report.coefficient_basis == ("1", "eps", "eps^2")
    assert report.basis_split_complete
    assert not report.curvature_residual_zero
    assert set(report.unresolved_terms) == {"(0,1)", "(1,0)"}
    assert report.entry_status_grid() == (("OK", "NONZERO(3)"), ("NONZERO(3)", "OK"))


def test_mkdv_report_reproduces_expected_split_flow():
    x, t, _lam, _fields, U, V = build_pair(order=3)

    report = curvature_report(zero_curvature(U, V, x, t))
    expected = expected_flow_components(x, t)

    upper_right = report.entries["(0,1)"].simplified_coefficients
    lower_left = report.entries["(1,0)"].simplified_coefficients

    assert all(sp.simplify(actual - wanted) == 0 for actual, wanted in zip(upper_right, expected))
    assert all(sp.simplify(actual + wanted) == 0 for actual, wanted in zip(lower_left, expected))


def test_markdown_curvature_report_contains_auditable_summary():
    zero = TruncatedPoly.zero(order=2)
    markdown = markdown_curvature_report([[zero]])

    assert "# Curvature Report" in markdown
    assert "## Visual Residual Summary" in markdown
    assert "- Matrix shape: 1 x 1" in markdown
    assert "- Coefficient basis: 1, eps" in markdown
    assert "| row | col 0 |" in markdown
    assert "| 0 | `OK` |" in markdown
    assert "| Basis | Raw coefficient | Simplified coefficient | Zero? |" in markdown


def test_exact_diagonal_pure_gauge_connection_is_flat():
    x, t = sp.symbols("x t")
    phi = sp.Function("phi")(x, t)
    phi_x = TruncatedPoly.from_coeffs([sp.diff(phi, x)])
    phi_t = TruncatedPoly.from_coeffs([sp.diff(phi, t)])
    zero = TruncatedPoly.zero()

    U = [[phi_x, zero], [zero, -phi_x]]
    V = [[phi_t, zero], [zero, -phi_t]]
    curvature = zero_curvature(U, V, x, t)
    report = curvature_report(curvature)

    assert matrix_is_zero(curvature)
    assert report.curvature_residual_zero
    assert report.curvature_terms_nonzero == 0


def test_curvature_proof_artifact_markdown_contains_convention_and_summary():
    zero = TruncatedPoly.zero(order=2)
    artifact = curvature_proof_artifact([[zero]], title="Flatness Audit")
    markdown = artifact.to_markdown()

    assert markdown.startswith("# Flatness Audit")
    assert "- Curvature convention: `U_t - V_x + [U,V]`" in markdown
    assert "- Matrix shape: 1 x 1" in markdown
    assert "- Coefficient basis: 1, eps" in markdown
    assert "- Residual zero: True" in markdown
    assert "- Total coefficient terms: 2" in markdown
    assert "## Visual Residual Summary" in markdown
    assert "| Basis | Raw coefficient | Simplified coefficient | Zero? |" in markdown


def test_curvature_report_dict_includes_visual_status_grid():
    zero = TruncatedPoly.zero(order=2)
    report_dict = curvature_report([[zero]]).as_dict()

    assert report_dict["entry_status_grid"] == [["OK"]]


def test_curvature_proof_artifact_writer_emits_utf8_markdown(tmp_path):
    zero = TruncatedPoly.zero(order=2)
    artifact = curvature_proof_artifact([[zero]], title="Writer Audit")
    output_path = tmp_path / "nested" / "curvature_report.md"

    written_path = artifact.write_markdown(output_path)

    assert written_path == output_path
    assert output_path.read_text(encoding="utf-8") == artifact.to_markdown()


def test_curvature_proof_artifact_writer_can_refuse_overwrite(tmp_path):
    zero = TruncatedPoly.zero(order=2)
    artifact = curvature_proof_artifact([[zero]], title="Writer Audit")
    output_path = tmp_path / "curvature_report.md"
    artifact.write_markdown(output_path)

    try:
        artifact.write_markdown(output_path, overwrite=False)
    except FileExistsError as exc:
        assert "Refusing to overwrite" in str(exc)
    else:
        raise AssertionError("Expected FileExistsError when overwrite is disabled")
