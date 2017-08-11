import yaml
import os
import math

from random import randint

from utility.utility import repeated_random, calc_time_diff, smallest_missing_in_list


class Player:
    def __init__(self, file=None, nation=None):
        if file:
            with open(file, "r") as player_file:
                self._stats = yaml.safe_load(player_file)
            self._shot_selection = self._stats["shot selection"]
            self._strength = self._stats["strength"]
            self._accuracy = self._stats["accuracy"]
            self._serve = self._stats["serve"]
            self._mobility = self._stats["mobility"]
            self._height = self._stats["height"]
            self._age = self._stats["age"]
            self._fitness = self._stats["fitness"]
            self._orders = self._stats["orders"]
            self._ranking_points = self._stats["ranking points"]
            self._player_stats = self._stats["player_stats"]
            self._id = self._stats["id"]
            self._nationality = self._stats["nationality"]
            self._name = self._stats["name"]
            self._stamina = self._stats["stamina"]
            self._strength_basis = self._stats["strength basis"]
            self._mobility_basis = self._stats["strength basis"]
            self._fitness_basis = self._stats["fitness basis"]
            self._age_factor = self._stats["age factor"]
        else:
            with open(os.environ["TENNIS_HOME"] + "//players//player_ids.yaml", "r") as file:
                id_used = yaml.safe_load(file)
            self._shot_selection = int(repeated_random(15, 35, 3))
            self._strength_basis = int(repeated_random(-176, 16, 3))
            self._mobility_basis = int(repeated_random(-176, 16, 3))
            self._fitness_basis = int(repeated_random(-176, 16, 3))
            self._age_factor = int(repeated_random(-2, 2, 2))
            self._age = int(repeated_random(13, 16, 2))
            str_constant = self._strength_basis - self._age_factor * self._age_factor - 2 * 28 * self._age_factor
            str_mult = 56 + 2 * self._age_factor
            self._strength = int((-self._age * self._age + str_mult * self._age + str_constant) / 10.0)
            self._accuracy = int(repeated_random(15, 35, 3))
            self._serve = int(repeated_random(15, 35, 3))
            mob_constant = self._mobility_basis - self._age_factor * self._age_factor - 2 * 22 * self._age_factor
            mob_mult = 44 + 2 * self._age_factor
            self._mobility = int((-self._age * self._age + mob_mult * self._age + mob_constant) / 10.0)
            self._height = int(repeated_random(135, 172, 4))
            for _ in range(13, self._age):
                self._height += repeated_random(1, 9, 3)
            fit_constant = self._fitness_basis - self._age_factor * self._age_factor - 2 * 22 * self._age_factor
            self._fitness = int((-self._age * self._age + str_mult * self._age + fit_constant) / 10.0)
            self._stamina = 1000
            self._orders = {"default": {"first serve aggression": 3, "second serve aggression": 2,
                                        "aggression": 3, "strategy": "All Court"}}
            self._ranking_points = {}
            self._player_stats = {}
            self._id = smallest_missing_in_list(id_used)
            self._nationality = self.set_nationality(nation)
            self._name = self.name_player()
            self._stats = {"shot selection": self._shot_selection, "strength": self._strength, "stamina": 1000,
                           "accuracy": self._accuracy, "serve": self._serve, "mobility": self._mobility,
                           "height": self._height, "age": self._age, "fitness": self._fitness, "orders": self._orders,
                           "ranking points": self._ranking_points, "player stats": self._player_stats, "id": self._id,
                           "nationality": self._nationality, "name": self._name, "strength basis": self._strength_basis,
                           "mobility basis": self._mobility_basis, "fitness basis": self._fitness_basis,
                           "age factor": self._age_factor}
            self.create_file()
        self._match_serve = self._strength
        self._match_mobility = self._mobility

    @staticmethod
    def set_nationality(nation):
        if nation is not None:
            return nation
        with open(os.environ["TENNIS_HOME"] + "//players//nationalities.yaml", "r") as file:
            nationalities = yaml.safe_load(file)
        big_list = []
        for nation in nationalities:
            big_list += [nation] * int(nationalities[nation])
        return big_list[randint(0, len(big_list) - 1)]

    def create_file(self):
        with open(os.environ["TENNIS_HOME"] + "//players//player_ids.yaml", "r") as file:
            id_used = yaml.safe_load(file)
        id_used.append(self._id)
        with open(os.environ["TENNIS_HOME"] + "//players//player_ids.yaml", "w") as file:
            yaml.safe_dump(id_used, file)
        with open(os.environ["TENNIS_HOME"] + "//players//players//Player_" + str(self._id) + ".yaml", "w") \
                as player_file:
            yaml.safe_dump(self._stats, player_file)

    def name_player(self):
        # TODO: Break the files into different countries
        # Maybe if the country file is in here use it, else use US file
        with open(os.environ['TENNIS_HOME'] + "//players//names//list_of_names.yaml", "r") as file:
            names = yaml.safe_load(file)
        random_first = randint(0, 99)
        random_second = randint(0, 99)
        set_nation = self._nationality if self._nationality in names.keys() else "United States of America"
        first_name = names[set_nation]["first"][random_first]
        second_name = names[set_nation]["second"][random_second]
        return first_name + " " + second_name

    def apply_court(self):
        pass

    def apply_strategy(self):
        pass

    def age(self):
        self._age += 1
        str_constant = self._strength_basis - self._age_factor * self._age_factor - 2 * 28 * self._age_factor
        str_mult = 56 + 2 * self._age_factor
        self._strength = int((-self._age * self._age + str_mult * self._age + str_constant) / 10.0)
        mob_constant = self._mobility_basis - self._age_factor * self._age_factor - 2 * 22 * self._age_factor
        mob_mult = 44 + 2 * self._age_factor
        self._mobility = int((-self._age * self._age + mob_mult * self._age + mob_constant) / 10.0)
        fit_constant = self._fitness_basis - self._age_factor * self._age_factor - 2 * 22 * self._age_factor
        self._fitness = int((-self._age * self._age + str_mult * self._age + fit_constant) / 10.0)
        self._height += repeated_random(1, 9, 3)

    def set_stats(self):
        with open(os.environ["TENNIS_HOME"] + "//players//stats//baseStats.yaml", "w") as base_file:
            stats = yaml.safe_load(base_file)
        with open(os.environ["TENNIS_HOME"] + "//players//stats//Player_" + str(self._id) + ".yaml", "w") as stat_file:
            yaml.safe_dump(stats, stat_file)

    def train(self, training):
        pass

    def apply_height(self):
        change_serve = 1 / float(1 + math.exp(-0.2 * (self._height - 185))) / 5 + 0.9
        change_serve = 1 - 2 * (1 - change_serve) if change_serve < 1 else change_serve
        self._match_serve *= change_serve
        change_mobility = 1 / float(1 + math.exp(-0.2 * (185 - self._height))) / 5 + 0.9
        change_mobility = 1 - 2 * (1 - change_mobility) if change_mobility < 1 else change_mobility
        self._match_mobility *= change_mobility

    def get_game_stats(self):
        self.apply_court()
        self.apply_strategy()
        self.apply_height()

for i in range(1001):
    Player()
