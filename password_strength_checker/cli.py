"""Command-line interface for the password strength checker.

Usage:
    python cli.py "MyPassw0rd!"     # check a password given as an argument
    python cli.py                   # prompt for a password without echoing it
"""

import argparse
import getpass
import sys

from strength import check_strength

# Exit codes let the tool be used in scripts and CI pipelines.
EXIT_STRONG = 0
EXIT_WEAK = 1

_BARS = {"weak": "█░░", "medium": "██░", "strong": "███"}


def format_report(report):
    """Render a check_strength() report as human-readable text."""
    rating = report["rating"]
    lines = [
        f"Strength : {rating.upper()}  {_BARS[rating]}  ({report['score']}/5)",
    ]
    if report["feedback"]:
        lines.append("Suggestions:")
        lines.extend(f"  - {tip}" for tip in report["feedback"])
    else:
        lines.append("Looks good — no suggestions.")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check how strong a password is."
    )
    parser.add_argument(
        "password",
        nargs="?",
        help="Password to check. If omitted, you'll be prompted securely.",
    )
    args = parser.parse_args(argv)

    password = args.password
    if password is None:
        password = getpass.getpass("Password: ")

    report = check_strength(password)
    print(format_report(report))

    return EXIT_STRONG if report["is_strong"] else EXIT_WEAK


if __name__ == "__main__":
    sys.exit(main())
