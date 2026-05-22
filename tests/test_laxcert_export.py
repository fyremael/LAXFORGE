from __future__ import annotations

import hashlib
import json

from laxforge.core.laxcert_export import (
    build_laxcert_calibration_candidate,
    write_laxcert_calibration_artifact,
)


def _canonical_hash(data: dict[str, object]) -> str:
    text = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def test_laxcert_calibration_candidate_uses_ast_certificate_shape() -> None:
    candidate = build_laxcert_calibration_candidate()

    assert candidate["candidate_id"] == "LaxforgeCalibration2x2Zero"
    assert candidate["laxcert_schema_version"] == candidate["schema_version"]
    assert candidate["scalar_ring"] == "rat_differential_polynomial"
    assert candidate["directions"] == {"space": ["x"], "time": "t"}
    assert candidate["fields"] == ["p", "q"]
    assert candidate["evolution"]["p"] == {"kind": "jet", "field": "p", "order": 1}
    assert candidate["operators"]["L"]["rows"][0][0]["terms"][0]["coeff"] == {
        "kind": "jet",
        "field": "p",
        "order": 0,
    }
    assert candidate["operators"]["P"]["rows"][0][0]["terms"][0] == {
        "order": 1,
        "coeff": {"kind": "const", "value": 1},
    }
    assert {claim["type"] for claim in candidate["claims"]} == {
        "lax_equation",
        "self_adjoint_L",
        "skew_adjoint_P",
    }
    assert candidate["provenance"]["source"] == "laxforge"


def test_laxcert_calibration_artifact_writes_manifest_and_candidate(tmp_path) -> None:
    output_dir = write_laxcert_calibration_artifact(tmp_path / "laxcert_export")

    candidate_path = output_dir / "candidate.json"
    manifest_path = output_dir / "laxforge_manifest.json"
    source_report_path = output_dir / "source_report.json"
    assert candidate_path.is_file()
    assert manifest_path.is_file()
    assert source_report_path.is_file()

    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source_report = json.loads(source_report_path.read_text(encoding="utf-8"))

    assert manifest["artifact_type"] == "laxforge.candidate_export"
    assert manifest["candidate_json"] == "candidate.json"
    assert manifest["candidate_hash"] == _canonical_hash(candidate)
    assert manifest["candidate_id"] == candidate["candidate_id"]
    assert source_report["candidate_hash"] == manifest["candidate_hash"]
