#!/usr/bin/env python3
"""
Daily cron script: flag decisions whose review_date has passed.

Rewrites decisions.csv in-place, changing status from 'pending' to 'review_due'
for any row where review_date <= today.

Cron entry (runs daily at 08:00):
    0 8 * * * /usr/bin/python3 /home/user/Rams-work/check_reviews.py
"""

import csv
import sys
from datetime import date
from pathlib import Path

CSV_FILE = Path(__file__).parent / "decisions.csv"
FIELDNAMES = ["date", "decision", "reasoning", "expected_outcome", "review_date", "status"]


def main():
    if not CSV_FILE.exists():
        sys.exit(0)

    today = date.today()
    rows = []
    flagged = 0

    with CSV_FILE.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["status"] == "pending":
                try:
                    if date.fromisoformat(row["review_date"]) <= today:
                        row["status"] = "review_due"
                        flagged += 1
                except ValueError:
                    pass
            rows.append(row)

    with CSV_FILE.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    if flagged:
        print(f"[check_reviews] Flagged {flagged} decision(s) as review_due")


if __name__ == "__main__":
    main()
