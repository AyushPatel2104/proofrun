#pragma once

#include <sstream>
#include <string>
#include <utility>
#include <vector>

namespace proofrun {
namespace trace {

struct Event {
  int step = 0;
  std::string type;
  int ts = 0;
  std::string payload_json;  // object body without outer braces optional; store full object
  std::string message;
};

// Minimal JSON object builder for trusted emitters (no third-party JSON dep required).
class Emitter {
 public:
  void set_meta(std::string algorithm_id, std::string fixture_id, int seed,
                std::string producer = "cpp-cli") {
    algorithm_id_ = std::move(algorithm_id);
    fixture_id_ = std::move(fixture_id);
    seed_ = seed;
    producer_ = std::move(producer);
  }

  void set_manifest(std::string name, std::string best, std::string avg, std::string worst,
                    std::string memory, std::string explanation) {
    name_ = std::move(name);
    best_ = std::move(best);
    avg_ = std::move(avg);
    worst_ = std::move(worst);
    memory_ = std::move(memory);
    explanation_ = std::move(explanation);
  }

  void set_initial_array(const std::vector<int>& a) {
    initial_json_ = array_to_json(a);
    current_ = a;
  }

  bool enabled() const { return enabled_; }
  void set_enabled(bool v) { enabled_ = v; }
  bool capped() const { return capped_; }

  void emit(const std::string& type, const std::string& payload_object,
            const std::string& message) {
    if (!enabled_) return;
    if (static_cast<int>(events_.size()) >= max_events_) {
      capped_ = true;
      return;
    }
    Event e;
    e.step = step_++;
    e.type = type;
    e.ts = e.step;
    e.payload_json = payload_object;
    e.message = message;
    events_.push_back(std::move(e));
  }

  void note_array(const std::vector<int>& a) { current_ = a; }

  const std::vector<int>& current() const { return current_; }

  std::string to_json() const;

  static std::string array_to_json(const std::vector<int>& a) {
    std::ostringstream os;
    os << '[';
    for (std::size_t i = 0; i < a.size(); ++i) {
      if (i) os << ',';
      os << a[i];
    }
    os << ']';
    return os.str();
  }

  static std::string escape(const std::string& s) {
    std::string out;
    out.reserve(s.size() + 8);
    for (char c : s) {
      switch (c) {
        case '\\': out += "\\\\"; break;
        case '"': out += "\\\""; break;
        case '\n': out += "\\n"; break;
        case '\r': out += "\\r"; break;
        case '\t': out += "\\t"; break;
        default: out += c; break;
      }
    }
    return out;
  }

 private:
  bool enabled_ = true;
  bool capped_ = false;
  int step_ = 0;
  int max_events_ = 5000;
  int seed_ = 0;
  std::string algorithm_id_;
  std::string fixture_id_;
  std::string producer_;
  std::string name_, best_, avg_, worst_, memory_, explanation_;
  std::string initial_json_ = "[]";
  std::vector<int> current_;
  std::vector<Event> events_;
};

}  // namespace trace
}  // namespace proofrun
