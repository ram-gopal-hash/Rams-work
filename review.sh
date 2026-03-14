#!/usr/bin/env bash
# Surface decisions flagged as review_due from decisions.csv
# Usage: ./review.sh

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
CSV="$REPO_DIR/decisions.csv"

if [[ ! -f "$CSV" ]]; then
    echo "No decisions.csv found."
    exit 0
fi

# Count flagged rows (skip header)
COUNT=$(tail -n +2 "$CSV" | awk -F',' '$6 == "review_due"' | wc -l)

if [[ "$COUNT" -eq 0 ]]; then
    echo "No decisions are due for review."
    exit 0
fi

echo "========================================"
echo " DECISIONS DUE FOR REVIEW ($COUNT)"
echo "========================================"
echo ""

# Print each review_due row in a readable format
tail -n +2 "$CSV" | awk -F',' '
$6 == "review_due" {
    # Strip surrounding quotes if present
    gsub(/"/, "", $0)
    printf "Date logged : %s\n", $1
    printf "Decision    : %s\n", $2
    printf "Reasoning   : %s\n", $3
    printf "Expected    : %s\n", $4
    printf "Review date : %s\n", $5
    printf "Status      : %s\n", $6
    print "----------------------------------------"
}'
