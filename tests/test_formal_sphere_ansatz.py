from laxforge.search.formal_sphere_ansatz import (
    Atom,
    FormalVector,
    cross_s,
    solve_formal_sphere_ansatz,
)
from laxforge.search.overnight import OvernightSearchConfig, run_overnight_search


def _candidate(vector_atom: str):
    report = run_overnight_search(
        OvernightSearchConfig(target_count=500, max_derivative_order=4)
    )
    return next(
        candidate
        for candidate in report.candidates
        if candidate.family == "scalar_weighted_cross"
        and candidate.scalar_factor == "unit"
        and candidate.vector_atom == vector_atom
    )


def test_formal_vector_calculus_reduces_heisenberg_identity():
    reduced = cross_s(FormalVector.atom(Atom("C", 0, 1)))

    assert reduced.terms == {Atom("S", 1): -1}


def test_formal_ansatz_solves_unit_sxx_heisenberg_candidate():
    report = solve_formal_sphere_ansatz(_candidate("sxx"), degree=2)

    assert report.solved
    assert report.status == "validated_formal_zcr_candidate"
    assert report.solution


def test_formal_ansatz_keeps_unit_sxxx_obstruction_visible():
    report = solve_formal_sphere_ansatz(_candidate("sxxx"), degree=3)

    assert not report.solved
    assert report.status in {"no_formal_solution", "residuals_remain_after_formal_solve"}
    assert report.obstruction_basis
