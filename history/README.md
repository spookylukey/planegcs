
# History of project

This project was created almost entirely using coding agents.

For the record, the process looked roughly as follows:


Using [exe.dev](https://exe.dev/), I started a fresh VM.

I then promped the Shelley coding agent like this:

> Make a checkout of the FreeCAD source code from https://github.com/FreeCAD/Fr

Then:

> I want to re-use a significant chunk of functionality from FreeCAD, specifically the 2D sketcher component with constraint solver. My plan is to be able to programmatically create equivalent sketches using functions from this code.
>
> To get started, first you will ensure that we have all relevant build tools installed, for Linux, and ensure we can compile FreeCAD, by consulting the developer documentation and running the relevant commands.
>
> Then locate tests that exercise this code. Then, using these tests as a starting point, make a standalone executable written in C++ that uses this code to create a “sketch” and solve it. For example, it could be a triangle that has one side of defined length, and the other two defined using constraints (e.g. equal to the first side).
>
> The executable should solve the sketch, then print out the coordinates of the points.
>
> Use a PLAN.md file to keep track of progress and iterate until done.

This resulted in PLAN_01.md, which the agent worked through successfully, creating a repo with a standalone C++ library and a small driver program. I prompted it a few more times to create some more examples to be sure it worked.

As a second phase, I created the Python wrapper, using prompts like the following:

> I want to create a standalone library with Python wrappers, so that I can easily write equivalent code using Python. The library must support all the constraint operations available in the FreeCAD sketcher component.
>
> Consider the options for wrapping a C++ library with Python, and make a recommendation. Give links to tool repos.

After the response we settled on pybind11 and I prompted it to continue in a new session:

> `sketch-solver` is a subset of the FreeCAD functionality, specifically the constraint solver from the Sketcher component - see PLAN.md for what we did before.
>
> Now, I want a Python wrapper for it so I can use it as a library. Use pybind11 to wrap the C++ code.
>
> Include some test files that will demonstrate that the wrapper actually works. The end goal is a Python package that I will be able to upload to PyPI and install. If relevant, choose modern tools like `uv` for package management. Create docs using Sphinx. Create a plan in WRAPPER_PLAN.md, use it to iterate until done.

The resulting plans are in `PLAN_02a.md` and `PLAN_02b.md` (got a bit confused).
This also completed successfully, with the work being done in a fresh repo (this one).
