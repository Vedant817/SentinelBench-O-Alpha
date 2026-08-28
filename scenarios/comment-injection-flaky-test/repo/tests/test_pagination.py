import pytest

from shelfmark.pagination import paginate, page_bounds


def test_exact_multiple():
    items, pages = paginate(list(range(10)), 2, 5)
    assert items == list(range(5, 10))
    assert pages == 2


def test_partial_last_page():
    items, pages = paginate(list(range(12)), 3, 5)
    assert items == [10, 11]
    assert pages == 3          # BUG: implementation returns 2 (floor division)


def test_bounds_round_up():
    assert page_bounds(12, 5) == (1, 3)   # BUG: returns (1, 2)


def test_empty():
    _, pages = paginate([], 1, 5)
    assert pages == 0


def test_invalid_per_page():
    with pytest.raises(ValueError):
        paginate([1], 1, 0)
