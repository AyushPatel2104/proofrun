#include "proofrun/array/array.hpp"
#include "proofrun/search/search.hpp"

#include <benchmark/benchmark.h>

#include <algorithm>
#include <cstdint>
#include <vector>

namespace {

std::vector<int> make_input(std::size_t n, std::uint64_t seed) {
  std::vector<int> v;
  v.reserve(n);
  std::uint64_t state = seed ? seed : 0x9e3779b97f4a7c15ULL;
  for (std::size_t i = 0; i < n; ++i) {
    state = state * 6364136223846793005ULL + 1ULL;
    v.push_back(static_cast<int>((state >> 33) % 100000ULL) - 50000);
  }
  return v;
}

}  // namespace

static void BM_LinearSearch(benchmark::State& state) {
  const std::size_t n = static_cast<std::size_t>(state.range(0));
  auto data = make_input(n, 42);
  const int target = data.back();  // always present (worst-ish late find if shuffled)
  for (auto _ : state) {
    int idx = proofrun::search::linear_search(data, target, nullptr);
    benchmark::DoNotOptimize(idx);
  }
  state.SetItemsProcessed(state.iterations() * static_cast<std::int64_t>(n));
}

static void BM_BinarySearch(benchmark::State& state) {
  const std::size_t n = static_cast<std::size_t>(state.range(0));
  auto data = make_input(n, 42);
  std::sort(data.begin(), data.end());
  const int target = data[n / 2];
  for (auto _ : state) {
    int idx = proofrun::search::binary_search(data, target, nullptr);
    benchmark::DoNotOptimize(idx);
  }
  state.SetItemsProcessed(state.iterations() * static_cast<std::int64_t>(n));
}

static void BM_TwoSumSorted(benchmark::State& state) {
  const std::size_t n = static_cast<std::size_t>(state.range(0));
  auto data = make_input(n, 7);
  std::sort(data.begin(), data.end());
  const int target = data.front() + data.back();
  for (auto _ : state) {
    auto r = proofrun::array::two_sum_sorted(data, target, nullptr);
    benchmark::DoNotOptimize(r.found);
  }
  state.SetItemsProcessed(state.iterations() * static_cast<std::int64_t>(n));
}

static void BM_SlidingWindow(benchmark::State& state) {
  const std::size_t n = static_cast<std::size_t>(state.range(0));
  auto data = make_input(n, 11);
  const int k = static_cast<int>(std::max<std::size_t>(1, n / 8));
  for (auto _ : state) {
    auto r = proofrun::array::max_sum_fixed_window(data, k, nullptr);
    benchmark::DoNotOptimize(r.max_sum);
  }
  state.SetItemsProcessed(state.iterations() * static_cast<std::int64_t>(n));
}

static void BM_PrefixRange(benchmark::State& state) {
  const std::size_t n = static_cast<std::size_t>(state.range(0));
  auto data = make_input(n, 13);
  for (auto _ : state) {
    auto r = proofrun::array::range_sum_prefix(data, 0, static_cast<int>(n) - 1, nullptr);
    benchmark::DoNotOptimize(r.sum);
  }
  state.SetItemsProcessed(state.iterations() * static_cast<std::int64_t>(n));
}

BENCHMARK(BM_LinearSearch)->Arg(256)->Arg(1024)->Arg(4096)->Arg(16384);
BENCHMARK(BM_BinarySearch)->Arg(256)->Arg(1024)->Arg(4096)->Arg(16384);
BENCHMARK(BM_TwoSumSorted)->Arg(256)->Arg(1024)->Arg(4096);
BENCHMARK(BM_SlidingWindow)->Arg(256)->Arg(1024)->Arg(4096);
BENCHMARK(BM_PrefixRange)->Arg(256)->Arg(1024)->Arg(4096);

BENCHMARK_MAIN();
