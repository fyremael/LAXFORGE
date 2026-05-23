from __future__ import annotations

import json
from pathlib import Path


REQUIRED_FILES = [
    "laxforge_manifest.json",
    "candidate.json",
    "source_report.json",
]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    out_dir = Path("runs/laxcert_calibration")
    if not out_dir.exists():
        print("ERROR: runs/laxcert_calibration does not exist.")
        return 1

    missing = [name for name in REQUIRED_FILES if not (out_dir / name).exists()]
    if missing:
        print("ERROR: Missing required calibration artifacts:")
        for name in missing:
            print(f"  - {name}")
        return 1

    candidate = _load_json(out_dir / "candidate.json")
    source_report = _load_json(out_dir / "source_report.json")
    manifest = _load_json(out_dir / "laxforge_manifest.json")

    if not isinstance(candidate, dict) or not candidate:
        print("ERROR: candidate.json is empty or invalid.")
        return 1
    if not isinstance(source_report, dict) or not source_report:
        print("ERROR: source_report.json is empty or invalid.")
        return 1
    if not isinstance(manifest, dict) or not manifest:
        print("ERROR: laxforge_manifest.json is empty or invalid.")
        return 1

    print("Calibration artifact check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
