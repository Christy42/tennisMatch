import random
import math
import yaml
from tennis_match import serve, rally_shots

from utility.utility import diff
from commentary import commentary


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
        self._sets_played = ""
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

    def stamina_effect(self):
        for i in range(len(self._players)):
            base_val = (self._players[i]["stamina"] < 500) * 0.2 + (self._players[i]["stamina"] < 300) * 0.1 + \
                       0.1 * (self._players[i]["stamina"] == 0)
            higher_val = base_val + 0.2 if base_val > 0 else 0
            for attribute in ["mobility", "strength"]:
                self._players[i][attribute] = self._players[i]["base " + attribute] * \
                 (higher_val * self._players[i]["stamina"] / 500.0 + 1 - higher_val)
            for attribute in ["accuracy", "serve"]:
                self._players[i][attribute] = self._players[i]["base " + attribute] * \
                    (base_val * self._players[i]["stamina"] / 500.0 + 1 - base_val)

    def print_to_comm_file(self):
        with open(self._commentary_file, "w") as com_file:
            yaml.safe_dump(self._commentary, com_file)

    def commentary(self, tie_break, points_required=4):
        com_score = commentary.calc_game_score(self._points)
        com_line = self._sets_played + str(self._games[0]) + "-" + str(self._games[1]) + ", " + \
            com_score[0] + " : " + com_score[1]
        moment = self.calc_special_moment(tie_break, points_required=points_required)
        total = 4
        if moment["moment"] == "None":
            total = 3
        if random.randint(1, total) == 1:
            commentary.basic_comm_line(1, 1, 1, 1, 1)
        self._commentary.append(com_line)

    def basic_comm_line(self, result, moment, server):
        if moment["moment"] != "None":
            pass
        # Use basic, figure out exact moment from winner, server, rally, balance
        basic = "winner" if result["balance"] < -40 else "unforced error" if result["balance"] > 20 else ""
        basic += "long rally" if result["rally"] < -40 else "short rally" if result["balance"] > 20 else ""
        # Add in double fault, aces - replace the above if used
        # Maybe do this when we add it to the stats
        if result["balance"] < -40:
            basic = "winner"
        elif result["balance"] > 20:
            basic = "unforced error"
        # Have a file that has different scenarios upcoming
        line = "{}   {}".format(self._players[0]["name"], self._players[1]["name"])

    def calc_special_moment(self, tie_break, points_required=4):
        game_point = [True if self._points[player] >= points_required - 1 and
                      (self._points[player] > self._points[(player + 1) % 2] or not self._deuce) else False
                      for player in range(2)]
        set_game = [True if self._games[player] >= self._games_required - 1 and
                    (self._games[player] > self._games[(player + 1) % 2] or tie_break) else False
                    for player in range(2)]
        match_set = [True if self._sets[player] >= self._sets_required - 1 else False for player in range(2)]
        match_point = [True if match_set[player] and set_game[player] and game_point[player] else False
                       for player in range(2)]
        set_point = [True if set_game[player] and game_point[player] else False for player in range(2)]
        match_game = [True if set_game[player] and match_set[player] else False for player in range(2)]

        set_game = [set_game[player] if self._points == [0, 0] else False for player in range(2)]
        match_game = [match_game[player] if self._points == [0, 0] else False for player in range(2)]
        match_set = [match_set[player] if self._games == self._points == [0, 0] else False for player in range(2)]

        dict_of_moments = {"match point": match_point, "match game": match_game, "match set": match_set,
                           "set game": set_game, "set point": set_point, "game point": game_point}
        for moment in dict_of_moments:
            for player in range(2):
                if dict_of_moments[moment[player]]:
                    return {"player": player, "moment": moment}
        return {"player": "NA", "moment": "None"}