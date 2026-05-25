import json

from laxforge.search.serious_cycle import run_serious_cycle_001, write_serious_cycle_report


FORBIDDEN_PROMOTION_TERMS = ("novel", "publishable", "publication")


def test_serious_cycle_freezes_baseline_and_refreshes_blocked_state():
    report = run_serious_cycle_001()
    baseline_target = next(
        record
        for record in report.baseline_process.frontier
        if record.item_id == report.target_item_id
    )
    refreshed_target = next(
        record
        for record in report.refreshed_process.frontier
        if record.item_id == report.target_item_id
    )

    assert report.cycle_id == "SERIOUS-001"
    assert baseline_target.potential_status == "promising_potential"
    assert refreshed_target.potential_status == "blocked_by_ansatz_obstruction"
    assert report.result_status == "blocked"
    assert report.recommendation == "blocked"


def test_serious_cycle_records_attempt_and_procedure_evidence():
    report = run_serious_cycle_001()

    assert report.attempt_report.validated is False
    assert report.attempt_report.obstruction_basis
    assert report.baseline_procedure.status == "pass"
    assert report.refreshed_procedure.status == "pass"
    assert report.refreshed_process.frontier[0].item_id == (
        "sphere-s-cross-s-x-tangent-candidate"
    )


def test_serious_cycle_report_avoids_promotion_language():
    report = run_serious_cycle_001()
    rendered = json.dumps(report.as_dict(), sort_keys=True).lower() + report.to_markdown().lower()

    assert all(term not in rendered for term in FORBIDDEN_PROMOTION_TERMS)


def test_write_serious_cycle_report_emits_json_and_markdown(tmp_path):
    report = run_serious_cycle_001()
    output_dir = tmp_path / "serious"

    written_path = write_serious_cycle_report(report, output_dir)

    assert written_path == output_dir
    cycle_json = json.loads((output_dir / "serious_cycle.json").read_text(encoding="utf-8"))
    assert cycle_json["cycle_id"] == "SERIOUS-001"
    assert (output_dir / "serious_cycle.md").read_text(encoding="utf-8").startswith(
        "# Serious Cycle SERIOUS-001"
    )


def test_write_serious_cycle_report_refuses_overwrite_when_requested(tmp_path):
    report = run_serious_cycle_001()
    output_dir = tmp_path / "serious"
    write_serious_cycle_report(report, output_dir)

    try:
        write_serious_cycle_report(report, output_dir, overwrite=False)
    except FileExistsError as exc:
        assert "Refusing to overwrite" in str(exc)
    else:
        raise AssertionError("Expected FileExistsError when overwrite is disabled")
