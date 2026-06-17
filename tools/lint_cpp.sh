#!/usr/bin/env bash
# Lint the C++ wrapper code (src/wrapper.h and src/bindings.cpp)
# using cppcheck and clang-tidy.
#
# Usage:
#   ./tools/lint_cpp.sh              # run both tools
#   ./tools/lint_cpp.sh cppcheck     # run only cppcheck
#   ./tools/lint_cpp.sh clang-tidy   # run only clang-tidy
#
# Prerequisites:
#   sudo apt-get install cppcheck clang-tidy
#   A compile_commands.json must exist (see below for generation).

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WRAPPER_FILES=("$ROOT/src/wrapper.h" "$ROOT/src/bindings.cpp")

run_tool="${1:-all}"
rc=0

# ── cppcheck ──────────────────────────────────────────────────────────
run_cppcheck() {
    echo "=== cppcheck ==="
    if ! command -v cppcheck &>/dev/null; then
        echo "ERROR: cppcheck not found. Install with: sudo apt-get install cppcheck" >&2
        return 1
    fi
    cppcheck \
        --enable=warning,style,performance,portability \
        --std=c++20 \
        --suppress=missingIncludeSystem \
        --suppress='*:*/planegcs/*' \
        -I "$ROOT/src" \
        -I "$ROOT/src/planegcs" \
        -I "$ROOT/src/planegcs/shims" \
        --error-exitcode=1 \
        "${WRAPPER_FILES[@]}" \
        2>&1
}

# ── clang-tidy ────────────────────────────────────────────────────────
run_clang_tidy() {
    echo "=== clang-tidy ==="
    if ! command -v clang-tidy &>/dev/null; then
        echo "ERROR: clang-tidy not found. Install with: sudo apt-get install clang-tidy" >&2
        return 1
    fi

    # Generate compile_commands.json if missing
    BUILD_DIR="$ROOT/build_lint"
    if [ ! -f "$BUILD_DIR/compile_commands.json" ]; then
        echo "Generating compile_commands.json..."
        # Locate pybind11's cmake dir.  We avoid "uv run" here because it
        # triggers a full project build (which itself needs pybind11 — circular).
        # Instead, use the venv's python directly, then fall back to bare python3.
        VENV_PYTHON="$ROOT/.venv/bin/python3"
        PYBIND11_DIR=$(
            "$VENV_PYTHON" -c "import pybind11; print(pybind11.get_cmake_dir())" 2>/dev/null \
            || python3 -c "import pybind11; print(pybind11.get_cmake_dir())" 2>/dev/null \
            || echo ""
        )
        cmake_args=(-S "$ROOT" -B "$BUILD_DIR" -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -Wno-dev)
        if [ -n "$PYBIND11_DIR" ]; then
            cmake_args+=(-Dpybind11_DIR="$PYBIND11_DIR")
        fi
        cmake "${cmake_args[@]}"
    fi

    if [ ! -f "$BUILD_DIR/compile_commands.json" ]; then
        echo "ERROR: Failed to generate compile_commands.json" >&2
        return 1
    fi

    clang-tidy -p "$BUILD_DIR" "$ROOT/src/bindings.cpp"
}

# ── Main ──────────────────────────────────────────────────────────────
case "$run_tool" in
    cppcheck)
        run_cppcheck || rc=1
        ;;
    clang-tidy)
        run_clang_tidy || rc=1
        ;;
    all)
        run_cppcheck || rc=1
        echo ""
        run_clang_tidy || rc=1
        ;;
    *)
        echo "Usage: $0 [cppcheck|clang-tidy|all]" >&2
        exit 1
        ;;
esac

if [ $rc -eq 0 ]; then
    echo ""
    echo "All C++ lint checks passed."
fi
exit $rc
