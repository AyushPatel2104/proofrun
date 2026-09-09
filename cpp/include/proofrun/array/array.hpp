#pragma once

#include <cstdint>
#include <utility>
#include <vector>

#include "proofrun/trace/event.hpp"

namespace proofrun {
namespace array {

struct TwoSumResult {
  bool found = false;
  int left = -1;
  int right = -1;
};

// Two-pointer two-sum on a nondecreasing array: find i < j with a[i] + a[j] == target.
// Precondition: a sorted ascending (CLI enforces).
TwoSumResult two_sum_sorted(const std::vector<int>& a, int target, trace::Emitter* trace = nullptr);

struct WindowSumResult {
  bool valid = false;
  std::int64_t max_sum = 0;
  int start = -1;  // inclusive
  int end = -1;    // inclusive
};

// Fixed-size sliding window: maximum sum of any contiguous window of length k.
// Invalid when k <= 0 or k > n (valid=false).
WindowSumResult max_sum_fixed_window(const std::vector<int>& a, int k,
                                     trace::Emitter* trace = nullptr);

struct PrefixRangeResult {
  bool valid = false;
  std::int64_t sum = 0;
  std::vector<std::int64_t> prefix;  // prefix[0]=0, prefix[i]=sum(a[0..i-1])
};

// Build prefix sums then answer inclusive range sum [left, right] in O(1) after O(n).
// Invalid when indices out of range or left > right.
PrefixRangeResult range_sum_prefix(const std::vector<int>& a, int left, int right,
                                   trace::Emitter* trace = nullptr);

bool is_sorted_nondecreasing(const std::vector<int>& a);

}  // namespace array
}  // namespace proofrun
