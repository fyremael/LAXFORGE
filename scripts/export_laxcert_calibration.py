#!/usr/bin/env python
"""Export a LAXCERT-ingestable calibration artifact from LAXFORGE."""

from __future__ import annotations

import argparse
from pathlib import Path

from laxforge.core.laxcert_export import write_laxcert_calibration_artifact


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--candidate-id", default="LaxforgeAKNSD2TransportZero")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    output_path = write_laxcert_calibration_artifact(
        args.output_dir,
        candidate_id=args.candidate_id,
        overwrite=args.overwrite,
    )
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
