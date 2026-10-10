#!/bin/bash
# Build every patch level and report how reproducible the solver is for each.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
cycles="${1:-20}"
for n in 0 1 2 3 4; do
    "$here/build.sh" "$n" >/dev/null
done
echo "sketch solved $cycles times per row; 'distinct results' > 1 means non-deterministic"
for n in 0 1 2 3 4; do
    bin="$here/experiment"
    [[ "$n" != "0" ]] && bin="$here/experiment-$n"
    for mode in freecad interleaved arena; do
        printf "patches=%s %-12s " "$n" "$mode"
        "$bin" "$cycles" "$mode" solve | tail -1
    done
done
