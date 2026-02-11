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

1. Bump the version number
~~~~~~~~~~~~~~~~~~~~~~~~~~

Use ``uv version --bump`` e.g. ``uv version --bump patch``

We roughly follow `Semantic Versioning <https://semver.org/>`_:

* **MAJOR** — incompatible API changes
* **MINOR** — new functionality, backwards-compatible
* **PATCH** — backwards-compatible bug fixes

2. Commit and push
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   git add pyproject.toml
   git commit -m "Bump version to X.Y.Z"
   git push origin main

3. Create a Git tag
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   git tag vX.Y.Z
   git push origin vX.Y.Z

4. Run the release workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Go to https://github.com/spookylukey/planegcs/actions/workflows/release.yml
2. Click **Run workflow**.
3. Choose the ``main`` branch.
4. Click **Run workflow**.

The workflow will:

* Build wheels for Linux and Windows.
* Build a source distribution.
* Run the test suite against each wheel.
* If ``upload_to_pypi`` was ``true``, publish everything to PyPI.

5. Create a GitHub Release (optional but recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After the workflow succeeds:

1. Go to **Releases** → **Draft a new release**.
2. Select the ``vX.Y.Z`` tag.
3. Write release notes (or click **Generate release notes**).
4. Download the wheel and sdist artifacts from the workflow run and attach
   them to the release.
5. Click **Publish release**.

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
    If the version in ``pyproject.toml`` and ``python/planegcs/__init__.py``
    don't match, the package metadata will be inconsistent.  Always update
    both files together.

File reference
--------------

* ``.github/workflows/release.yml`` — the release workflow
* ``.github/workflows/ci.yml`` — CI workflow (runs tests on push/PR)
* ``pyproject.toml`` — build config including ``[tool.cibuildwheel]`` settings
* ``CMakeLists.txt`` — CMake build (cross-platform, supports MSVC and GCC/Clang)
