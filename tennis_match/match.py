import random
import math
from tennis_match import serve, rally_shots

from utility.utility import diff


class Match:
    def __init__(self, max_sets, players, tie_breaks, comm_file, games_required=6, deuce=True, let=True):
        # TODO: Update statistics throughout
        # TODO: Create an effect from stamina after every game
        # TODO: Stick list of all statistics recorded in a yaml file?
        self._max_sets = max_sets
        self._players = players
        self._sets = [0, 0]
        self._points = [0, 0]
        self._games = [0, 0]
        self._games_required = games_required
        self._deuce = deuce
        self._tie_breaks = tie_breaks
        self._in_tie_break = False
        self._commentary_file = comm_file
        self._commentary = []
        self._set_number = 0
        self._let = let
        self._stats = {players[i]["id"]: {} for i in range(len(players))}
        self._sets_required = int(math.ceil(self._max_sets / 2.0 + 0.5))
        self.set_base_attributes()

    def singles_match(self):
        server = random.randint(0, 1)
        while max(self._sets) < self._sets_required:
            result = self._set_winner(server)
            self._sets[result["winner"]] += 1
            self._stats[result["set"]]["point"] = 1 + self._stats[result["winner"]].get("set", 0)
            self._games = [0, 0]
            server = result["server"]
        # TODO: Get reverse of all statistics at the end
        self._get_statistics()
        return {"winner": self._sets.index(max(self._sets))}

    def _get_statistics(self):
        stat_list = ["aces for", "first serve for", "second serve for", "first serve beaten", "second serve beaten",
                     "let winners for", "let bounce for", "points for", "games for", "sets for"]
        for player in range(len(self._players)):
            for element in stat_list:
                amended = element.replace(" for", " against").replace(" won", " beaten")
                self._stats[player][amended] = self._stats[(player + 1) % 2].get(element, 0)

    def _set_winner(self, server):
        while max(self._games) < self._games_required or diff(self._games) < 2:
            result = self._play_game(server)
            self._games[result["winner"]] += 1
            server = (server + 1) % 2
            self._stats[result["winner"]]["games for"] = 1 + self._stats[result["winner"]].get("games for", 0)
            self._points = [0, 0]
            if self._games == [6, 6] and self._tie_breaks[self._set_number]:
                self._in_tie_break = True
                result = self._tie_break(server)
                self._games[result["winner"]] += 1
                self._points = [0, 0]
                self._in_tie_break = False
                break
        return {"winner": self._games.index(max(self._games))}

    def _play_game(self, server):
        while max(self._points) < 4 or (diff(self._points) < 2 and self._deuce):
            result = self._play_point(server)
            self._points[result["winner"]] += 1
            self._stats[result["winner"]]["points for"] = 1 + self._stats[result["winner"]].get("points for", 0)
            for i in range(2):
                self._players[i]["stamina"] -= result["rally"] / 2.0 * (1.1 - self._players[i]["fitness"] / 146.0)
                self._players[i]["stamina"] = max(self._players[i]["stamina"], 0.0)
        return {"winner": self._points.index(max(self._points))}

    def _play_point(self, server):
        service = 0
        # In the box
        self._stats[server]["first serves for"] = 1 + self._stats[server].get("first serves for", 0)
        for service in range(2):
            if serve.serve_in(self._players[server]["server aggression"][service], self._players[server]["serve"]) > \
                    random.random():
                break
            elif service == 1:
                self._stats[server]["double faults for"] = 1 + self._stats[server].get("double faults for", 0)
                return {"winner": (server + 1) % 2, "result": 1}
            else:
                # Second serve
                self._stats[server]["second serves for"] = 1 + self._stats[server].get("second serves for", 0)
        serve_aggression = self._players[server]["serve aggression"][service]
        # Ace
        if serve.ace(serve_aggression, self._players[server]["serve"], self._players[server]["strength"],
                     self._players[(server + 1) % 2]["mobility"], self._players[server]["shot selection"]) > \
                random.random():
            self._stats[server]["aces for"] = 1 + self._stats[server].get("aces for", 0)
            return {"winner": server, "rally": 1}
        let = 1.0 if self._let else random.random()

        # Work out starting balance
        balance = serve.serve_balance(serve_aggression, self._players[server]["serve"],
                                      self._players[server]["strength"], self._players[(server + 1) % 2]["mobility"])
        balance -= rally_shots.shot_selection_effect(self._players[server]["shot selection"], 0)
        if let < 0.015:
            self._stats[server]["let winners for"] = 1 + self._stats[server].get("let winners for", 0)
            return {"winner": (server + 1) % 2, "result": 1}
        elif let < 0.03:
            self._stats[server]["let bounce for"] = 1 + self._stats[server].get("let bounce for", 0)
            balance = 0
        # Run through the rally itself
        result = rally_shots.rally(self._players, balance, (server + 1) % 2)
        # Use rally attributes to get statistics
        service_str = "first" if service == 0 else "second"
        winner_list = "won" if result["winner"] == server else "lost"
        self._stats[service][service_str + " serve " + winner_list[0]] = \
            1 + self._stats[service].get(service_str + " serve " + winner_list, 0)

        return {"winner": result["winner"], "rally": result["rally"] + 1}

    def set_base_attributes(self):
        for i in range(2):
            for attribute in ["mobility", "accuracy", "strength", "serve"]:
                self._players[i]["base " + attribute] = self._players[i][attribute]

    def _tie_break(self, server):
        while max(self._points) < 7 or diff(self._points) < 2:
            result = self._play_point(server)
            self._points[result["winner"]] += 1
            self._stats[result["winner"]]["point"] = 1 + self._stats[result["winner"]].get("point", 0)
            server = (server + 1) % 2 if sum(self._points) % 2 == 1 else server
        return {"winner": self._points.index(max(self._points))}


def stamina_effect(players):
    for i in range(len(players)):
        base_val = (players[i]["stamina"] < 500) * 0.2 + (players[i]["stamina"] < 300) * 0.1 + \
                   0.1 * (players[i]["stamina"] == 0)
        higher_val = base_val + 0.2 if base_val > 0 else 0
        for attribute in ["mobility", "strength"]:
            players[i][attribute] = players[i]["base " + attribute] * \
                (higher_val * players[i]["stamina"] / 500.0 + 1 - higher_val)
        for attribute in ["accuracy", "serve"]:
            players[i][attribute] = players[i]["base " + attribute] * \
                (base_val * players[i]["stamina"] / 500.0 + 1 - base_val)
    return players
