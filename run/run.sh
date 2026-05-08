#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

for i in $(seq 1 5); do
    echo "=== Run $i/5 ==="
    python3 simulator/runner.py
    echo
done
