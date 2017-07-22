from utility import utility
from unittest import mock


def test_diff():
    assert utility.diff([1, 0]) == 1
    assert utility.diff([0, 1]) == 1
    assert utility.diff([1, 1, 0]) == 0


def test_divide_diff_by_int():
    assert utility.divide_diff_by_int({0: {1: 2, 3: 4}}, 3) == {0: {1: 2/3.0, 3: 4/3.0}}


@mock.patch('random.randint')
def test_repeated_random(mocked):
    mocked.return_value = 1
    assert 0 <= utility.repeated_random(0, 2, 4) <= 2
