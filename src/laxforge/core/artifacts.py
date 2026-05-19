"""Explicit candidate artifact bundle writer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

from laxforge.core.dossier import CandidateDossier
from laxforge.core.models import ArtifactBundleModel


def required_artifact_filenames() -> tuple[str, ...]:
    """Return the required explicit artifact bundle filenames."""
    return ArtifactBundleModel().filenames()


def _markdown_report(title: str, payload: Mapping[str, object]) -> str:
    lines = [f"# {title}", ""]
    for key, value in payload.items():
        lines.append(f"- `{key}`: `{value}`")
    return "\n".join(lines).rstrip() + "\n"


def _write(path: Path, content: str, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_candidate_artifact_bundle(
    dossier: CandidateDossier,
    output_dir: str | Path,
    overwrite: bool = True,
) -> Path:
    """Write a complete explicit artifact bundle for one candidate."""
    output_path = Path(output_dir)
    if output_path.exists() and any(output_path.iterdir()) and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing artifact bundle: {output_path}")
    output_path.mkdir(parents=True, exist_ok=True)

    payload = dossier.as_dict()
    _write(
        output_path / "candidate.json",
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        overwrite,
    )
    _write(
        output_path / "curvature_report.md",
        _markdown_report("Curvature Report", payload["curvature_expansion"]),
        overwrite,
    )
    _write(
        output_path / "proof_sketch.md",
        _markdown_report("Coefficient Splitting Proof", payload["coefficient_splitting_proof"]),
        overwrite,
    )
    _write(
        output_path / "gauge_report.md",
        _markdown_report("Gauge Report", payload["gauge_report"]),
        overwrite,
    )
    _write(
        output_path / "invariants.json",
        json.dumps(
            {
                "cyclic_basis_report": payload["cyclic_basis_report"],
                "spectral_parameter_report": payload["spectral_parameter_report"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        overwrite,
    )
    _write(
        output_path / "conservation_report.md",
        _markdown_report("Conservation Report", payload["conservation_report"]),
        overwrite,
    )
    _write(
        output_path / "hamiltonian_report.md",
        _markdown_report("Hamiltonian Report", payload["hamiltonian_report"]),
        overwrite,
    )
    _write(
        output_path / "prior_art_report.md",
        _markdown_report("Prior-Art Report", payload["collision_report"]),
        overwrite,
    )
    _write(
        output_path / "publishability_classification.md",
        _markdown_report(
            "Human Review Classification",
            {
                "classification": payload["classification"],
                "recommendation": payload["recommendation"],
                "publishability_classification": payload["publishability_classification"],
                "falsifiability_statement": payload["falsifiability_statement"],
            },
        ),
        overwrite,
    )
    return output_path
