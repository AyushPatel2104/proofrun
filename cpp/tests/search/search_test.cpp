#include "proofrun/search/search.hpp"

#include <algorithm>
#include <vector>

#include <gtest/gtest.h>

namespace {

TEST(LinearSearch, Empty) {
  EXPECT_EQ(proofrun::search::linear_search({}, 1), -1);
}

TEST(LinearSearch, SingleFound) {
  EXPECT_EQ(proofrun::search::linear_search({7}, 7), 0);
}

TEST(LinearSearch, SingleMissing) {
  EXPECT_EQ(proofrun::search::linear_search({7}, 3), -1);
}

TEST(LinearSearch, FirstMatch) {
  EXPECT_EQ(proofrun::search::linear_search({1, 2, 2, 3}, 2), 1);
}

TEST(LinearSearch, Negatives) {
  EXPECT_EQ(proofrun::search::linear_search({-5, -1, 0, 4}, -1), 1);
}

TEST(LinearSearch, NotFound) {
  EXPECT_EQ(proofrun::search::linear_search({1, 3, 5}, 4), -1);
}

TEST(BinarySearch, Empty) {
  EXPECT_EQ(proofrun::search::binary_search({}, 1), -1);
}

TEST(BinarySearch, Single) {
  EXPECT_EQ(proofrun::search::binary_search({5}, 5), 0);
  EXPECT_EQ(proofrun::search::binary_search({5}, 1), -1);
}

TEST(BinarySearch, FoundAndMissing) {
  const std::vector<int> a{1, 3, 5, 7, 9};
  EXPECT_EQ(proofrun::search::binary_search(a, 1), 0);
  EXPECT_EQ(proofrun::search::binary_search(a, 9), 4);
  EXPECT_EQ(proofrun::search::binary_search(a, 5), 2);
  EXPECT_EQ(proofrun::search::binary_search(a, 4), -1);
}

TEST(BinarySearch, DuplicatesReturnsSomeIndex) {
  const std::vector<int> a{1, 2, 2, 2, 5};
  const int idx = proofrun::search::binary_search(a, 2);
  ASSERT_GE(idx, 0);
  EXPECT_EQ(a[idx], 2);
}

TEST(BinarySearch, Negatives) {
  const std::vector<int> a{-9, -3, 0, 4};
  EXPECT_EQ(proofrun::search::binary_search(a, -3), 1);
}

TEST(BinarySearch, PropertyMatchesPresence) {
  std::vector<int> a;
  for (int i = 0; i < 100; ++i) a.push_back((i * 7) % 50 - 10);
  std::sort(a.begin(), a.end());
  for (int t = -15; t <= 45; ++t) {
    const int idx = proofrun::search::binary_search(a, t);
    const bool present = std::binary_search(a.begin(), a.end(), t);
    if (present) {
      ASSERT_GE(idx, 0);
      EXPECT_EQ(a[idx], t);
    } else {
      EXPECT_EQ(idx, -1);
    }
  }
}

TEST(SearchTrace, LinearEmitsInitFoundDone) {
  std::vector<int> a{4, 8, 2};
  proofrun::trace::Emitter em;
  em.set_enabled(true);
  em.set_meta("search.linear_search", "test", 1);
  em.set_manifest("Linear Search", "O(1)", "O(n)", "O(n)", "O(1)", "test");
  em.set_initial_array(a);
  EXPECT_EQ(proofrun::search::linear_search(a, 8, &em), 1);
  const std::string json = em.to_json();
  EXPECT_NE(json.find("\"type\":\"init\""), std::string::npos);
  EXPECT_NE(json.find("\"type\":\"found\""), std::string::npos);
  EXPECT_NE(json.find("\"type\":\"done\""), std::string::npos);
}

TEST(SearchFaultInjection, BrokenLinearDetected) {
  auto broken = [](const std::vector<int>& a, int target) {
    // Intentionally wrong: always reports missing.
    (void)a;
    (void)target;
    return -1;
  };
  EXPECT_EQ(broken({1, 2, 3}, 2), -1);
  EXPECT_NE(proofrun::search::linear_search({1, 2, 3}, 2), -1);
}

}  // namespace
