from random import randint
from math import log
import os
import yaml
import datetime


from utility.utility import shift_bit_length


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


def create_competition_files():
    with open(os.environ["TENNIS_HOME"] + "//currentDate.yaml", "r") as date_file:
        date = datetime.datetime.strptime(yaml.safe_load(date_file), "%d/%m/%Y")
    with open(os.environ["TENNIS_HOME"] + "//competitions//year " + str(date.year) + "//calender.yaml", "r") as cal:
        calender = yaml.safe_load(cal)
    calender = {week: calender[week] for week in calender
                if date <= datetime.datetime.strptime(week, "%Y-%m-%d") <= date + datetime.timedelta(days=35)}
    for week in calender:
        for element in calender[week]:
            if os.path.isfile(os.environ["TENNIS_HOME"] + "//competitions//year " + str(date.year) + "//" + element +
                              ".yaml"):
                calender[week].remove(element)
            else:
                create_competition_file(element, week, str(date.year))
    print(calender)


def create_competition_file(competition, week, year):
    competition_file = os.environ["TENNIS_HOME"] + "//competitions//competition_config//" + \
                       competition.split("((")[0] + "_Config.yaml"
    with open(competition_file, "r") as comp_file:
        competition_stats = yaml.safe_load(comp_file)
    competition_stats["sign ups"] = []
    # with open(os.environ["TENNIS_HOME"] + "//competitions//year " + year + "//" + competition + ".yaml", "w") as file:
    #     yaml.safe_dump(competition_stats, file)
    print(competition_file)


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
        yaml.safe_dump({"round 1": final, "days": days, "seeded": seeded_players, "sign ups": [], "rounds played": 0,
                        "qualification rounds": qualification_rounds, "competition_name": competition_name,
                        "year": year[5:]}, file)


def run_next_round(year, competition_name):
    with open(os.environ["TENNIS_HOME"] + "//competitions//" + str(year) + "//" + competition_name + ".yaml", "r") \
       as file:
        competition = yaml.safe_load(file)
    if "round 2" not in competition.keys():
        # TODO: Need to remember what this was doing and get it doing it  better.
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


def get_rankings(number_required, sign_ups, ranking_style):
    with open(os.environ["TENNIS_HOME"] + "//players//" + ranking_style + ".yaml", "r") as ranking_file:
        rank = yaml.safe_load(ranking_file)
    sign_up_ranking = {i: rank[i]["id"] for i in rank if rank[i]["id"] in sign_ups}
    while len(sign_ups) > number_required:
        del sign_up_ranking[max(sign_up_ranking)]
    return sign_up_ranking


def create_competition_config_file(name, numbers, seeded, qualifying_rounds, ranking_points, surface, file_name,
                                   ranking_restrictions, age_restrictions, ranking_method, qualifying_seeds,
                                   qualifying_number):
    config = {"name": name, "numbers": numbers, "seeded": seeded, "qualifying rounds": qualifying_rounds,
              "ranking points": ranking_points, "surface": surface, "ranking method": ranking_method,
              "ranking restrictions": ranking_restrictions, "age restrictions": age_restrictions,
              "qualifying seeds": qualifying_seeds, "qualifying number": qualifying_number}
    with open(os.environ["TENNIS_HOME"] + "//competitions//competition_config//" + file_name + "_Config.yaml", "w") \
            as config_file:
        yaml.safe_dump(config, config_file)

create_competition_config_file(name="CH1+h", ranking_method="senior", surface="clay", file_name="CH1+h(clay)",
                               ranking_restrictions={"rank": ["greater than", 50]}, age_restrictions={},
                               qualifying_rounds=2, numbers=32, seeded=8,
                               ranking_points={"W": 80, "F": 48, "SF": 29, "QF": 15, "R2": 6, "R1": 0,
                                               "Q": 3, "Q2": 0, "Q1": 0},
                               qualifying_seeds=8, qualifying_number=4)
#                       125	75	45	25	10	5
# Challenger 125,000	110	65	40	20	9	5
# Challenger 100,000	100	60	35	18	8	5
# Challenger 75,000	     90	55	33	17	8	5
# Challenger 50,000	     80	48	29	15	7	3
# Challenger 35,000 +H	 80	48	29	15	6	3
