import json

import sympy as sp

from laxforge.core.prior_art import CandidateClassification
from laxforge.search.sphere import (
    SphereSearchConfig,
    run_sphere_low_order_search,
    write_discovery_run,
)


EXPECTED_CANDIDATE_NAMES = (
    "sphere zero-flow zero-connection control",
    "sphere s_cross_s_x tangent candidate",
    "sphere s_cross_s_xx Heisenberg-shaped candidate",
    "sphere s_cross_s_xxx exploratory candidate",
)


def test_sphere_low_order_search_generates_fixed_candidate_set():
    report = run_sphere_low_order_search()

    assert report.run_id == "DIS-002"
    assert tuple(candidate.name for candidate in report.candidates) == EXPECTED_CANDIDATE_NAMES


def test_every_sphere_candidate_has_dossier_gates_and_conservative_recommendation():
    report = run_sphere_low_order_search()
    required_gates = {
        "tangent_condition",
        "tangent_status",
        "curvature_validation",
        "gauge_risk_score",
        "spectral_parameter_status",
        "conservation_evidence",
        "collision_classification",
        "recommendation",
    }

    for candidate in report.candidates:
        assert candidate.dossier is not None
        assert required_gates <= set(candidate.gate_summary)
        assert candidate.dossier.collision_report
        assert candidate.dossier.recommendation in {"discard", "needs_human_review", "blocked"}


def test_zero_control_is_fake_and_discarded():
    candidate = run_sphere_low_order_search().candidates[0]

    assert candidate.dossier.classification == CandidateClassification.FAKE
    assert candidate.dossier.recommendation == "discard"
    assert candidate.connection_status == "validated_zero_control"
    assert candidate.failure_reasons


def test_cross_product_candidates_are_tangent_by_construction():
    report = run_sphere_low_order_search()

    for candidate in report.candidates[1:]:
        assert sp.simplify(candidate.tangent_condition) == 0
        assert candidate.tangent_status == "tangent"


def test_heisenberg_shaped_candidate_records_collision_warnings():
    candidate = run_sphere_low_order_search().candidates[2]
    collisions = candidate.dossier.collision_report["collisions"]

    assert candidate.dossier.classification == CandidateClassification.KNOWN
    assert candidate.dossier.recommendation == "discard"
    assert candidate.connection_status == "validated_known_zcr"
    assert candidate.zcr_report["validated"]
    assert candidate.gate_summary["zcr_solution"] == {"alpha": "-1", "beta": "1"}
    assert any("Heisenberg" in collision for collision in collisions)
    assert any("AKNS" in collision for collision in collisions)


def test_sx_candidate_records_recursive_nonlocal_tower_gate():
    candidate = run_sphere_low_order_search().candidates[1]

    assert candidate.dossier.recommendation == "needs_human_review"
    assert candidate.connection_status == "validated_formal_infinite_nonlocal_tower"
    assert candidate.zcr_report["validated"] is True
    assert candidate.zcr_report["first_potential_opened"] is True
    assert candidate.zcr_report["nonlocal_status"] == "validated_formal_infinite_nonlocal_tower"
    assert candidate.zcr_report["recursive_depth"] == 3
    assert (
        candidate.zcr_report["recursive_closure_status"]
        == "formal_infinite_tower_closes_by_recurrence"
    )
    assert candidate.zcr_report["obstruction_basis"]
    assert candidate.gate_summary["zcr_obstruction_basis"]
    assert any("finite truncations" in reason for reason in candidate.failure_reasons)


def test_sxxx_candidate_records_blocked_ansatz_obstruction():
    candidate = run_sphere_low_order_search().candidates[3]

    assert candidate.dossier.recommendation == "blocked"
    assert candidate.connection_status == "ansatz_obstruction_current_family"
    assert candidate.zcr_report["validated"] is False
    assert candidate.zcr_report["obstruction_basis"]
    assert candidate.gate_summary["zcr_obstruction_basis"]


def test_sphere_candidate_markdown_avoids_promotion_language():
    forbidden = ("novel", "publishable", "publication", "new ")
    report = run_sphere_low_order_search()

    for candidate in report.candidates:
        markdown = candidate.to_markdown().lower()
        assert all(term not in markdown for term in forbidden)


def test_sphere_search_config_can_limit_orders():
    report = run_sphere_low_order_search(SphereSearchConfig(max_order=1))

    assert tuple(candidate.order for candidate in report.candidates) == (0, 1)
    assert report.candidates[1].connection_status == "validated_formal_infinite_nonlocal_tower"


def test_sphere_search_config_can_freeze_sx_before_attempt():
    candidate = run_sphere_low_order_search(
        SphereSearchConfig(max_order=1, attempt_sx_ansatz=False)
    ).candidates[1]

    assert candidate.dossier.recommendation == "needs_human_review"
    assert candidate.connection_status == "no_validated_zcr"
    assert candidate.zcr_report is None


def test_sphere_search_config_can_freeze_sxxx_before_attempt():
    candidate = run_sphere_low_order_search(
        SphereSearchConfig(attempt_sxxx_ansatz=False)
    ).candidates[3]

    assert candidate.dossier.recommendation == "needs_human_review"
    assert candidate.connection_status == "no_validated_zcr"
    assert candidate.zcr_report is None


def test_write_discovery_run_emits_json_and_markdown(tmp_path):
    report = run_sphere_low_order_search()
    output_dir = tmp_path / "dis002"

    written_path = write_discovery_run(report, output_dir)

    assert written_path == output_dir
    run_json = json.loads((output_dir / "run.json").read_text(encoding="utf-8"))
    assert run_json["run_id"] == "DIS-002"
    assert (output_dir / "run.md").read_text(encoding="utf-8").startswith("# Discovery Run DIS-002")
    assert len(list((output_dir / "candidates").glob("*.json"))) == 4
    assert len(list((output_dir / "candidates").glob("*.md"))) == 4


def test_write_discovery_run_refuses_overwrite_when_requested(tmp_path):
    report = run_sphere_low_order_search()
    output_dir = tmp_path / "dis002"
    write_discovery_run(report, output_dir)

    try:
        write_discovery_run(report, output_dir, overwrite=False)
    except FileExistsError as exc:
        assert "Refusing to overwrite" in str(exc)
    else:
        raise AssertionError("Expected FileExistsError when overwrite is disabled")
