"""LAXCERT candidate-certificate export helpers.

This module is the LAXFORGE side of the LAXFORGE -> LAXCERT boundary. It emits
AST-based candidate JSON for the current LAXCERT MVP schema, plus a manifest
that lets LAXCERT ingest the artifact directory without relying on internal
fixtures.
"""

from __future__ import annotations

import hashlib
import json
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any


LAXCERT_TARGET_VERSION = "0.1.0"
LAXCERT_SCHEMA_VERSION = "0.1.0"
EXPORTER_NAME = "laxforge.core.laxcert_export.write_laxcert_calibration_artifact"


def _package_version() -> str:
    try:
        return version("laxforge")
    except PackageNotFoundError:
        return "0.1.0"


def _sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _const(value: int | str) -> dict[str, Any]:
    return {"kind": "const", "value": value}


def _jet(field: str, order: int) -> dict[str, Any]:
    return {"kind": "jet", "field": field, "order": order}


def _diffop(order: int, coeff: dict[str, Any]) -> dict[str, Any]:
    return {"terms": [{"order": order, "coeff": coeff}]}


def _zero_op() -> dict[str, Any]:
    return _diffop(0, _const(0))


def build_laxcert_calibration_candidate(
    candidate_id: str = "LaxforgeCalibration2x2Zero",
) -> dict[str, Any]:
    """Build the current LAXCERT-compatible 2x2 calibration candidate.

    This is intentionally conservative: it exercises matrix differential
    operators, evolution-derived `L_t`, operator commutator cancellation, and
    adjoint claims while staying inside LAXCERT's current MVP schema.
    """

    return {
        "schema_version": LAXCERT_SCHEMA_VERSION,
        "candidate_id": candidate_id,
        "laxforge_version": f"laxforge:{_package_version()}",
        "laxcert_target_version": LAXCERT_TARGET_VERSION,
        "scalar_ring": "rat_differential_polynomial",
        "directions": {"space": ["x"], "time": "t"},
        "fields": ["p", "q"],
        "evolution": {
            "p": _jet("p", 1),
            "q": _jet("q", 1),
        },
        "operators": {
            "L": {
                "rows": [
                    [_diffop(0, _jet("p", 0)), _zero_op()],
                    [_zero_op(), _diffop(0, _jet("q", 0))],
                ]
            },
            "P": {
                "rows": [
                    [_diffop(1, _const(1)), _zero_op()],
                    [_zero_op(), _diffop(1, _const(1))],
                ]
            },
        },
        "claims": [
            {"type": "lax_equation", "proof_strategy": "coefficient_certificate"},
            {"type": "self_adjoint_L", "proof_strategy": "coefficient_certificate"},
            {"type": "skew_adjoint_P", "proof_strategy": "coefficient_certificate"},
        ],
        "assumptions": [
            "formal differential operators over commuting scalar coefficients",
            "formal adjoint ignores boundary terms",
        ],
        "provenance": {
            "source": "laxforge",
            "exporter": EXPORTER_NAME,
            "calibration_target": "2x2 formal differential-operator smoke calibration",
        },
    }


def _write_json(path: Path, data: dict[str, Any], overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_laxcert_calibration_artifact(
    output_dir: str | Path,
    *,
    candidate_id: str = "LaxforgeCalibration2x2Zero",
    overwrite: bool = False,
) -> Path:
    """Write a LAXCERT-ingestable LAXFORGE calibration artifact directory."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    candidate = build_laxcert_calibration_candidate(candidate_id=candidate_id)
    candidate_text = _canonical_json(candidate)
    candidate_hash = _sha256_text(candidate_text)
    manifest = {
        "artifact_type": "laxforge.candidate_export",
        "candidate_id": candidate_id,
        "candidate_json": "candidate.json",
        "candidate_hash": candidate_hash,
        "exporter": EXPORTER_NAME,
        "laxcert_target_version": LAXCERT_TARGET_VERSION,
        "laxforge_version": f"laxforge:{_package_version()}",
    }
    source_report = {
        "status": "exported",
        "candidate_id": candidate_id,
        "candidate_hash": candidate_hash,
        "summary": (
            "LAXFORGE emitted an AST-based formal differential-operator "
            "candidate for LAXCERT MVP calibration."
        ),
        "trust_boundary": "LAXFORGE proposes candidate JSON; LAXCERT validates and proves it.",
    }

    _write_json(output_path / "candidate.json", candidate, overwrite)
    _write_json(output_path / "laxforge_manifest.json", manifest, overwrite)
    _write_json(output_path / "source_report.json", source_report, overwrite)
    return output_path
