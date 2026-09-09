#pragma once

#include <vector>

#include "proofrun/trace/event.hpp"

namespace proofrun {
namespace search {

// First-index linear search. Returns index or -1 if absent.
int linear_search(const std::vector<int>& a, int target, trace::Emitter* trace = nullptr);

// Classic binary search on a nondecreasing array. Returns an index of target or -1.
// Precondition: a must be sorted ascending. Callers/CLI must enforce this.
int binary_search(const std::vector<int>& a, int target, trace::Emitter* trace = nullptr);

// True iff a is nondecreasing.
bool is_sorted_nondecreasing(const std::vector<int>& a);

}  // namespace search
}  // namespace proofrun
