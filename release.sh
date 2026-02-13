#!/usr/bin/env bash
set -euo pipefail

RELEASE_WORKFLOW_URL="https://github.com/spookylukey/planegcs/actions/workflows/release.yml"

# --- helpers ----------------------------------------------------------------

die()  { echo "ERROR: $*" >&2; exit 1; }
info() { echo "==> $*"; }

open_url() {
    local url="$1"
    # Try common GUI openers; fall back to printing the URL.
    if command -v xdg-open &>/dev/null; then
        xdg-open "$url" 2>/dev/null &
    elif command -v open &>/dev/null; then      # macOS
        open "$url"
    elif command -v wslview &>/dev/null; then    # WSL
        wslview "$url"
    else
        echo "    Open this URL in your browser:"
        echo "      $url"
        return
    fi
    echo "    Opened $url"
}

# --- pre-flight checks ------------------------------------------------------

[[ $# -eq 1 ]] || die "Usage: $0 <bump>  (e.g. major, minor, patch, ...)"
BUMP="$1"

command -v uv  &>/dev/null || die "'uv' not found — install it first"
command -v git &>/dev/null || die "'git' not found"

# Must be in the repo root (where pyproject.toml lives)
[[ -f pyproject.toml ]] || die "Run this script from the repository root"

# Working tree must be clean
if ! git diff --quiet || ! git diff --cached --quiet; then
    die "Working tree is dirty — commit or stash changes first"
fi

# Must be on main
BRANCH=$(git rev-parse --abbrev-ref HEAD)
[[ "$BRANCH" == "main" ]] || die "You are on '$BRANCH' — switch to 'main' first"

# --- run tests and type checking --------------------------------------------

info "Running tests with coverage …"
uv run pytest -x -q --cov --cov-fail-under=100 \
    || die "Tests failed — fix before releasing"

info "Running ty type checker …"
ty check \
    || die "Type checking failed — fix before releasing"

# --- verify type stubs are up to date ---------------------------------------

info "Checking _planegcs.pyi is up to date …"
uv run pytest tests/test_stubs.py -x -q \
    || die "Type stubs are out of date — regenerate with:\n" \
           "  python -m pybind11_stubgen planegcs._planegcs" \
           "    --enum-class-locations 'Algorithm:planegcs._planegcs' -o python\n" \
           "  ruff check --fix python/planegcs/_planegcs.pyi\n" \
           "  ruff format python/planegcs/_planegcs.pyi"

# --- step 1: bump version ---------------------------------------------------

info "Bumping version (uv version --bump $BUMP) …"
uv version --bump "$BUMP"
NEW_VERSION=$(uv version --short)          # reads back the version from pyproject.toml
TAG="v${NEW_VERSION}"

info "New version: $NEW_VERSION  (tag: $TAG)"

# --- step 2: commit and push ------------------------------------------------

info "Committing and pushing …"
git add pyproject.toml
git commit -m "Bump version to $NEW_VERSION"
git push origin main

# --- step 3: tag and push tag -----------------------------------------------

info "Creating and pushing tag $TAG …"
git tag "$TAG"
git push origin "$TAG"

# --- step 4: trigger the release workflow ------------------------------------

echo
info "All local steps done!"
echo
echo "Next: trigger the release workflow on GitHub Actions:"
echo "  1. Go to the workflow page."
echo "  2. Click 'Run workflow', choose the 'main' branch."
echo "  3. Click 'Run workflow' to start the build."
echo
open_url "$RELEASE_WORKFLOW_URL"
