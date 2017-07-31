from random import randint
from math import log
import os
import yaml

from utility.utility import shift_bit_length, arg_max


def set_seeds(sign_ups):
    rank = {}
    for player in sign_ups:
        with open(os.environ["TENNIS_HOME"] + "//player//players//Player_" + player + ".yaml", "r") as file:
            rank = yaml.safe_load(file)["ranking"]
            rank.update({rank, player})
    seedings = {}
    for i in range(len(sign_ups)):
        next_seed = arg_max(rank)
        seedings.update({i: next_seed})
        del rank[next_seed]
    return seedings


def create_groups(numbers, seeded_players):
    total = shift_bit_length(numbers)
    seeded_players = shift_bit_length(seeded_players)
    group = []
    list_remaining = list(range(1, total + 1))
    for i in range(1, seeded_players + 1):
        group.append([i])
        list_remaining.remove(i)
    last_group = 0
    for i in range(numbers + 1, total + 1):
        group[last_group].append(i)
        last_group = (last_group + 1) % seeded_players
        list_remaining.remove(i)

    for i in range(seeded_players):
        while len(group[i]) < int(total / seeded_players):
            next_player = list_remaining[randint(0, len(list_remaining) - 1)]
            list_remaining.remove(next_player)
            group[i].append(next_player)
    sorting = [group[0], group[1]]
    group = group[2:]

    for i in range(2, int(log(seeded_players, 2)) + 1):
        next_group = 2 ** i - max(2 ** (i - 1), 2)
        safety = sorting + [[]] * len(sorting)
        for k in range(len(sorting)):
            safety[2 * k] = sorting[k]
            if k > 0:
                safety[2 * k - 1] = []
        sorting = safety
        picked = []
        for j in range(next_group):
            picking = randint(0, next_group - 1)
            while picking in picked:
                picking = randint(0, next_group - 1)
            picked.append(picking)
            sorting[j * 2 - 1] = group[picking]
        group = group[next_group:]
    return sorting


def create_schedule(numbers, seeded_players, year, competition_name, start_day=1, qualification_rounds=999):
    sorting = create_groups(numbers, seeded_players)
    final = []
    for i in range(len(sorting)):
        final += sorting[i]
    sub_set = final[int(len(final) / 2):]
    sub_set = sub_set[::-1]
    final = final[:int(len(final) / 2)] + sub_set
    days = [(start_day + x * 2) % 7 for x in range(int(log(numbers, 2)))]
    if days[len(days) - 1] == 6 or days[len(days) - 1] == 1:
        days[len(days) - 1] = 0
    with open(os.environ["TENNIS_HOME"] + "//competitions//" + year + "//" + competition_name + ".yaml", "w") \
            as file:
        yaml.safe_dump({"round 1": final, "days": days, "seeded": seeded_players, "sign ups": {}, "rounds played": 0,
                        "qualification rounds": qualification_rounds, "competition_name": competition_name,
                        "year": year[5:]}, file)


def run_next_round(year, competition_name):
    with open(os.environ["TENNIS_HOME"] + "//competitions//" + str(year) + "//" + competition_name + ".yaml", "r") \
       as file:
        competition = yaml.safe_load(file)
    if "round 2" not in competition.keys():
        competition["seeds"] = set_seeds(competition["sign ups"])

    players_left = competition["round " + str(competition["rounds played"] + 1)]

    if competition["rounds played"] + 1 < competition["qualification rounds"]:
        # TODO: Stick in a way to grab relevant players here, need to have the players first
        # Need: a way to label the relevant seeds as byes
        competition["rounds played"] += 1
        next_round = []
        for i in range(int(len(players_left) / 2)):
            score_one = randint(0, 100) + players_left[2 * i] + 200 * (players_left[2 * i] > numbers)
            score_two = randint(0, 100) + players_left[2 * i + 1] + 200 * (players_left[2 * i + 1] > numbers)
            print("{}: {} Vs {} :{}".format(players_left[2 * i], score_one, score_two, players_left[2 * i + 1]))
            if score_one < score_two:
                next_round.append(players_left[2 * i])
            else:
                next_round.append(players_left[2 * i + 1])
        competition["round " + str(competition["rounds played"] + 1)] = next_round
        print("")
        print(players_left)
    with open(os.environ["TENNIS_HOME"] + "//competitions//" + str(year) + "//" + competition_name + ".yaml", "w") \
     as file:
        yaml.safe_dump(competition, file)
