import sympy as sp

from laxforge.search.sphere_zcr import (
    cross_product_matrix,
    solve_heisenberg_zcr_ansatz,
    solve_sx_zcr_ansatz,
    solve_sxxx_zcr_ansatz,
)


def test_cross_product_matrix_represents_vector_cross_product():
    a1, a2, a3, b1, b2, b3 = sp.symbols("a1 a2 a3 b1 b2 b3")
    a = sp.Matrix([a1, a2, a3])
    b = sp.Matrix([b1, b2, b3])

    assert cross_product_matrix(a) * b == a.cross(b)


def test_heisenberg_zcr_ansatz_solves_expected_coefficients():
    report = solve_heisenberg_zcr_ansatz()

    assert report.solution == {sp.Symbol("alpha"): -1, sp.Symbol("beta"): 1}
    assert report.validated


def test_heisenberg_zcr_residual_reduces_to_zero_mod_constraints():
    report = solve_heisenberg_zcr_ansatz()

    assert report.constraints_used
    for residual_vector in report.reduced_residual_basis.values():
        assert all(sp.simplify(component) == 0 for component in residual_vector)


def test_heisenberg_zcr_pair_has_non_scalar_lambda_and_no_block_reduction():
    report = solve_heisenberg_zcr_ansatz()
    gauge_report = report.gauge_report

    assert gauge_report["block_report"]["block_reducible"] is False
    assert gauge_report["spectral_report"]["lambda_present"] is True
    assert gauge_report["spectral_report"]["status"] == "unresolved"


def test_heisenberg_zcr_records_cyclic_fingerprint_and_known_collision():
    report = solve_heisenberg_zcr_ansatz()

    assert report.cyclic_report["fingerprint"]
    assert report.collision_report["classification"] == "known"
    assert any("Heisenberg" in collision for collision in report.collision_report["collisions"])


def test_sx_zcr_ansatz_opens_first_nonlocal_potential_gate():
    report = solve_sx_zcr_ansatz()

    assert report.validated is True
    assert report.formal_status == "no_formal_solution"
    assert report.first_potential_opened is True
    assert report.nonlocal_status == "validated_formal_infinite_nonlocal_tower"
    assert report.recursive_depth == 3
    assert report.recursive_closure_status == "formal_infinite_tower_closes_by_recurrence"
    assert report.formal_tower_validated is True
    assert report.finite_truncation_validated is False
    assert report.covering_equations
    assert all(
        sp.simplify(component) == 0
        for component in report.nonlocal_residual_basis["lambda^1_after_covering"]
    )
    assert all(
        sp.simplify(component) == 0
        for component in report.nonlocal_residual_basis["lambda^3_after_covering"]
    )
    assert any(
        sp.simplify(component) != 0
        for component in report.nonlocal_residual_basis[
            "lambda^4_finite_tower_closure_residual"
        ]
    )
    assert all(
        sp.simplify(component) == 0
        for component in report.nonlocal_residual_basis["lambda^k_after_formal_recurrence"]
    )
    assert report.obstruction_basis
    assert any("formal infinite tower closes" in term for term in report.obstruction_basis)
    assert report.gauge_report["status"] == "partial_formal_tower_gauge_evidence"
    assert report.conservation_report["status"] == "constraint_preservation_only"
    assert "sphere_constraint_preservation" in report.conservation_report["method_evidence"]
    assert report.hamiltonian_report["status"] == "open_gate"
    assert report.hamiltonian_report["verified"] is False
    assert report.cyclic_report["fingerprint"]
    assert any(
        "Nonlocal coverings" in collision for collision in report.collision_report["collisions"]
    )


def test_sxxx_zcr_ansatz_records_current_family_obstruction():
    report = solve_sxxx_zcr_ansatz()

    assert report.validated is False
    assert report.consistency_solution == {
        sp.Symbol("a"): -sp.Symbol("b"),
        sp.Symbol("c"): sp.Symbol("b"),
        sp.Symbol("d"): 0,
        sp.Symbol("e"): 0,
    }
    assert report.obstruction_basis
    assert any("obstructed" in term for term in report.obstruction_basis)


def test_sxxx_zcr_attempt_carries_audit_evidence_without_promotion_language():
    reports = (solve_sx_zcr_ansatz(), solve_sxxx_zcr_ansatz())

    for report in reports:
        rendered = str(report.as_dict()).lower()
        assert report.gauge_report
        assert report.cyclic_report["fingerprint"]
        assert report.collision_report["classification"] == "needs_human_review"
        assert all(term not in rendered for term in ("novel", "publishable", "publication"))
