import random
import time

from tennis_match.point import play_point
from utility.utility import diff, divide_diff_by_int


def singles_match(players, max_sets, tie_break_last_set, stats={0: {}, 1: {}}):
    sets_won = [0, 0]
    for player in players:
        player["stamina"] = 1000
    server = random.randint(0, 1)
    players = set_base_attributes(players)
    while max(sets_won) < max_sets / 2.0 + 0.5:
        result = set_winner(players, server, tie_break_last_set or sum(sets_won) < max_sets, stats)
        sets_won[result["winner"]] += 1
        server = result["server"]
        stats = result["stats"]
    if sets_won[0] == max(sets_won):
        return {"winner": 0, "stats": stats}
    return {"winner": 1, "stats": stats}


def set_winner(players, server, tie_break_last_set, stats):
    games_won = [0, 0]
    while max(games_won) < 6 or diff(games_won) < 2:
        result = play_game(players, server, stats)
        games_won[result["winner"]] += 1
        server = (server + 1) % 2
        if games_won == [6, 6] and tie_break_last_set:
            res = tie_break(players, server, stats)
            games_won[res["winner"]] += 2
        stats = result["stats"]
    stats[0]["game won"] = games_won[0] + stats[0].get("game won", 0)
    stats[1]["game won"] = games_won[1] + stats[1].get("game won", 0)
    if games_won[0] == max(games_won):
        return {"winner": 0, "server": server, "stats": stats}
    return {"winner": 1, "server": server, "stats": stats}


def tie_break(players, server, stats):
    points = [0, 0]
    played = 0
    while max(points) < 7 or diff(points) < 2:
        result = play_point(players, server, stats)
        points[result["winner"]] += 1
        played += 1
        if played % 2 == 1:
            server = (server + 1) % 2
    if points[0] > points[1]:
        return {"winner": 0}
    return {"winner": 1}


def play_game(players, server, stats):
    score = [0, 0]
    while max(score) < 4 or diff(score) < 2:
        result = play_point(players, server, stats)
        score[result["winner"]] += 1
        stats = result["stats"]
        for i in range(2):
            players[i]["stamina"] -= result["rally"] / 2.0 * (1.1 - players[i]["fitness"] / 146.0)
            players[i]["stamina"] = max(players[i]["stamina"], 0.0)
        players = stamina_effect(players)
    stats[0]["points"] = score[0] + stats[0].get("points", 0)
    stats[1]["points"] = score[1] + stats[1].get("points", 0)
    if score[0] == max(score):
        return {"winner": 0, "stats": stats}
    return {"winner": 1, "stats": stats}


def stamina_effect(players):
    return players


def set_base_attributes(players):
    for i in range(2):
        for attribute in ["mobility", "accuracy", "strength", "serve"]:
            players[i]["base " + attribute] = players[i][attribute]
    return players

player_one = {"shot selection": 50, "mobility": 50, "accuracy": 50, "serve": 50, "strength": 50, "aggression": 5,
              "first serve aggression": 6, "second serve aggression": 3, "fitness": 50, "name": "Nadal"}
player_two = {"shot selection": 50, "mobility": 50, "accuracy": 60, "serve": 50, "strength": 50, "aggression": 5,
              "first serve aggression": 6, "second serve aggression": 3, "fitness": 50, "name": "Federer"}


# player_one = {"shot selection": 30, "mobility": 30, "accuracy": 30, "serve": 30, "strength": 30, "aggression": 8,
#              "first serve aggression": 8, "second serve aggression": 5, "fitness": 50, "name": "Nadal"}
# player_two = {"shot selection": 30, "mobility": 30, "accuracy": 30, "serve": 30, "strength": 30, "aggression": 3,
#              "first serve aggression": 3, "second serve aggression": 2, "fitness": 50, "name": "Federer"}
count = 0
loops = 100
stats = {0: {}, 1: {}}
start = time.time()
for i in range(loops):
    result = singles_match([player_one, player_two], 5, False, stats)
    count += result["winner"]
    stats = result["stats"]
    print("{}:   {}".format(i, count))
end = time.time()
print((end - start)/ float(loops))
print(count / float(loops))
print(divide_diff_by_int(stats, loops))

