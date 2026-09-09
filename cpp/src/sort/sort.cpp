#include "proofrun/sort/sort.hpp"

#include <sstream>
#include <string>
#include <utility>

namespace proofrun {
namespace sort {
namespace {

std::string idx_payload(int i, int j, const std::vector<int>& a) {
  std::ostringstream os;
  os << "{\"i\":" << i << ",\"j\":" << j << ",\"array\":" << trace::Emitter::array_to_json(a)
     << '}';
  return os.str();
}

std::string array_payload(const std::vector<int>& a) {
  std::ostringstream os;
  os << "{\"array\":" << trace::Emitter::array_to_json(a) << '}';
  return os.str();
}

void emit_init(trace::Emitter* t, const std::vector<int>& a) {
  if (!t) return;
  t->emit("init", array_payload(a), "initial array");
}

void emit_done(trace::Emitter* t, const std::vector<int>& a) {
  if (!t) return;
  t->note_array(a);
  t->emit("done", array_payload(a), "sorted");
}

}  // namespace

void bubble_sort(std::vector<int>& a, trace::Emitter* t) {
  emit_init(t, a);
  const int n = static_cast<int>(a.size());
  for (int i = 0; i < n; ++i) {
    bool swapped = false;
    for (int j = 0; j + 1 < n - i; ++j) {
      if (t) {
        t->emit("compare", idx_payload(j, j + 1, a), "compare adjacent");
      }
      if (a[j] > a[j + 1]) {
        std::swap(a[j], a[j + 1]);
        swapped = true;
        if (t) {
          t->note_array(a);
          t->emit("swap", idx_payload(j, j + 1, a), "swap adjacent");
        }
      }
    }
    if (!swapped) break;
  }
  emit_done(t, a);
}

void insertion_sort(std::vector<int>& a, trace::Emitter* t) {
  emit_init(t, a);
  const int n = static_cast<int>(a.size());
  for (int i = 1; i < n; ++i) {
    int key = a[i];
    int j = i - 1;
    if (t) {
      std::ostringstream os;
      os << "{\"i\":" << i << ",\"key\":" << key << ",\"array\":" << trace::Emitter::array_to_json(a)
         << '}';
      t->emit("highlight", os.str(), "pick key");
    }
    while (j >= 0) {
      if (t) t->emit("compare", idx_payload(j, i, a), "compare key with a[j]");
      if (a[j] <= key) break;
      a[j + 1] = a[j];
      if (t) {
        t->note_array(a);
        std::ostringstream os;
        os << "{\"index\":" << (j + 1) << ",\"value\":" << a[j + 1]
           << ",\"array\":" << trace::Emitter::array_to_json(a) << '}';
        t->emit("write", os.str(), "shift right");
      }
      --j;
    }
    a[j + 1] = key;
    if (t) {
      t->note_array(a);
      std::ostringstream os;
      os << "{\"index\":" << (j + 1) << ",\"value\":" << key
         << ",\"array\":" << trace::Emitter::array_to_json(a) << '}';
      t->emit("write", os.str(), "insert key");
    }
  }
  emit_done(t, a);
}

void selection_sort(std::vector<int>& a, trace::Emitter* t) {
  emit_init(t, a);
  const int n = static_cast<int>(a.size());
  for (int i = 0; i < n; ++i) {
    int min_idx = i;
    for (int j = i + 1; j < n; ++j) {
      if (t) t->emit("compare", idx_payload(min_idx, j, a), "compare for minimum");
      if (a[j] < a[min_idx]) min_idx = j;
    }
    if (min_idx != i) {
      std::swap(a[i], a[min_idx]);
      if (t) {
        t->note_array(a);
        t->emit("swap", idx_payload(i, min_idx, a), "swap min into place");
      }
    }
  }
  emit_done(t, a);
}

void merge_range(std::vector<int>& a, int lo, int mid, int hi, trace::Emitter* t) {
  std::vector<int> left(a.begin() + lo, a.begin() + mid);
  std::vector<int> right(a.begin() + mid, a.begin() + hi);
  int i = 0, j = 0, k = lo;
  while (i < static_cast<int>(left.size()) && j < static_cast<int>(right.size())) {
    if (t) {
      std::ostringstream os;
      os << "{\"left\":" << left[i] << ",\"right\":" << right[j] << '}';
      t->emit("compare", os.str(), "merge compare");
    }
    if (left[i] <= right[j]) {
      a[k++] = left[i++];
    } else {
      a[k++] = right[j++];
    }
    if (t) {
      t->note_array(a);
      t->emit("write", array_payload(a), "merge write");
    }
  }
  while (i < static_cast<int>(left.size())) {
    a[k++] = left[i++];
    if (t) {
      t->note_array(a);
      t->emit("write", array_payload(a), "merge drain left");
    }
  }
  while (j < static_cast<int>(right.size())) {
    a[k++] = right[j++];
    if (t) {
      t->note_array(a);
      t->emit("write", array_payload(a), "merge drain right");
    }
  }
}

void merge_sort_rec(std::vector<int>& a, int lo, int hi, trace::Emitter* t) {
  if (hi - lo <= 1) return;
  int mid = lo + (hi - lo) / 2;
  if (t) {
    std::ostringstream os;
    os << "{\"lo\":" << lo << ",\"mid\":" << mid << ",\"hi\":" << hi << '}';
    t->emit("partition", os.str(), "divide");
  }
  merge_sort_rec(a, lo, mid, t);
  merge_sort_rec(a, mid, hi, t);
  merge_range(a, lo, mid, hi, t);
}

void merge_sort(std::vector<int>& a, trace::Emitter* t) {
  emit_init(t, a);
  merge_sort_rec(a, 0, static_cast<int>(a.size()), t);
  emit_done(t, a);
}

int partition_lomuto(std::vector<int>& a, int lo, int hi, trace::Emitter* t) {
  int pivot = a[hi];
  if (t) {
    std::ostringstream os;
    os << "{\"lo\":" << lo << ",\"hi\":" << hi << ",\"pivot\":" << pivot << '}';
    t->emit("partition", os.str(), "pivot");
  }
  int i = lo;
  for (int j = lo; j < hi; ++j) {
    if (t) t->emit("compare", idx_payload(j, hi, a), "compare with pivot");
    if (a[j] <= pivot) {
      std::swap(a[i], a[j]);
      if (t && i != j) {
        t->note_array(a);
        t->emit("swap", idx_payload(i, j, a), "swap into left partition");
      }
      ++i;
    }
  }
  std::swap(a[i], a[hi]);
  if (t) {
    t->note_array(a);
    t->emit("swap", idx_payload(i, hi, a), "place pivot");
  }
  return i;
}

void quick_sort_rec(std::vector<int>& a, int lo, int hi, trace::Emitter* t) {
  if (lo >= hi) return;
  int p = partition_lomuto(a, lo, hi, t);
  quick_sort_rec(a, lo, p - 1, t);
  quick_sort_rec(a, p + 1, hi, t);
}

void quick_sort(std::vector<int>& a, trace::Emitter* t) {
  emit_init(t, a);
  if (!a.empty()) quick_sort_rec(a, 0, static_cast<int>(a.size()) - 1, t);
  emit_done(t, a);
}

}  // namespace sort
}  // namespace proofrun
