from tennis_match import match
from unittest import mock


@mock.patch('tennis_match.match.set_winner')
def test_singles_match(mocked):
    mocked.return_value = {"winner": 1, "server": 1, "stats": {}}
    assert match.singles_match([{"mobility": 1, "accuracy": 1, "strength": 1, "serve": 1},
                               {"mobility": 1, "accuracy": 1, "strength": 1, "serve": 1},
                                ], 5, False)["winner"] == 1
