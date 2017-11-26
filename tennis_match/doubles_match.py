import random

from utility.utility import diff
from tennis_match.match import Match


# Players are numbered 0, 1 vs 2, 3
# Sides are 0, 1 though (respectively)
class DoublesMatch(Match):
    def __init__(self, max_sets, players, tie_breaks, comm_file, games_required=6, deuce=True, let=True,
                 championship_match=False, third_set_tie_break=True):
        Match.__init__(max_sets, players, tie_breaks, comm_file, games_required, deuce, let, championship_match)
        self._final_set_tie_break = third_set_tie_break
        self._server = random.randint(0, 3)
        self._receiver = random.randint(0, 1) + 2 * (self._server in [0, 1])

    def singles_match(self):
        while max(self._sets) < self._sets_required:
            result = self._set_winner()

    def _set_winner(self):

        return 1

    def _play_game(self):
        while max(self._points) < 4 or (diff(self._points) < 2 and self._deuce):
            result = self._play_point(server)
            self._points[result["winner"]] += 1
            self._receiver = (self._receiver + 1) % 2 + 2 * (self._server in [0, 1])
            self._stats[result["winner"]]["points for"] = 1 + self._stats[result["winner"]].get("points for", 0)
            for i in range(2):
                self._players[i]["stamina"] -= result["rally"] / 2.0 * (1.1 - self._players[i]["fitness"] / 146.0)
                self._players[i]["stamina"] = max(self._players[i]["stamina"], 0.0)
        return {"winner": self._points.index(max(self._points))}

    def _play_point(self, server):

        return {}
