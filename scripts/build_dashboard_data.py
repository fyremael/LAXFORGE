#!/usr/bin/env python
"""Build the static LAXFORGE dashboard data payload on explicit request."""

from __future__ import annotations

import argparse
from pathlib import Path

from laxforge.ui.dashboard import (
    add_dashboard_cli_arguments,
    write_dashboard_data,
    write_dashboard_data_js,
)


def main() -> None:
    """Write the browser-consumable dashboard data file."""
    parser = argparse.ArgumentParser(description=__doc__)
    add_dashboard_cli_arguments(parser)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    if args.output is None:
        output_path = repo_root / "web" / "dashboard_data.js"
    else:
        output_path = args.output
    written = (
        write_dashboard_data_js(output_path)
        if args.format == "js"
        else write_dashboard_data(output_path)
    )
    print(f"Wrote dashboard data: {written}")


if __name__ == "__main__":
    main()
