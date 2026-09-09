#include "proofrun/sort/sort.hpp"

#include <algorithm>
#include <functional>
#include <vector>

#include <gtest/gtest.h>

namespace {

using SortFn = void (*)(std::vector<int>&, proofrun::trace::Emitter*);

void expect_sorted_with(SortFn fn, std::vector<int> input) {
  std::vector<int> expected = input;
  std::sort(expected.begin(), expected.end());
  fn(input, nullptr);
  EXPECT_EQ(input, expected);
}

class SortParamTest : public ::testing::TestWithParam<SortFn> {};

TEST_P(SortParamTest, Empty) { expect_sorted_with(GetParam(), {}); }
TEST_P(SortParamTest, Single) { expect_sorted_with(GetParam(), {42}); }
TEST_P(SortParamTest, AlreadySorted) { expect_sorted_with(GetParam(), {1, 2, 3, 4, 5}); }
TEST_P(SortParamTest, ReverseSorted) { expect_sorted_with(GetParam(), {5, 4, 3, 2, 1}); }
TEST_P(SortParamTest, Duplicates) { expect_sorted_with(GetParam(), {3, 1, 2, 1, 3, 2}); }
TEST_P(SortParamTest, Negatives) { expect_sorted_with(GetParam(), {-2, -5, 0, 3, -1}); }
TEST_P(SortParamTest, RepeatedValues) { expect_sorted_with(GetParam(), {7, 7, 7, 7}); }
TEST_P(SortParamTest, SmallRandom) {
  expect_sorted_with(GetParam(), {9, -4, 2, 2, 0, 15, -9, 8});
}
TEST_P(SortParamTest, LargerRandom) {
  std::vector<int> v;
  for (int i = 0; i < 200; ++i) v.push_back((i * 37 + 11) % 97 - 40);
  expect_sorted_with(GetParam(), v);
}

INSTANTIATE_TEST_SUITE_P(
    SortingAlgos, SortParamTest,
    ::testing::Values(&proofrun::sort::bubble_sort, &proofrun::sort::insertion_sort,
                      &proofrun::sort::selection_sort, &proofrun::sort::merge_sort,
                      &proofrun::sort::quick_sort));

TEST(SortFaultInjection, IncorrectImplementationIsDetected) {
  auto broken = [](std::vector<int>& a, proofrun::trace::Emitter*) {
    // Intentionally incorrect: only partially orders.
    if (a.size() >= 2 && a[0] > a[1]) std::swap(a[0], a[1]);
  };
  std::vector<int> input{3, 1, 2};
  std::vector<int> expected = input;
  std::sort(expected.begin(), expected.end());
  broken(input, nullptr);
  EXPECT_NE(input, expected);
}

TEST(TraceEvents, BubbleEmitsInitAndDone) {
  std::vector<int> a{3, 1, 2};
  proofrun::trace::Emitter em;
  em.set_enabled(true);
  em.set_meta("sort.bubblesort", "test", 1);
  em.set_manifest("Bubble Sort", "O(n)", "O(n^2)", "O(n^2)", "O(1)", "test");
  em.set_initial_array(a);
  proofrun::sort::bubble_sort(a, &em);
  const std::string json = em.to_json();
  EXPECT_NE(json.find("\"type\":\"init\""), std::string::npos);
  EXPECT_NE(json.find("\"type\":\"done\""), std::string::npos);
  EXPECT_EQ(a, (std::vector<int>{1, 2, 3}));
}

}  // namespace
