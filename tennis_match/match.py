import random

from tennis_match.point import play_point
from utility.utility import diff


def singles_match(players, max_sets, tie_break_last_set, stats=None):
    if not stats:
        stats = {}
        for i in range(len(players)):
            stats.update({i: {}})
    sets_won = [0, 0]
    for player in players:
        player["stamina"] = 1000
    server = random.randint(0, len(players))
    players = set_base_attributes(players)
    while max(sets_won) < max_sets / 2.0 + 0.5:
        result = set_winner(players, server, tie_break_last_set or sum(sets_won) < max_sets, stats)
        sets_won[result["winner"]] += 1
        server = result["server"]
        stats = result["stats"]
    if sets_won[0] == max(sets_won):
        return {"winner": 0, "stats": stats}

    return {"winner": 1, "stats": stats, "stamina": [players[0]["stamina"], players[1]["stamina"]]}


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
