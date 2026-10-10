#!/bin/bash
# Build the FreeCAD-allocation-pattern experiment against the vendored planegcs.
#
#   ./build.sh       -> ./experiment     (planegcs exactly as vendored)
#   ./build.sh N     -> ./experiment-N   (first N determinism patches applied
#                                         to a copy of the sources; see
#                                         patch_planegcs.py).  N = 1..4
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
root="$here/../.."
n="${1:-0}"

if [[ "$n" == "0" ]]; then
    srcdir="$root/src/planegcs"
    out="$here/experiment"
else
    srcdir="$here/build-$n/planegcs"
    out="$here/experiment-$n"
    rm -rf "$here/build-$n"
    mkdir -p "$here/build-$n"
    cp -r "$root/src/planegcs" "$srcdir"
    python3 "$here/patch_planegcs.py" "$srcdir" "$n"
fi

g++ -std=c++20 -O2 -g -o "$out" \
    "$here/main.cpp" \
    "$srcdir/Constraints.cpp" "$srcdir/GCS.cpp" "$srcdir/Geo.cpp" \
    "$srcdir/SubSystem.cpp" "$srcdir/qp_eq.cpp" \
    -I"$srcdir" -I"$srcdir/shims" -I/usr/include/eigen3 -w
echo "built $out"
