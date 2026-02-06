cmake_minimum_required(VERSION 3.15)
project(planegcs LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(pybind11 REQUIRED)
find_package(Eigen3 REQUIRED NO_MODULE)
find_package(Boost REQUIRED)

# PlaneGCS solver sources
set(PLANEGCS_SOURCES
    src/planegcs/Constraints.cpp
    src/planegcs/GCS.cpp
    src/planegcs/Geo.cpp
    src/planegcs/SubSystem.cpp
    src/planegcs/qp_eq.cpp
)

pybind11_add_module(_planegcs
    src/bindings.cpp
    ${PLANEGCS_SOURCES}
)

target_include_directories(_planegcs PRIVATE
    src/planegcs
    src/planegcs/shims
    ${Boost_INCLUDE_DIRS}
)

target_link_libraries(_planegcs PRIVATE
    Eigen3::Eigen
)

# Suppress warnings from FreeCAD code
target_compile_options(_planegcs PRIVATE
    -Wno-unused-parameter
    -Wno-missing-field-initializers
    -Wno-sign-compare
)

install(TARGETS _planegcs LIBRARY DESTINATION planegcs)
