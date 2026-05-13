import json

import sympy as sp

from laxforge.search.bulk import (
    BulkSearchConfig,
    run_scaled_candidate_search,
    write_scaled_candidate_search,
)


FORBIDDEN_PROMOTION_TERMS = ("novel", "publishable", "publication")


def test_scaled_candidate_search_generates_minimum_batch():
    report = run_scaled_candidate_search()

    assert report.run_id == "DIS-003"
    assert len(report.candidates) == 128
    assert report.candidates[0].name == "scaled sphere zero-flow zero-connection control"
    assert len({candidate.name for candidate in report.candidates}) == len(report.candidates)


def test_scaled_candidates_are_conservative_and_auditable():
    report = run_scaled_candidate_search()
    required_gates = {
        "tangent_condition",
        "tangent_status",
        "curvature_validation",
        "gauge_risk_score",
        "spectral_parameter_status",
        "conservation_evidence",
        "collision_classification",
        "recommendation",
        "descriptor",
        "priority_score",
    }

    for candidate in report.candidates:
        assert required_gates <= set(candidate.gate_summary)
        assert candidate.dossier.recommendation in {"discard", "needs_human_review"}
        assert candidate.failure_reasons
        assert candidate.dossier.collision_report["checklist"]


def test_scaled_search_zero_control_is_discarded_and_others_remain_review():
    report = run_scaled_candidate_search()
    zero_control = report.candidates[0]
    reviewed = report.candidates[1:]

    assert zero_control.dossier.recommendation == "discard"
    assert zero_control.connection_status == "validated_zero_control"
    assert all(candidate.dossier.recommendation == "needs_human_review" for candidate in reviewed)
    assert len(reviewed) >= 100


def test_scaled_tangent_candidates_have_zero_tangent_condition():
    report = run_scaled_candidate_search()

    for candidate in report.candidates[1:]:
        assert sp.simplify(candidate.tangent_condition) == 0
        assert candidate.tangent_status == "tangent"


def test_scaled_search_refuses_too_small_batch():
    try:
        run_scaled_candidate_search(BulkSearchConfig(target_count=99))
    except ValueError as exc:
        assert "at least 100 candidates" in str(exc)
    else:
        raise AssertionError("Expected scaled search to reject fewer than 100 candidates")


def test_scaled_search_avoids_promotion_language():
    report = run_scaled_candidate_search()
    rendered = json.dumps(report.as_dict(), sort_keys=True).lower()
    rendered += "\n".join(candidate.to_markdown().lower() for candidate in report.candidates)

    assert all(term not in rendered for term in FORBIDDEN_PROMOTION_TERMS)


def test_write_scaled_candidate_search_emits_json_and_markdown(tmp_path):
    report = run_scaled_candidate_search()
    output_dir = tmp_path / "dis003"

    written_path = write_scaled_candidate_search(report, output_dir)

    assert written_path == output_dir
    run_json = json.loads((output_dir / "run.json").read_text(encoding="utf-8"))
    assert run_json["run_id"] == "DIS-003"
    assert len(run_json["candidates"]) == 128
    assert (output_dir / "run.md").read_text(encoding="utf-8").startswith(
        "# Discovery Run DIS-003"
    )
    assert len(list((output_dir / "candidates").glob("*.json"))) == 128
    assert len(list((output_dir / "candidates").glob("*.md"))) == 128


def test_write_scaled_candidate_search_refuses_overwrite_when_requested(tmp_path):
    report = run_scaled_candidate_search()
    output_dir = tmp_path / "dis003"
    write_scaled_candidate_search(report, output_dir)

    try:
        write_scaled_candidate_search(report, output_dir, overwrite=False)
    except FileExistsError as exc:
        assert "Refusing to overwrite" in str(exc)
    else:
        raise AssertionError("Expected FileExistsError when overwrite is disabled")
