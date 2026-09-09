#include "proofrun/sort/sort.hpp"

#include <benchmark/benchmark.h>

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

template <typename Fn>
void BenchSort(benchmark::State& state, Fn fn) {
  const std::size_t n = static_cast<std::size_t>(state.range(0));
  const auto base = make_input(n, 42);
  for (auto _ : state) {
    auto data = base;
    fn(data, nullptr);
    benchmark::DoNotOptimize(data.data());
    benchmark::ClobberMemory();
  }
  state.SetItemsProcessed(state.iterations() * static_cast<std::int64_t>(n));
}

}  // namespace

static void BM_Bubble(benchmark::State& st) {
  BenchSort(st, proofrun::sort::bubble_sort);
}
static void BM_Insertion(benchmark::State& st) {
  BenchSort(st, proofrun::sort::insertion_sort);
}
static void BM_Selection(benchmark::State& st) {
  BenchSort(st, proofrun::sort::selection_sort);
}
static void BM_Merge(benchmark::State& st) {
  BenchSort(st, proofrun::sort::merge_sort);
}
static void BM_Quick(benchmark::State& st) {
  BenchSort(st, proofrun::sort::quick_sort);
}

BENCHMARK(BM_Bubble)->Arg(64)->Arg(256)->Arg(1024);
BENCHMARK(BM_Insertion)->Arg(64)->Arg(256)->Arg(1024);
BENCHMARK(BM_Selection)->Arg(64)->Arg(256)->Arg(1024);
BENCHMARK(BM_Merge)->Arg(64)->Arg(256)->Arg(1024)->Arg(4096);
BENCHMARK(BM_Quick)->Arg(64)->Arg(256)->Arg(1024)->Arg(4096);

BENCHMARK_MAIN();
