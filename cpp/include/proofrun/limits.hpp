#pragma once

#include <cstddef>

namespace proofrun {

// Hard limits for trusted CLI/demo paths (see SECURITY.md).
constexpr std::size_t kMaxArrayViz = 64;
constexpr std::size_t kMaxArrayCli = 100000;
constexpr std::size_t kMaxTraceEvents = 5000;

}  // namespace proofrun
