from tennis_match import rally_shots
from unittest import mock


@mock.patch('random.random')
def test_rally_shots(mocked):
    mocked.return_value = 0.0
    assert rally_shots.shot_selection_effect(50, 5) == 10
    assert rally_shots.shot_selection_effect(30, -51) == 0
    assert rally_shots.shot_selection_effect(800, 5) == 160

