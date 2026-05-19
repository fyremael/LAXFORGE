import json

from laxforge.core.procedures import (
    audit_iterative_discovery,
    build_procedure_audit_report,
    discovery_procedure_steps,
    write_procedure_audit_report,
)
from laxforge.search.iterative import run_iterative_discovery


FORBIDDEN_PROMOTION_TERMS = ("novel", "publishable", "publication")


def test_discovery_procedure_has_ordered_steps_and_evidence_rules():
    steps = discovery_procedure_steps()

    assert tuple(step.step_id for step in steps) == tuple(f"P{index}" for index in range(10))
    assert steps[0].owner == "Orchestrator"
    assert steps[-1].label == "Emit explicit artifacts"
    assert all(step.required_evidence for step in steps)
    assert all(step.completion_rule for step in steps)


def test_current_iterative_discovery_passes_procedure_audit():
    report = build_procedure_audit_report()

    assert report.procedure_id == "PROC-001"
    assert report.status == "pass"
    assert report.passed is True
    assert report.failure_count == 0
    assert {check.check_id for check in report.checks} == {
        "A0",
        "A1",
        "A2",
        "A3",
        "A4",
        "A5",
        "A6",
        "A7",
    }
    assert all(check.status == "pass" for check in report.checks)


def test_procedure_audit_tracks_frontier_and_discard_partition():
    iterative = run_iterative_discovery()
    audit = audit_iterative_discovery(iterative)
    partition_check = next(check for check in audit.checks if check.check_id == "A1")

    assert partition_check.status == "pass"
    assert len(partition_check.item_ids) == len(iterative.all_records)
    assert len(iterative.frontier) == 134
    assert len(iterative.discarded) == 9


def test_procedure_audit_markdown_and_json_avoid_promotion_language():
    report = build_procedure_audit_report()
    rendered = json.dumps(report.as_dict(), sort_keys=True).lower() + report.to_markdown().lower()

    assert all(term not in rendered for term in FORBIDDEN_PROMOTION_TERMS)


def test_write_procedure_audit_report_emits_json_and_markdown(tmp_path):
    report = build_procedure_audit_report()
    output_dir = tmp_path / "procedure"

    written_path = write_procedure_audit_report(report, output_dir)

    assert written_path == output_dir
    audit_json = json.loads((output_dir / "procedure_audit.json").read_text(encoding="utf-8"))
    assert audit_json["procedure_id"] == "PROC-001"
    assert (output_dir / "procedure_audit.md").read_text(encoding="utf-8").startswith(
        "# LAXFORGE Discovery Procedure Audit"
    )


def test_write_procedure_audit_report_refuses_overwrite_when_requested(tmp_path):
    report = build_procedure_audit_report()
    output_dir = tmp_path / "procedure"
    write_procedure_audit_report(report, output_dir)

    try:
        write_procedure_audit_report(report, output_dir, overwrite=False)
    except FileExistsError as exc:
        assert "Refusing to overwrite" in str(exc)
    else:
        raise AssertionError("Expected FileExistsError when overwrite is disabled")
