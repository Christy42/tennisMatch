from tennis_match import match
import time
from utility.utility import divide_diff_by_int, add_lists

basic_Value = 50


def define_player(serve=basic_Value, strength=basic_Value, mobility=basic_Value, accuracy=basic_Value,
                  shot_selection=basic_Value, aggression=5, first_serve_aggression=5, second_serve_aggression=3,
                  fitness=basic_Value):
    return {"mobility": mobility, "strength": strength, "accuracy": accuracy, "serve": serve,
            "shot selection": shot_selection, "aggression": aggression, "fitness": fitness,
            "first serve aggression": first_serve_aggression, "second serve aggression": second_serve_aggression}


def define_player_plain(basic_value):
    return {"mobility": basic_value, "strength": basic_value, "accuracy": basic_value, "serve": basic_value,
            "shot selection": basic_value, "aggression": 5, "fitness": basic_value,
            "first serve aggression": 6, "second serve aggression": 3}


def set_players():
    player_zero = define_player()
    player_one = define_player(fitness=0)
    return [player_zero, player_one]


loops = 10
total = 0
stats = {}
stamina = [0, 0]
start = time.time()
for i in range(loops):
    result = match.singles_match(set_players(), 3, True, stats=stats)
    total += result["winner"]
    stats = result["stats"]
    stamina = add_lists(result["stamina"], stamina)
    print("{}: {}".format(i, total))
end = time.time()
print((end - start) / float(loops))
print(total / float(loops))
print(divide_diff_by_int(stats, loops))
print(stamina[0] / float(loops))
