#!/usr/bin/env python3
"""
Log a decision to decisions.csv.

Usage (from Claude chat or terminal):
    python log_decision.py \
        --decision "Use Invidious instead of yt-dlp" \
        --reasoning "yt-dlp is proxy-blocked on this server" \
        --outcome "YouTube search works without an API key"

The review date is automatically set to 30 days from today.
"""

import argparse
import csv
import sys
from datetime import date, timedelta
from pathlib import Path

CSV_FILE = Path(__file__).parent / "decisions.csv"
FIELDNAMES = ["date", "decision", "reasoning", "expected_outcome", "review_date", "status"]


def log(decision: str, reasoning: str, outcome: str) -> None:
    today = date.today()
    review_date = today + timedelta(days=30)
    row = {
        "date": today.isoformat(),
        "decision": decision,
        "reasoning": reasoning,
        "expected_outcome": outcome,
        "review_date": review_date.isoformat(),
        "status": "pending",
    }

    is_new = not CSV_FILE.exists() or CSV_FILE.stat().st_size == 0
    with CSV_FILE.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, lineterminator="\n")
        if is_new:
            writer.writeheader()
        writer.writerow(row)

    print(f"Logged: {decision}")
    print(f"Review due: {review_date.isoformat()}")


def main():
    parser = argparse.ArgumentParser(description="Log a decision to decisions.csv")
    parser.add_argument("--decision", required=True, help="What was decided")
    parser.add_argument("--reasoning", required=True, help="Why this decision was made")
    parser.add_argument("--outcome", required=True, help="Expected outcome")
    args = parser.parse_args()

    log(args.decision, args.reasoning, args.outcome)


if __name__ == "__main__":
    main()
