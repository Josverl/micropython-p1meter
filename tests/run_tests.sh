#!/bin/sh
# run_tests.sh — run the full test suite with the MicroPython Unix port.
#
# Usage (from repo root):
#   ./tests/run_tests.sh               # uses 'micropython' on $PATH
#   ./tests/run_tests.sh /path/to/micropython
#
# The tests can also be run individually:
#   micropython tests/test_crc16.py

set -e
MP=${1:-micropython}
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0
FAIL=0

echo "Using MicroPython: $($MP --version 2>&1 || echo 'version unknown')"
echo "Running tests from: $REPO_ROOT"
echo "------------------------------------------------------------"

for f in "$REPO_ROOT"/tests/test_*.py; do
    printf "  %-40s " "$(basename "$f")"
    if "$MP" "$f" 2>&1; then
        PASS=$((PASS + 1))
        echo "  PASS"
    else
        FAIL=$((FAIL + 1))
        echo "  FAIL"
    fi
done

echo "------------------------------------------------------------"
echo "Results: $PASS passed, $FAIL failed"

[ "$FAIL" -eq 0 ]
