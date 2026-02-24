#!/bin/sh

python -m pybind11_stubgen planegcs._planegcs --enum-class-locations 'Algorithm:planegcs._planegcs' -o python
ruff format python/planegcs/_planegcs.pyi
ruff check --fix python/planegcs/_planegcs.pyi
