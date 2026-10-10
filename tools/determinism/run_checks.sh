#!/bin/bash
# Run the determinism checks over a range of configurations.
# Exits non-zero if any configuration produced more than one distinct answer.
set -u
cd "$(dirname "$0")"
N=${1:-20}
status=0
run() { uv run --no-sync python check_determinism.py "$N" "$@" || status=1; }
run --nsides 40
run --nsides 100
run --nsides 200
run --nsides 100 --equal
run --nsides 100 --recycle
run --nsides 100 --equal --recycle
run --nsides 100 --subprocess
run --nsides 100 --equal --recycle --subprocess
run --nsides 60 --mode diagnose --redundant
run --nsides 60 --mode diagnose --redundant --subprocess
exit $status
