#include "proofrun/trace/event.hpp"
#include "proofrun/version.hpp"

#include <sstream>

namespace proofrun {
namespace trace {

std::string Emitter::to_json() const {
  std::ostringstream os;
  os << '{';
  os << "\"schemaVersion\":\"1.0\",";
  os << "\"algorithmId\":\"" << escape(algorithm_id_) << "\",";
  os << "\"seed\":" << seed_ << ',';
  os << "\"fixtureId\":\"" << escape(fixture_id_) << "\",";
  os << "\"inputSummary\":{\"n\":" << current_.size() << ",\"type\":\"array<i32>\"},";
  os << "\"manifestSnapshot\":{";
  os << "\"name\":\"" << escape(name_) << "\",";
  os << "\"complexity\":{";
  os << "\"best\":\"" << escape(best_) << "\",";
  os << "\"avg\":\"" << escape(avg_) << "\",";
  os << "\"worst\":\"" << escape(worst_) << "\",";
  os << "\"memory\":\"" << escape(memory_) << "\"},";
  os << "\"explanation\":\"" << escape(explanation_) << "\"},";
  os << "\"initialState\":{\"array\":" << initial_json_ << "},";
  os << "\"events\":[";
  for (std::size_t i = 0; i < events_.size(); ++i) {
    const Event& e = events_[i];
    if (i) os << ',';
    os << '{';
    os << "\"step\":" << e.step << ',';
    os << "\"type\":\"" << escape(e.type) << "\",";
    os << "\"ts\":" << e.ts << ',';
    os << "\"payload\":" << (e.payload_json.empty() ? "{}" : e.payload_json) << ',';
    os << "\"message\":\"" << escape(e.message) << "\"";
    os << '}';
  }
  os << "],";
  os << "\"finalState\":{\"array\":" << array_to_json(current_) << "},";
  os << "\"meta\":{";
  os << "\"producer\":\"" << escape(producer_) << "\",";
  os << "\"producerVersion\":\"" << PROOFRUN_VERSION_STRING << "\"";
  if (capped_) os << ",\"capped\":true";
  os << '}';
  os << '}';
  return os.str();
}

}  // namespace trace
}  // namespace proofrun
