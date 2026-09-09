from proofrun_py.oracles import is_nondecreasing, is_permutation, sort_oracle


def test_sort_oracle_basic():
    assert sort_oracle([3, 1, 2]) == [1, 2, 3]
    assert sort_oracle([]) == []
    assert sort_oracle([-1, -1, 0]) == [-1, -1, 0]


def test_permutation_helper():
    assert is_permutation([3, 1, 2], [1, 2, 3])
    assert not is_permutation([3, 1, 2], [1, 2, 4])


def test_nondecreasing():
    assert is_nondecreasing([1, 1, 2])
    assert not is_nondecreasing([2, 1])
