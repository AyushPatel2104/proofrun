#pragma once

#include <vector>

#include "proofrun/trace/event.hpp"

namespace proofrun {
namespace sort {

// In-place sorts. If trace != nullptr and enabled, emit visualization events.
void bubble_sort(std::vector<int>& a, trace::Emitter* trace = nullptr);
void insertion_sort(std::vector<int>& a, trace::Emitter* trace = nullptr);
void selection_sort(std::vector<int>& a, trace::Emitter* trace = nullptr);
void merge_sort(std::vector<int>& a, trace::Emitter* trace = nullptr);
void quick_sort(std::vector<int>& a, trace::Emitter* trace = nullptr);

}  // namespace sort
}  // namespace proofrun
