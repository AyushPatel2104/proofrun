from hypothesis import given, settings
from hypothesis import strategies as st

from proofrun_py.oracles import (
    binary_search_oracle,
    is_nondecreasing,
    linear_search_oracle,
    max_sum_window_oracle,
    prefix_range_oracle,
    two_sum_sorted_oracle,
)


@given(st.lists(st.integers(-50, 50), max_size=40), st.integers(-60, 60))
@settings(max_examples=80)
def test_linear_search_oracle_consistency(values, target):
    idx = linear_search_oracle(values, target)
    if idx < 0:
        assert target not in values
    else:
        assert values[idx] == target
        assert target not in values[:idx]


@given(st.lists(st.integers(-50, 50), max_size=40), st.integers(-60, 60))
@settings(max_examples=80)
def test_binary_search_oracle_on_sorted(values, target):
    sorted_vals = sorted(values)
    idx = binary_search_oracle(sorted_vals, target)
    if idx < 0:
        assert target not in sorted_vals
    else:
        assert sorted_vals[idx] == target


@given(st.lists(st.integers(-30, 30), min_size=0, max_size=30), st.integers(-60, 60))
@settings(max_examples=60)
def test_two_sum_oracle_pairs_sum(values, target):
    a = sorted(values)
    assert is_nondecreasing(a)
    pair = two_sum_sorted_oracle(a, target)
    if pair is None:
        for i in range(len(a)):
            for j in range(i + 1, len(a)):
                assert a[i] + a[j] != target
    else:
        i, j = pair
        assert i < j
        assert a[i] + a[j] == target


@given(st.lists(st.integers(-40, 40), min_size=1, max_size=30), st.integers(1, 30))
@settings(max_examples=60)
def test_window_oracle_matches_definition(values, k):
    if k > len(values):
        assert max_sum_window_oracle(values, k) is None
        return
    got = max_sum_window_oracle(values, k)
    assert got is not None
    s, start, end = got
    assert end - start + 1 == k
    assert sum(values[start : end + 1]) == s
    # maximality
    for i in range(0, len(values) - k + 1):
        assert sum(values[i : i + k]) <= s


@given(st.lists(st.integers(-40, 40), min_size=1, max_size=25))
@settings(max_examples=50)
def test_prefix_oracle_all_ranges(values):
    for l in range(len(values)):
        for r in range(l, len(values)):
            assert prefix_range_oracle(values, l, r) == sum(values[l : r + 1])
