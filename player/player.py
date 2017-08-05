import yaml
import os

from utility.utility import repeated_random, calc_time_diff


class Player:
    def __init__(self, file=None):
        if file:
            with open(file, "r") as player_file:
                stats = yaml.safe_load(player_file)
        else:
            stats = {"shot selection": int(repeated_random(15, 35, 3)),
                     "strength": int(repeated_random(15, 35, 3)),
                     "accuracy": int(repeated_random(15, 35, 3)),
                     "serve": int(repeated_random(15, 35, 3)),
                     "mobility": int(repeated_random(15, 35, 3)),
                     "height": int(repeated_random(46, 60, 6)),
                     "age": int(repeated_random(13, 16, 2)),
                     "fitness": int(repeated_random(15, 35, 3)),
                     "orders": {"default": {"first serve aggression": 3, "second serve aggression": 2,
                                            "aggression": 3, "strategy": "All Court"}},
                     "rankings": {},
                     # How to do rankings
                     "stats": {}}
        self._id = 1
        self._stats = stats

    def create_file(self):
        with open("players//used_ids.yaml", "r") as file:
            id_used = yaml.safe_load(file)
        lowest_id = max(id_used) + 1
        # TODO: See what other stuff did for this
        with open("players//players//Player_" + str(lowest_id), "w") as player_file:
            yaml.safe_dump(self._stats, player_file)

    def apply_court(self):
        pass

    def apply_strategy(self):
        pass

    def age(self):
        pass

    def set_stats(self):
        with open(os.environ["TENNIS_HOME"] + "//players//stats//baseStats.yaml", "w") as base_file:
            stats = yaml.safe_load(base_file)
        with open(os.environ["TENNIS_HOME"] + "//players//stats//Player_" + str(self._id) + ".yaml", "w") as stat_file:
            yaml.safe_dump(stats, stat_file)

    def train(self, training):
        pass

    def apply_height(self):
        pass

    def calc_ranking_points(self, current_week, current_year):
        with open(os.environ["TENNIS_HOME"] + "//players//stats//Player_" + str(self._id) + ".yaml", "r") as stat_file:
            competitions = yaml.safe_load(stat_file)
        mandatory = competitions["events mandatory"]
        competitions = competitions["competition results"]

        junior_events = {competition: competitions[competition]["ranking points"]
                         for competition in competitions if competitions[competition]["style"] in
                         ["Junior", "Junior Doubles"] and competitions[competition]["year"] < 104}
        single_events = {competition: competitions[competition]["ranking points"]
                         for competition in competitions if competitions[competition]["style"] == "Single" and
                         competitions[competition]["year"] < 104}
        double_events = {competition: competitions[competition]["ranking points"]
                         for competition in competitions if competitions[competition]["style"] == "Double" and
                         competitions[competition]["year"] < 104}

    def get_game_stats(self):
        self.apply_court()
        self.apply_strategy()
        self.apply_height()
