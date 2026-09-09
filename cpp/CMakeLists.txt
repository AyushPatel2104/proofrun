cmake_minimum_required(VERSION 3.16)
project(proofrun_cpp VERSION 0.1.0 LANGUAGES CXX)

if(POLICY CMP0135)
  cmake_policy(SET CMP0135 NEW)
endif()

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

option(PROOFRUN_BUILD_TESTS "Build GoogleTest suite" ON)
option(PROOFRUN_BUILD_BENCH "Build Google Benchmark suite" ON)

# Regenerate catalog header from catalogs/algorithms.json (single source of truth).
find_package(Python3 COMPONENTS Interpreter REQUIRED)
set(PROOFRUN_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/..")
set(PROOFRUN_CATALOG_JSON "${PROOFRUN_ROOT}/catalogs/algorithms.json")
set(PROOFRUN_CATALOG_HEADER "${CMAKE_CURRENT_SOURCE_DIR}/include/proofrun/catalog/generated_algorithms.hpp")
set(PROOFRUN_CATALOG_SCRIPT "${PROOFRUN_ROOT}/scripts/generate_catalog_artifacts.py")
add_custom_target(proofrun_catalog
  COMMAND "${Python3_EXECUTABLE}" "${PROOFRUN_CATALOG_SCRIPT}" --root "${PROOFRUN_ROOT}"
  DEPENDS "${PROOFRUN_CATALOG_JSON}" "${PROOFRUN_CATALOG_SCRIPT}"
  BYPRODUCTS "${PROOFRUN_CATALOG_HEADER}"
  COMMENT "Generating algorithm catalog header"
  VERBATIM
)

include(FetchContent)
set(FETCHCONTENT_QUIET OFF)

FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/archive/refs/tags/v1.14.0.zip
)
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)

FetchContent_Declare(
  benchmark
  URL https://github.com/google/benchmark/archive/refs/tags/v1.8.3.zip
)
set(BENCHMARK_ENABLE_TESTING OFF CACHE BOOL "" FORCE)
set(BENCHMARK_ENABLE_GTEST_TESTS OFF CACHE BOOL "" FORCE)

if(PROOFRUN_BUILD_TESTS)
  FetchContent_MakeAvailable(googletest)
endif()
if(PROOFRUN_BUILD_BENCH)
  FetchContent_MakeAvailable(benchmark)
endif()

add_library(proofrun_core
  src/sort/sort.cpp
  src/search/search.cpp
  src/array/array.cpp
  src/trace/event.cpp
)
add_dependencies(proofrun_core proofrun_catalog)
target_include_directories(proofrun_core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)

add_executable(proofrun_cli src/tools/proofrun_cli.cpp)
add_dependencies(proofrun_cli proofrun_catalog)
target_link_libraries(proofrun_cli PRIVATE proofrun_core)

if(PROOFRUN_BUILD_TESTS)
  enable_testing()
  include(GoogleTest)
  add_executable(proofrun_sort_tests tests/sort/sort_test.cpp)
  target_link_libraries(proofrun_sort_tests PRIVATE proofrun_core GTest::gtest_main)
  gtest_discover_tests(proofrun_sort_tests)

  add_executable(proofrun_search_tests tests/search/search_test.cpp)
  target_link_libraries(proofrun_search_tests PRIVATE proofrun_core GTest::gtest_main)
  gtest_discover_tests(proofrun_search_tests)

  add_executable(proofrun_array_tests tests/array/array_test.cpp)
  target_link_libraries(proofrun_array_tests PRIVATE proofrun_core GTest::gtest_main)
  gtest_discover_tests(proofrun_array_tests)
endif()

if(PROOFRUN_BUILD_BENCH)
  add_executable(proofrun_sort_bench benches/sort_bench.cpp)
  target_link_libraries(proofrun_sort_bench PRIVATE proofrun_core benchmark::benchmark)

  add_executable(proofrun_search_array_bench benches/search_array_bench.cpp)
  target_link_libraries(proofrun_search_array_bench PRIVATE proofrun_core benchmark::benchmark)
endif()
