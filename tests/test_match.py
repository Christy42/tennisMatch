from tennis_match import match
from unittest import mock


@mock.patch('tennis_match.match.set_winner')
def test_singles_match(mocked):
    mocked.return_value = {"winner": 1, "server": 1, "stats": {}}
    assert match.singles_match([{"mobility": 1, "accuracy": 1, "strength": 1, "serve": 1},
                               {"mobility": 1, "accuracy": 1, "strength": 1, "serve": 1},
                                ], 5, False)["winner"] == 1


@mock.patch('tennis_match.match.play_game')
@mock.patch('tennis_match.match.tie_break')
def test_set_winner(mocked_play_game, mocked_tie_break):
    mocked_play_game.return_value = {"winner": 1, "server": 1, "stats": {0: {}, 1: {}}}
    mocked_tie_break.return_value = {"winner": 1, "server": 1, "stats": {0: {}, 1: {}}}
    assert match.set_winner([], 1, True, {0: {}, 1: {}})["winner"] == 1


@mock.patch('tennis_match.match.play_point')
def test_tie_break(mocked):
    mocked.return_value = {"winner": 1}
    assert match.tie_break([], 0, {})["winner"] == 1


@mock.patch('tennis_match.match.play_point')
def test_play_game(mocked):
    mocked.return_value = {"winner": 1, "stats": {0: {}, 1: {}}, "rally": 5}
    player = {"mobility": 30, "accuracy": 30, "strength": 30, "serve": 30, "stamina": 30, "fitness": 50}
    assert match.play_game([player, player], 1, {0: {}, 1: {}})["winner"] == 1


def test_set_base_attributes():
    player = {"mobility": 30, "accuracy": 30, "strength": 30, "serve": 30, "stamina": 30}
    player_update = {"mobility": 30, "accuracy": 30, "strength": 30, "serve": 30, "stamina": 30,
                     "base mobility": 30, "base accuracy": 30, "base strength": 30, "base serve": 30}
    assert match.set_base_attributes([player, player]) == [player_update, player_update]
