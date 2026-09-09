from hypothesis import given, settings
from hypothesis import strategies as st

from proofrun_py.oracles import is_nondecreasing, is_permutation, sort_oracle


@given(st.lists(st.integers(min_value=-1000, max_value=1000), max_size=64))
@settings(max_examples=40)
def test_oracle_is_sorted_permutation(xs):
    ys = sort_oracle(xs)
    assert is_nondecreasing(ys)
    assert is_permutation(xs, ys)


@given(st.lists(st.integers(min_value=-100, max_value=100), max_size=32))
@settings(max_examples=25)
def test_sorting_idempotent(xs):
    assert sort_oracle(sort_oracle(xs)) == sort_oracle(xs)
