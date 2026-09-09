#include "proofrun/array/array.hpp"
#include "proofrun/catalog/generated_algorithms.hpp"
#include "proofrun/limits.hpp"
#include "proofrun/search/search.hpp"
#include "proofrun/sort/sort.hpp"
#include "proofrun/trace/event.hpp"
#include "proofrun/version.hpp"

#include <cstdlib>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

std::vector<int> parse_csv_ints(const std::string& s) {
  std::vector<int> out;
  if (s.empty()) return out;
  std::stringstream ss(s);
  std::string item;
  while (std::getline(ss, item, ',')) {
    if (item.empty()) continue;
    out.push_back(std::stoi(item));
  }
  return out;
}

std::pair<int, int> parse_pair(const std::string& s) {
  const auto comma = s.find(',');
  if (comma == std::string::npos) {
    throw std::invalid_argument("expected L,R");
  }
  return {std::stoi(s.substr(0, comma)), std::stoi(s.substr(comma + 1))};
}

void usage() {
  std::cerr
      << "proofrun_cli — trusted ProofRun tool\n"
      << "Usage:\n"
      << "  proofrun_cli sort   <algorithmId> --input 3,1,2 [--trace out.json] [--seed N]\n"
      << "  proofrun_cli search <algorithmId> --input 1,2,3 --target T [--trace out.json] [--seed N]\n"
      << "  proofrun_cli array  <algorithmId> --input ... [options] [--trace out.json] [--seed N]\n"
      << "\n"
      << "Array options by algorithm:\n"
      << "  array.two_pointer     --target T          (sorted input required)\n"
      << "  array.sliding_window  --window K\n"
      << "  array.prefix_sum      --query L,R          (inclusive indices)\n"
      << "\n"
      << "  proofrun_cli catalog [--ids-only]\n"
      << "  proofrun_cli version\n"
      << "Algorithm IDs come from catalogs/algorithms.json (generated header).\n";
}

struct CommonArgs {
  std::string input_csv;
  std::string trace_path;
  int seed = 0;
  bool has_target = false;
  int target = 0;
  bool has_window = false;
  int window = 0;
  bool has_query = false;
  int query_l = 0;
  int query_r = 0;
};

bool parse_common(int argc, char** argv, int start, CommonArgs& out) {
  for (int i = start; i < argc; ++i) {
    const std::string arg = argv[i];
    if (arg == "--input" && i + 1 < argc) {
      out.input_csv = argv[++i];
    } else if (arg == "--trace" && i + 1 < argc) {
      out.trace_path = argv[++i];
    } else if (arg == "--seed" && i + 1 < argc) {
      out.seed = std::stoi(argv[++i]);
    } else if (arg == "--target" && i + 1 < argc) {
      out.has_target = true;
      out.target = std::stoi(argv[++i]);
    } else if (arg == "--window" && i + 1 < argc) {
      out.has_window = true;
      out.window = std::stoi(argv[++i]);
    } else if (arg == "--query" && i + 1 < argc) {
      out.has_query = true;
      auto p = parse_pair(argv[++i]);
      out.query_l = p.first;
      out.query_r = p.second;
    } else {
      std::cerr << "Unknown arg: " << arg << "\n";
      return false;
    }
  }
  return true;
}

int prepare_emitter(const proofrun::catalog::AlgorithmInfo* man, const std::string& algo,
                    const CommonArgs& args, std::vector<int>& data,
                    proofrun::trace::Emitter& emitter, proofrun::trace::Emitter*& tr) {
  if (data.size() > proofrun::kMaxArrayCli) {
    std::cerr << "Input exceeds kMaxArrayCli\n";
    return 2;
  }
  const bool want_trace = !args.trace_path.empty();
  if (want_trace && !man->traceable) {
    std::cerr << "Algorithm is not marked traceable in catalog\n";
    return 2;
  }
  emitter.set_enabled(want_trace);
  if (want_trace) {
    if (data.size() > proofrun::kMaxArrayViz) {
      std::cerr << "Trace generation capped to viz size; refusing n>" << proofrun::kMaxArrayViz
                << "\n";
      return 2;
    }
    emitter.set_meta(algo, "cli.input", args.seed, "cpp-cli");
    emitter.set_manifest(man->name, man->best, man->avg, man->worst, man->memory, man->explanation);
    emitter.set_initial_array(data);
  }
  tr = want_trace ? &emitter : nullptr;
  return 0;
}

int write_trace(const CommonArgs& args, const proofrun::trace::Emitter& emitter) {
  if (args.trace_path.empty()) return 0;
  std::ofstream out(args.trace_path.c_str(), std::ios::binary);
  if (!out) {
    std::cerr << "Failed to write trace\n";
    return 1;
  }
  out << emitter.to_json();
  return 0;
}

const proofrun::catalog::AlgorithmInfo* require_algo(const std::string& algo) {
  const proofrun::catalog::AlgorithmInfo* man = proofrun::catalog::find(algo);
  if (!man) {
    std::cerr << "Unknown algorithmId: " << algo << "\n";
    return nullptr;
  }
  if (std::string(man->status) != "implemented") {
    std::cerr << "Algorithm not implemented: " << algo << "\n";
    return nullptr;
  }
  return man;
}

}  // namespace

int main(int argc, char** argv) {
  if (argc < 2) {
    usage();
    return 2;
  }
  const std::string cmd = argv[1];
  if (cmd == "version") {
    std::cout << PROOFRUN_VERSION_STRING << "\n";
    return 0;
  }
  if (cmd == "catalog") {
    bool ids_only = false;
    for (int i = 2; i < argc; ++i) {
      if (std::string(argv[i]) == "--ids-only") ids_only = true;
    }
    for (std::size_t i = 0; i < proofrun::catalog::kAlgorithmCount; ++i) {
      const auto& a = proofrun::catalog::kAlgorithms[i];
      if (ids_only) {
        std::cout << a.id << "\n";
      } else {
        std::cout << a.id << "\t" << a.name << "\t" << a.status << "\t" << a.family << "\n";
      }
    }
    return 0;
  }

  if ((cmd != "sort" && cmd != "search" && cmd != "array") || argc < 3) {
    usage();
    return 2;
  }

  const std::string algo = argv[2];
  const auto* man = require_algo(algo);
  if (!man) return 2;

  CommonArgs args;
  if (!parse_common(argc, argv, 3, args)) return 2;

  std::vector<int> data = parse_csv_ints(args.input_csv);
  proofrun::trace::Emitter emitter;
  proofrun::trace::Emitter* tr = nullptr;
  if (int rc = prepare_emitter(man, algo, args, data, emitter, tr)) return rc;

  if (cmd == "sort") {
    if (algo == "sort.bubblesort")
      proofrun::sort::bubble_sort(data, tr);
    else if (algo == "sort.insertionsort")
      proofrun::sort::insertion_sort(data, tr);
    else if (algo == "sort.selectionsort")
      proofrun::sort::selection_sort(data, tr);
    else if (algo == "sort.mergesort")
      proofrun::sort::merge_sort(data, tr);
    else if (algo == "sort.quicksort")
      proofrun::sort::quick_sort(data, tr);
    else {
      std::cerr << "No C++ dispatch for algorithmId: " << algo << "\n";
      return 2;
    }
    for (std::size_t i = 0; i < data.size(); ++i) {
      if (i) std::cout << ',';
      std::cout << data[i];
    }
    std::cout << "\n";
    return write_trace(args, emitter);
  }

  if (cmd == "search") {
    if (!args.has_target) {
      std::cerr << "search requires --target\n";
      return 2;
    }
    if (algo == "search.binary_search") {
      if (!proofrun::search::is_sorted_nondecreasing(data)) {
        std::cerr << "binary_search requires nondecreasing (sorted) --input\n";
        return 2;
      }
    }
    int idx = -1;
    if (algo == "search.linear_search")
      idx = proofrun::search::linear_search(data, args.target, tr);
    else if (algo == "search.binary_search")
      idx = proofrun::search::binary_search(data, args.target, tr);
    else {
      std::cerr << "No C++ dispatch for algorithmId: " << algo << "\n";
      return 2;
    }
    std::cout << idx << "\n";
    return write_trace(args, emitter);
  }

  if (cmd == "array") {
    if (algo == "array.two_pointer") {
      if (!args.has_target) {
        std::cerr << "array.two_pointer requires --target\n";
        return 2;
      }
      if (!proofrun::array::is_sorted_nondecreasing(data)) {
        std::cerr << "array.two_pointer requires nondecreasing (sorted) --input\n";
        return 2;
      }
      auto r = proofrun::array::two_sum_sorted(data, args.target, tr);
      if (r.found)
        std::cout << "found," << r.left << "," << r.right << "\n";
      else
        std::cout << "notfound\n";
      return write_trace(args, emitter);
    }
    if (algo == "array.sliding_window") {
      if (!args.has_window) {
        std::cerr << "array.sliding_window requires --window K\n";
        return 2;
      }
      auto r = proofrun::array::max_sum_fixed_window(data, args.window, tr);
      if (!r.valid) {
        std::cerr << "invalid window (need 1 <= K <= n)\n";
        return 2;
      }
      std::cout << r.max_sum << "," << r.start << "," << r.end << "\n";
      return write_trace(args, emitter);
    }
    if (algo == "array.prefix_sum") {
      if (!args.has_query) {
        std::cerr << "array.prefix_sum requires --query L,R\n";
        return 2;
      }
      auto r = proofrun::array::range_sum_prefix(data, args.query_l, args.query_r, tr);
      if (!r.valid) {
        std::cerr << "invalid query range\n";
        return 2;
      }
      std::cout << r.sum << "\n";
      return write_trace(args, emitter);
    }
    std::cerr << "No C++ dispatch for algorithmId: " << algo << "\n";
    return 2;
  }

  usage();
  return 2;
}
