#include "proofrun/search/search.hpp"

#include <sstream>
#include <string>

namespace proofrun {
namespace search {
namespace {

std::string array_payload(const std::vector<int>& a) {
  std::ostringstream os;
  os << "{\"array\":" << trace::Emitter::array_to_json(a) << '}';
  return os.str();
}

void emit_init(trace::Emitter* t, const std::vector<int>& a, int target) {
  if (!t) return;
  std::ostringstream os;
  os << "{\"array\":" << trace::Emitter::array_to_json(a) << ",\"target\":" << target << '}';
  t->emit("init", os.str(), "start search");
}

void emit_done(trace::Emitter* t, const std::vector<int>& a, int result_index, int target) {
  if (!t) return;
  t->note_array(a);
  std::ostringstream os;
  os << "{\"array\":" << trace::Emitter::array_to_json(a) << ",\"target\":" << target
     << ",\"resultIndex\":" << result_index << ",\"found\":" << (result_index >= 0 ? "true" : "false")
     << '}';
  t->emit("done", os.str(), result_index >= 0 ? "found" : "not found");
}

}  // namespace

bool is_sorted_nondecreasing(const std::vector<int>& a) {
  for (std::size_t i = 1; i < a.size(); ++i) {
    if (a[i] < a[i - 1]) return false;
  }
  return true;
}

int linear_search(const std::vector<int>& a, int target, trace::Emitter* t) {
  emit_init(t, a, target);
  for (int i = 0; i < static_cast<int>(a.size()); ++i) {
    if (t) {
      std::ostringstream os;
      os << "{\"i\":" << i << ",\"value\":" << a[i] << ",\"target\":" << target
         << ",\"array\":" << trace::Emitter::array_to_json(a) << '}';
      t->emit("compare", os.str(), "compare a[i] to target");
    }
    if (a[i] == target) {
      if (t) {
        std::ostringstream os;
        os << "{\"i\":" << i << ",\"index\":" << i << ",\"target\":" << target
           << ",\"array\":" << trace::Emitter::array_to_json(a) << '}';
        t->emit("found", os.str(), "target located");
      }
      emit_done(t, a, i, target);
      return i;
    }
  }
  if (t) {
    std::ostringstream os;
    os << "{\"target\":" << target << ",\"array\":" << trace::Emitter::array_to_json(a) << '}';
    t->emit("not_found", os.str(), "target absent");
  }
  emit_done(t, a, -1, target);
  return -1;
}

int binary_search(const std::vector<int>& a, int target, trace::Emitter* t) {
  emit_init(t, a, target);
  int lo = 0;
  int hi = static_cast<int>(a.size()) - 1;
  while (lo <= hi) {
    const int mid = lo + (hi - lo) / 2;
    if (t) {
      std::ostringstream os;
      os << "{\"i\":" << lo << ",\"j\":" << hi << ",\"index\":" << mid << ",\"low\":" << lo
         << ",\"mid\":" << mid << ",\"high\":" << hi << ",\"value\":" << a[mid]
         << ",\"target\":" << target << ",\"array\":" << trace::Emitter::array_to_json(a) << '}';
      t->emit("highlight", os.str(), "set low/mid/high");
      t->emit("compare", os.str(), "compare a[mid] to target");
    }
    if (a[mid] == target) {
      if (t) {
        std::ostringstream os;
        os << "{\"i\":" << lo << ",\"j\":" << hi << ",\"index\":" << mid << ",\"target\":" << target
           << ",\"array\":" << trace::Emitter::array_to_json(a) << '}';
        t->emit("found", os.str(), "target located");
      }
      emit_done(t, a, mid, target);
      return mid;
    }
    if (a[mid] < target) {
      lo = mid + 1;
      if (t) {
        std::ostringstream os;
        os << "{\"i\":" << lo << ",\"j\":" << hi << ",\"index\":" << mid
           << ",\"array\":" << trace::Emitter::array_to_json(a) << '}';
        t->emit("highlight", os.str(), "search right half");
      }
    } else {
      hi = mid - 1;
      if (t) {
        std::ostringstream os;
        os << "{\"i\":" << lo << ",\"j\":" << hi << ",\"index\":" << mid
           << ",\"array\":" << trace::Emitter::array_to_json(a) << '}';
        t->emit("highlight", os.str(), "search left half");
      }
    }
  }
  if (t) {
    std::ostringstream os;
    os << "{\"target\":" << target << ",\"array\":" << trace::Emitter::array_to_json(a) << '}';
    t->emit("not_found", os.str(), "target absent");
  }
  emit_done(t, a, -1, target);
  return -1;
}

}  // namespace search
}  // namespace proofrun
