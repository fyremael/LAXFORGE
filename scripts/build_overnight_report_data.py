#!/usr/bin/env python
"""Build the explicit static data file for the overnight report."""

from __future__ import annotations

import argparse
from pathlib import Path

from laxforge.search.overnight import (
    OvernightSearchConfig,
    run_overnight_search,
    write_overnight_data_js,
)


def main() -> None:
    """Generate web/overnight_data.js on explicit request."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("web") / "overnight_data.js",
        help="Output JavaScript file path.",
    )
    parser.add_argument(
        "--target-count",
        type=int,
        default=1024,
        help="Number of candidates to generate.",
    )
    args = parser.parse_args()
    report = run_overnight_search(OvernightSearchConfig(target_count=args.target_count))
    output_path = write_overnight_data_js(args.output, report=report)
    print(f"Wrote overnight report data: {output_path.resolve()}")


if __name__ == "__main__":
    main()
