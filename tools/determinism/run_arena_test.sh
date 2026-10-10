#!/bin/bash
# Compile and run the C++ unit test for src/param_arena.h.
set -eu
cd "$(dirname "$0")"
out=$(mktemp -d)/test_param_arena
${CXX:-g++} -std=c++20 -O2 -Wall -Wextra -fsanitize=address,undefined \
    -o "$out" test_param_arena.cpp
"$out"
