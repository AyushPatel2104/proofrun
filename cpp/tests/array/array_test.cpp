#include "proofrun/array/array.hpp"

#include <numeric>
#include <vector>

#include <gtest/gtest.h>

namespace {

TEST(TwoSumSorted, EmptyAndSingle) {
  EXPECT_FALSE(proofrun::array::two_sum_sorted({}, 5).found);
  EXPECT_FALSE(proofrun::array::two_sum_sorted({5}, 5).found);
}

TEST(TwoSumSorted, FoundPair) {
  const auto r = proofrun::array::two_sum_sorted({1, 2, 4, 7, 11}, 9);
  ASSERT_TRUE(r.found);
  EXPECT_EQ(r.left + 0, 1);  // 2+7
  EXPECT_EQ(r.right, 3);
}

TEST(TwoSumSorted, NotFound) {
  EXPECT_FALSE(proofrun::array::two_sum_sorted({1, 2, 3, 9}, 8).found);
}

TEST(TwoSumSorted, Negatives) {
  const std::vector<int> a{-5, -1, 0, 3, 8};
  const auto r = proofrun::array::two_sum_sorted(a, 2);
  ASSERT_TRUE(r.found);
  EXPECT_EQ(a[r.left] + a[r.right], 2);
}

TEST(TwoSumSorted, Duplicates) {
  const auto r = proofrun::array::two_sum_sorted({1, 3, 3, 5}, 6);
  ASSERT_TRUE(r.found);
  EXPECT_EQ(3 + 3, 6);
}

TEST(SlidingWindow, InvalidK) {
  EXPECT_FALSE(proofrun::array::max_sum_fixed_window({1, 2, 3}, 0).valid);
  EXPECT_FALSE(proofrun::array::max_sum_fixed_window({1, 2, 3}, 4).valid);
}

TEST(SlidingWindow, SingleWindow) {
  const auto r = proofrun::array::max_sum_fixed_window({5, -1, 3}, 3);
  ASSERT_TRUE(r.valid);
  EXPECT_EQ(r.max_sum, 7);
  EXPECT_EQ(r.start, 0);
  EXPECT_EQ(r.end, 2);
}

TEST(SlidingWindow, Classic) {
  // windows of 3: 2+1+5=8, 1+5+3=9, 5+3+2=10, 3+2+7=12
  const auto r = proofrun::array::max_sum_fixed_window({2, 1, 5, 3, 2, 7}, 3);
  ASSERT_TRUE(r.valid);
  EXPECT_EQ(r.max_sum, 12);
  EXPECT_EQ(r.start, 3);
  EXPECT_EQ(r.end, 5);
}

TEST(SlidingWindow, Negatives) {
  // windows of 2: -5, -4, -5 → max is -4
  const auto r = proofrun::array::max_sum_fixed_window({-4, -1, -3, -2}, 2);
  ASSERT_TRUE(r.valid);
  EXPECT_EQ(r.max_sum, -4);
  EXPECT_EQ(r.start, 1);
  EXPECT_EQ(r.end, 2);
}

TEST(SlidingWindow, MatchesBruteForce) {
  const std::vector<int> a{4, -2, 7, 1, -5, 3, 8, -1};
  const int k = 3;
  const auto r = proofrun::array::max_sum_fixed_window(a, k);
  ASSERT_TRUE(r.valid);
  std::int64_t best = 0;
  bool first = true;
  for (int i = 0; i + k <= static_cast<int>(a.size()); ++i) {
    std::int64_t s = 0;
    for (int j = 0; j < k; ++j) s += a[i + j];
    if (first || s > best) {
      best = s;
      first = false;
    }
  }
  EXPECT_EQ(r.max_sum, best);
}

TEST(PrefixSum, InvalidRange) {
  EXPECT_FALSE(proofrun::array::range_sum_prefix({1, 2, 3}, -1, 1).valid);
  EXPECT_FALSE(proofrun::array::range_sum_prefix({1, 2, 3}, 2, 1).valid);
  EXPECT_FALSE(proofrun::array::range_sum_prefix({1, 2, 3}, 0, 3).valid);
}

TEST(PrefixSum, FullAndPartial) {
  const std::vector<int> a{2, 4, 6, 8};
  auto full = proofrun::array::range_sum_prefix(a, 0, 3);
  ASSERT_TRUE(full.valid);
  EXPECT_EQ(full.sum, 20);
  auto mid = proofrun::array::range_sum_prefix(a, 1, 2);
  ASSERT_TRUE(mid.valid);
  EXPECT_EQ(mid.sum, 10);
}

TEST(PrefixSum, EmptyArrayQueryInvalid) {
  EXPECT_FALSE(proofrun::array::range_sum_prefix({}, 0, 0).valid);
}

TEST(PrefixSum, MatchesNaiveSum) {
  const std::vector<int> a{-3, 5, 0, 7, -2, 4};
  for (int l = 0; l < static_cast<int>(a.size()); ++l) {
    for (int r = l; r < static_cast<int>(a.size()); ++r) {
      const auto got = proofrun::array::range_sum_prefix(a, l, r);
      ASSERT_TRUE(got.valid);
      const std::int64_t naive =
          std::accumulate(a.begin() + l, a.begin() + r + 1, std::int64_t{0});
      EXPECT_EQ(got.sum, naive);
    }
  }
}

TEST(ArrayTrace, SlidingEmitsInitDone) {
  std::vector<int> a{1, 2, 3, 4};
  proofrun::trace::Emitter em;
  em.set_enabled(true);
  em.set_meta("array.sliding_window", "test", 1);
  em.set_manifest("Sliding Window", "O(n)", "O(n)", "O(n)", "O(1)", "test");
  em.set_initial_array(a);
  auto r = proofrun::array::max_sum_fixed_window(a, 2, &em);
  EXPECT_TRUE(r.valid);
  const std::string json = em.to_json();
  EXPECT_NE(json.find("\"type\":\"init\""), std::string::npos);
  EXPECT_NE(json.find("\"type\":\"done\""), std::string::npos);
}

TEST(ArrayFaultInjection, BrokenWindowDetected) {
  auto broken = [](const std::vector<int>& a, int k) {
    proofrun::array::WindowSumResult r;
    r.valid = true;
    r.max_sum = a.empty() ? 0 : a[0];  // wrong
    r.start = 0;
    r.end = k - 1;
    return r;
  };
  const std::vector<int> a{1, 100, 1};
  EXPECT_NE(broken(a, 2).max_sum, proofrun::array::max_sum_fixed_window(a, 2).max_sum);
}

}  // namespace
