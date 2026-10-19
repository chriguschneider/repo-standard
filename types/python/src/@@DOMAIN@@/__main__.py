"""Command-line entry point: `@@REPO@@` or `python -m @@DOMAIN@@`."""

from __future__ import annotations

import argparse

from . import __version__

# The one-sentence description can be long; it is data, not code.
DESCRIPTION = "@@DESCRIPTION@@"  # noqa: E501


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="@@REPO@@", description=DESCRIPTION)
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.parse_args(argv)
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
