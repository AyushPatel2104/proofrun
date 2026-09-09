"""Product workflow limits (mirror cpp/include/proofrun/limits.hpp for viz path)."""

# Product Run always requests a trace → use viz cap.
MAX_ARRAY_PRODUCT = 64
MAX_ARRAY_GENERATE = 64
MAX_INT = 1_000_000
MIN_INT = -1_000_000
MAX_BENCHMARK_N = 64
MAX_BENCHMARK_REPEATS = 20
DEFAULT_BENCHMARK_WARMUP = 2
DEFAULT_BENCHMARK_REPEATS = 5
