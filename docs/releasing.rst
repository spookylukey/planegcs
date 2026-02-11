Releasing
=========

This document describes how to make a new release of **planegcs**.

Overview
--------

Releases are built using `cibuildwheel <https://cibuildwheel.pypa.io/>`_ in
GitHub Actions and published to PyPI.  The workflow is triggered manually from
the GitHub Actions UI.

What gets built:

* **Platforms:** Linux (manylinux, x86_64) and Windows (x86_64)
* **Python versions:** 3.12 and 3.13
* **Artifacts:** platform wheels + source distribution (sdist)

Step-by-step release process
----------------------------

The ``release.sh`` script automates the local steps (version bump, commit, tag,
push).  Run it from the repository root:

.. code-block:: bash

   ./release.sh <bump>

where ``<bump>`` is the argument passed to ``uv version --bump`` — typically one
of ``major``, ``minor``, or ``patch``.

We roughly follow `Semantic Versioning <https://semver.org/>`_:

* **MAJOR** — incompatible API changes
* **MINOR** — new functionality, backwards-compatible
* **PATCH** — backwards-compatible bug fixes

The script will:

1. Check that the working tree is clean and you are on ``main``.
2. Bump the version in ``pyproject.toml``.
3. Commit the change and push to ``origin main``.
4. Create a ``vX.Y.Z`` tag and push it.
5. Open the GitHub Actions workflow page (or print the URL) so you can trigger
   the build.

Triggering the release workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After the script finishes, trigger the build on GitHub Actions:

1. Go to https://github.com/spookylukey/planegcs/actions/workflows/release.yml
   (the script will try to open this for you).
2. Click **Run workflow**.
3. Choose the ``main`` branch.
4. Click **Run workflow**.

The workflow will:

* Build wheels for Linux and Windows.
* Build a source distribution.
* Run the test suite against each wheel.
* If ``upload_to_pypi`` was ``true``, publish everything to PyPI.


PyPI authentication
-------------------

The publish step uses **PyPI trusted publishing** (OpenID Connect).  This
requires one-time setup on PyPI:

1. Go to https://pypi.org/manage/project/planegcs/settings/publishing/
2. Add a new **GitHub** trusted publisher:

   * **Owner:** ``<your GitHub username>``  (or your GitHub org/username)
   * **Repository:** ``planegcs``
   * **Workflow name:** ``release.yml``
   * **Environment name:** ``pypi``

Once configured, the workflow can publish without any API tokens or passwords.

.. note::

   If you prefer to use a PyPI API token instead of trusted publishing,
   store the token as a GitHub Actions secret named ``PYPI_API_TOKEN`` and
   replace the publish step in ``.github/workflows/release.yml`` with:

   .. code-block:: yaml

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}

Troubleshooting
---------------

**Wheels fail to build on Windows**
    Check that ``vcpkg`` can install the dependencies.  The GitHub Actions
    ``windows-latest`` runner has ``vcpkg`` pre-installed.  The workflow runs
    ``vcpkg install eigen3:x64-windows boost-graph:x64-windows
    boost-math:x64-windows`` before building.

**Wheels fail to build on Linux**
    The manylinux container uses ``yum``.  The ``before-all`` command tries
    ``yum`` first, then falls back to ``apt-get``.

**Tests fail in cibuildwheel**
    cibuildwheel installs the built wheel into a fresh virtualenv and runs
    ``pytest {project}/tests -x``.  Check the test output in the workflow logs.

**Version mismatch**
    The version lives in ``pyproject.toml``.  The ``release.sh`` script uses
    ``uv version --bump`` to update it automatically.

File reference
--------------

* ``release.sh`` — automates version bump, commit, tag, and push
* ``.github/workflows/release.yml`` — the release workflow
* ``.github/workflows/ci.yml`` — CI workflow (runs tests on push/PR)
* ``pyproject.toml`` — build config including ``[tool.cibuildwheel]`` settings
* ``CMakeLists.txt`` — CMake build (cross-platform, supports MSVC and GCC/Clang)
