# Pointer-ordered parameters: a planegcs bug, not a wrapper artefact

## Question

An earlier investigation found that `planegcs-py` produces different solutions
for the same sketch from run to run, because `SubSystem::initialize()` orders
the solver's unknown vector by the *address* of each `double*` parameter.

Is that an artefact of how this Python wrapper allocates parameters, or is it
also a (latent) bug for planegcs in its original home, FreeCAD's Sketcher?

## Answer

It is a planegcs bug. The affected code in `src/planegcs` is byte-identical to
FreeCAD's copy, and FreeCAD's way of allocating parameters makes the problem
*worse*, not better: this wrapper keeps parameters in one `std::deque<double>`
(addresses mostly monotonic, only a few chunk boundaries out of order), whereas
FreeCAD allocates every parameter with a separate `new double` and frees them
all on each sketch rebuild — so the address order is essentially a fresh random
permutation on every solve.

Reconstructing FreeCAD's allocation pattern on top of the vendored solver, the
same sketch solved 20 times in one process gave **10 different results**, with
coordinates differing by up to **1.37 units on a ~10 unit polygon** — not
last-bit noise, but visibly different (equally valid) solutions of an
under-constrained sketch.

## The evidence

### 1. The solver code is the same

`src/planegcs/SubSystem.cpp` is identical to
`FreeCAD/src/Mod/Sketcher/App/planegcs/SubSystem.cpp` (`diff` reports no
difference). `GCS.cpp` has diverged slightly (this vendored copy is a little
older and has local fixes), but every pointer-ordering site below is present
verbatim in both.

### 2. FreeCAD allocates parameters as individual heap cells

`FreeCAD/src/Mod/Sketcher/App/Sketch.cpp` has 89 occurrences of:

```cpp
params.push_back(new double(p->getPoint().x));
```

and `Sketch::clear()` does:

```cpp
for (auto param : Parameters) {
    delete param;
}
```

`Sketch::setUpSketch()` calls `clear()` first, and `setUpSketch()` runs on every
sketch rebuild/recompute. The parameters handed to the solver
(`GCSsys.declareUnknowns(Parameters)`) are therefore a vector of pointers into
freshly recycled heap cells, interleaved with allocations of geometry copies,
`GCS::Point`/`Line` objects and `Constraint` objects. Their relative order has
no relationship to the order the sketch declares them in, and it changes from
one rebuild to the next.

### 3. Four places where the heap decides the maths

| # | Site | Effect |
|---|------|--------|
| 1 | `SubSystem::initialize` — `std::set_intersection` over `SET_pD` (`std::set<double*>`) builds `tmpplist` | Jacobian column order |
| 2 | `SubSystem::initialize` — `SET_pD constr_params` builds `c2p`/`p2c` | gradient accumulation order |
| 3 | `System::solve(subsysA, subsysB)` — `std::sort` + `std::set_union` on pointers | unknown order for the two-subsystem (redundant) solve |
| 4 | `SubSystem::redirectParams` — copies values into `pvals` while iterating `pmap` (`std::map<double*, double*>`) | **semantic**: after an exact-equality reduction two original parameters share one `pvals` slot, so *last write wins*, and which one is last depends on the addresses |

Sites 1–3 only perturb floating-point rounding, but in a Newton/dogleg iteration
that is enough to land on a different local solution. Site 4 is a real
ambiguity being resolved by the allocator: the merged unknown is seeded with
the value of whichever of the two equality-linked parameters happens to sit at
the higher address.

### 4. Experiment

`tools/freecad_alloc_experiment/` builds a small C++ harness directly against
the vendored planegcs sources. It builds the same sketch (12-sided polygon,
equal-length chain, a pinned corner, a horizontal side, a few diagonal
distances) repeatedly in one process and hashes the solved coordinates.

Allocation modes:

* `freecad` — one `new double` per parameter, all freed between cycles (what
  `Sketch.cpp` does)
* `interleaved` — the same, plus small unrelated allocations in between (what
  `Sketch.cpp` *actually* does, since it allocates geometry and constraints as
  it goes)
* `arena` — all parameters in one contiguous `std::vector<double>` (control:
  address order == declaration order)

`./run_experiment.sh 20` builds patch levels 0–4 (see `patch_planegcs.py`) and
solves the sketch 20 times per configuration:

```
patches=0 freecad      distinct param orderings: 20, distinct results: 10, max coord spread: 1.37
patches=0 interleaved  distinct param orderings: 20, distinct results: 11, max coord spread: 1.37
patches=0 arena        distinct param orderings: 1,  distinct results: 1,  max coord spread: 0
...
patches=4 freecad      distinct param orderings: 20, distinct results: 1,  max coord spread: 0
patches=4 interleaved  distinct param orderings: 20, distinct results: 1,  max coord spread: 0
```

Reading it:

* unpatched planegcs + FreeCAD's allocation pattern ⇒ the solution depends on
  the heap layout;
* the same code with a contiguous parameter arena is perfectly reproducible, so
  the only input that changed is the addresses;
* with all four patches applied, the shuffled addresses no longer matter.

Under `valgrind` (whose allocator hands out addresses in allocation order) the
unpatched binary is also perfectly reproducible, and valgrind reports no
uninitialised reads — further confirmation that address order, not memory
corruption, is the mechanism.

### 5. What about the redundancy diagnosis?

`./experiment N <mode> diagnose` runs the same loop on a deliberately
over-constrained sketch and prints DoF, conflicting/redundant/partially
redundant tags and the dependent-parameter list. In this test the diagnosis
was *stable*: `System::diagnose()` builds its Jacobian from `plist`, which
keeps the caller's order. That does not prove the diagnosis is immune — the
redundant-solving step inside `diagnose()` goes through sites 1–4, and
whichever constraint is reported as "the redundant one" is picked out of
`std::set<Constraint*>`/`std::map<Constraint*, …>` containers that are also
address-ordered — only that our sketch did not expose it.

FreeCAD has long-standing complaints that an unchanged sketch flips between
"redundant", "under-constrained" and "conflicting"; the FPA grant proposal
*"Make Sketcher constraint redundancy diagnosis reliable"* collects several
issues of that kind. The mechanism documented here is a plausible contributor,
but we have not demonstrated that link.

## Why this wrapper sees a milder version

`src/wrapper.h` stores all parameters in a `std::deque<double>` for pointer
stability. A deque allocates in chunks, so addresses are monotonic *within* a
chunk and only the handful of chunk boundaries can be out of order. That is
why `planegcs-py` typically flips between two or three outputs, while the
FreeCAD-style allocation produces a near-unique result per run.

## Implications for FreeCAD

* Solving the same sketch twice can produce different geometry, and the result
  depends on the process's allocation history (which sketches were edited
  before, in what order), not only on the document.
* Those coordinates are saved into the document and feed downstream features,
  so the non-determinism propagates into derived geometry and exported files.
* It makes solver regressions hard to test: any golden-value test for the
  Sketcher is intrinsically flaky.
* Site 4 can change the *starting point* of an equality-reduced unknown, which
  for under-constrained or multi-solution sketches can select a different
  branch entirely.

## Suggested upstream fix

None of these sites need an address ordering; they need *a* deterministic
order, and the caller's declaration order is the obvious one:

1. Build `tmpplist` by iterating `params` and testing membership in the
   constraint-parameter set.
2. Build `c2p`/`p2c` from a deduplicated vector instead of `SET_pD`.
3. Replace the sort + `set_union` in `System::solve(subsysA, subsysB)` with an
   order-preserving union.
4. Give `SubSystem` an ordered list of `pmap` keys and use it in
   `redirectParams()` — and ideally make the equality-reduction seeding
   explicit rather than last-write-wins.

`tools/freecad_alloc_experiment/patch_planegcs.py` implements exactly these
four changes against a copy of the sources and can be used as a starting point
for a patch to either project.

## Caveats

* The harness reconstructs FreeCAD's allocation pattern; we did not build or
  instrument FreeCAD itself. The claim it supports is "planegcs is sensitive to
  the parameter addresses it is given, and FreeCAD gives it shuffled
  addresses", which is exactly what both halves of the evidence show.
* Results are from one machine, glibc malloc, GCC 20-standard build. The
  *specific* outputs will differ elsewhere; the non-reproducibility will not.
