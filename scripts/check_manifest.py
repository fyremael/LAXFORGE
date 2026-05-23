from __future__ import annotations

from pathlib import Path


REQUIRED_SECTIONS = [
    "## Candidate metadata",
    "## Algebra and representation",
    "## Zero-curvature validation",
    "## Gauge/fake-pair checks",
    "## Invariants and classification",
    "## Reproducibility",
]


def main() -> int:
    manifest_path = Path("MANIFEST.md")
    if not manifest_path.exists():
        print("ERROR: MANIFEST.md is missing.")
        return 1

    text = manifest_path.read_text(encoding="utf-8")
    missing = [section for section in REQUIRED_SECTIONS if section not in text]
    if missing:
        print("ERROR: MANIFEST.md is missing required section headers:")
        for section in missing:
            print(f"  - {section}")
        return 1

    print("MANIFEST.md check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
