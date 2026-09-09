#include "proofrun/array/array.hpp"

#include <sstream>
#include <string>

namespace proofrun {
namespace array {
namespace {

std::string array_json(const std::vector<int>& a) { return trace::Emitter::array_to_json(a); }

std::string prefix_json(const std::vector<std::int64_t>& p) {
  std::ostringstream os;
  os << '[';
  for (std::size_t i = 0; i < p.size(); ++i) {
    if (i) os << ',';
    os << p[i];
  }
  os << ']';
  return os.str();
}

}  // namespace

bool is_sorted_nondecreasing(const std::vector<int>& a) {
  for (std::size_t i = 1; i < a.size(); ++i) {
    if (a[i] < a[i - 1]) return false;
  }
  return true;
}

TwoSumResult two_sum_sorted(const std::vector<int>& a, int target, trace::Emitter* t) {
  if (t) {
    std::ostringstream os;
    os << "{\"array\":" << array_json(a) << ",\"target\":" << target << '}';
    t->emit("init", os.str(), "two-pointer two-sum on sorted array");
  }
  TwoSumResult out;
  int left = 0;
  int right = static_cast<int>(a.size()) - 1;
  while (left < right) {
    const std::int64_t sum = static_cast<std::int64_t>(a[left]) + static_cast<std::int64_t>(a[right]);
    if (t) {
      std::ostringstream os;
      os << "{\"i\":" << left << ",\"j\":" << right << ",\"left\":" << left << ",\"right\":" << right
         << ",\"sum\":" << sum << ",\"target\":" << target << ",\"array\":" << array_json(a) << '}';
      t->emit("compare", os.str(), "compare a[left]+a[right] to target");
    }
    if (sum == target) {
      out.found = true;
      out.left = left;
      out.right = right;
      if (t) {
        std::ostringstream os;
        os << "{\"i\":" << left << ",\"j\":" << right << ",\"array\":" << array_json(a) << '}';
        t->emit("found", os.str(), "pair found");
        t->note_array(a);
        t->emit("done", os.str(), "complete");
      }
      return out;
    }
    if (sum < target) {
      ++left;
      if (t) {
        std::ostringstream os;
        os << "{\"i\":" << left << ",\"j\":" << right << ",\"array\":" << array_json(a) << '}';
        t->emit("highlight", os.str(), "move left pointer right");
      }
    } else {
      --right;
      if (t) {
        std::ostringstream os;
        os << "{\"i\":" << left << ",\"j\":" << right << ",\"array\":" << array_json(a) << '}';
        t->emit("highlight", os.str(), "move right pointer left");
      }
    }
  }
  if (t) {
    std::ostringstream os;
    os << "{\"array\":" << array_json(a) << ",\"target\":" << target << '}';
    t->emit("not_found", os.str(), "no pair");
    t->note_array(a);
    t->emit("done", os.str(), "complete");
  }
  return out;
}

WindowSumResult max_sum_fixed_window(const std::vector<int>& a, int k, trace::Emitter* t) {
  WindowSumResult out;
  const int n = static_cast<int>(a.size());
  if (t) {
    std::ostringstream os;
    os << "{\"array\":" << array_json(a) << ",\"k\":" << k << '}';
    t->emit("init", os.str(), "fixed sliding window max sum");
  }
  if (k <= 0 || k > n) {
    if (t) {
      std::ostringstream os;
      os << "{\"array\":" << array_json(a) << ",\"k\":" << k << ",\"valid\":false}";
      t->note_array(a);
      t->emit("done", os.str(), "invalid window size");
    }
    return out;
  }

  std::int64_t window = 0;
  for (int i = 0; i < k; ++i) window += a[i];
  out.valid = true;
  out.max_sum = window;
  out.start = 0;
  out.end = k - 1;
  if (t) {
    std::ostringstream os;
    os << "{\"i\":0,\"j\":" << (k - 1) << ",\"windowSum\":" << window << ",\"maxSum\":" << out.max_sum
       << ",\"array\":" << array_json(a) << '}';
    t->emit("highlight", os.str(), "initial window");
  }

  for (int end = k; end < n; ++end) {
    const int start = end - k + 1;
    window += a[end];
    if (t) {
      std::ostringstream os;
      os << "{\"i\":" << (start - 1) << ",\"j\":" << end << ",\"array\":" << array_json(a) << '}';
      t->emit("highlight", os.str(), "expand right");
    }
    window -= a[start - 1];
    if (t) {
      std::ostringstream os;
      os << "{\"i\":" << start << ",\"j\":" << end << ",\"windowSum\":" << window
         << ",\"array\":" << array_json(a) << '}';
      t->emit("highlight", os.str(), "contract left");
    }
    if (window > out.max_sum) {
      out.max_sum = window;
      out.start = start;
      out.end = end;
      if (t) {
        std::ostringstream os;
        os << "{\"i\":" << start << ",\"j\":" << end << ",\"maxSum\":" << out.max_sum
           << ",\"array\":" << array_json(a) << '}';
        t->emit("write", os.str(), "update max window");
      }
    }
  }

  if (t) {
    std::ostringstream os;
    os << "{\"i\":" << out.start << ",\"j\":" << out.end << ",\"maxSum\":" << out.max_sum
       << ",\"array\":" << array_json(a) << '}';
    t->note_array(a);
    t->emit("done", os.str(), "max window located");
  }
  return out;
}

PrefixRangeResult range_sum_prefix(const std::vector<int>& a, int left, int right,
                                   trace::Emitter* t) {
  PrefixRangeResult out;
  const int n = static_cast<int>(a.size());
  if (t) {
    std::ostringstream os;
    os << "{\"array\":" << array_json(a) << ",\"left\":" << left << ",\"right\":" << right << '}';
    t->emit("init", os.str(), "prefix sum then range query");
  }

  out.prefix.assign(static_cast<std::size_t>(n) + 1, 0);
  for (int i = 0; i < n; ++i) {
    out.prefix[static_cast<std::size_t>(i) + 1] =
        out.prefix[static_cast<std::size_t>(i)] + static_cast<std::int64_t>(a[i]);
    if (t) {
      // Visualize prefix growth using int truncation for bar chart (demo sizes are small).
      std::vector<int> viz(out.prefix.begin(), out.prefix.end());
      std::ostringstream os;
      os << "{\"index\":" << (i + 1) << ",\"prefix\":" << prefix_json(out.prefix)
         << ",\"array\":" << trace::Emitter::array_to_json(viz) << '}';
      t->emit("write", os.str(), "accumulate prefix");
      t->note_array(viz);
    }
  }

  if (left < 0 || right < 0 || left >= n || right >= n || left > right) {
    if (t) {
      std::vector<int> viz(out.prefix.begin(), out.prefix.end());
      std::ostringstream os;
      os << "{\"valid\":false,\"array\":" << trace::Emitter::array_to_json(viz) << '}';
      t->emit("done", os.str(), "invalid query range");
    }
    return out;
  }

  out.valid = true;
  out.sum = out.prefix[static_cast<std::size_t>(right) + 1] - out.prefix[static_cast<std::size_t>(left)];
  if (t) {
    std::vector<int> viz(out.prefix.begin(), out.prefix.end());
    std::ostringstream os;
    os << "{\"i\":" << left << ",\"j\":" << right << ",\"sum\":" << out.sum
       << ",\"array\":" << trace::Emitter::array_to_json(viz) << '}';
    t->emit("highlight", os.str(), "range query via prefix");
    t->note_array(viz);
    t->emit("done", os.str(), "query complete");
  }
  return out;
}

}  // namespace array
}  // namespace proofrun
