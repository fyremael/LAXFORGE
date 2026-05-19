import json

from laxforge.core.artifacts import (
    required_artifact_filenames,
    write_candidate_artifact_bundle,
)
from laxforge.core.completeness import (
    REQUIRED_ARTIFACTS,
    REQUIRED_DOSSIER_FIELDS,
    REQUIRED_RUN_IDS,
    build_functional_completeness_audit_report,
)
from laxforge.core.dossier import build_mkdv_second_jet_dossier
from laxforge.search.bulk import run_scaled_candidate_search
from laxforge.search.run_matrix import run_density_matrix_search, run_matrix_catalog


def test_complete_candidate_dossier_model_contains_required_fields():
    dossier = build_mkdv_second_jet_dossier()
    model = dossier.complete_model()
    payload = model.model_dump(mode="json")

    assert REQUIRED_DOSSIER_FIELDS <= set(payload)
    assert json.loads(model.model_dump_json())["name"] == dossier.name
    assert payload["field_definition"]["fields"]
    assert payload["connection_pair"]["status"] == "constructed"


def test_artifact_bundle_writer_emits_required_files_and_guard(tmp_path):
    dossier = build_mkdv_second_jet_dossier()
    output_dir = tmp_path / "bundle"

    written = write_candidate_artifact_bundle(dossier, output_dir)

    assert written == output_dir
    assert {path.name for path in output_dir.iterdir()} == REQUIRED_ARTIFACTS
    assert set(required_artifact_filenames()) == REQUIRED_ARTIFACTS
    assert json.loads((output_dir / "candidate.json").read_text(encoding="utf-8"))["name"]
    try:
        write_candidate_artifact_bundle(dossier, output_dir, overwrite=False)
    except FileExistsError as exc:
        assert "Refusing to overwrite" in str(exc)
    else:
        raise AssertionError("Expected artifact bundle overwrite guard")


def test_run_matrix_restores_density_and_renames_scaled_lane():
    density = run_density_matrix_search()
    scaled = run_scaled_candidate_search()
    catalog_ids = {entry.run_id for entry in run_matrix_catalog()}

    assert density.run_id == "DIS-003"
    assert scaled.run_id == "DIS-006"
    assert REQUIRED_RUN_IDS <= catalog_ids
    assert len(density.candidates) == 3
    assert len(scaled.candidates) >= 100


def test_functional_completeness_audit_passes():
    report = build_functional_completeness_audit_report()

    assert report.passed
    assert all(check.status == "pass" for check in report.checks)
