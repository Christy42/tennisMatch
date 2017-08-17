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
                if date <= datetime.datetime.strptime(week, "%Y-%m-%d") <= date + datetime.timedelta(days=21)}
    for week in calender:
        for i in range(len(calender[week])):
            if os.path.isfile(os.environ["TENNIS_HOME"] + "//competitions//year " + str(date.year) + "//" + str(i) +
                              ".yaml"):
                pass
            else:
                create_competition_file(calender[week][i], week)


def create_competition_file(competition, start_date):
    competition_file = os.environ["TENNIS_HOME"] + "//competitions//competition_config//" + \
                       competition.split("((")[0] + "_Config.yaml"
    with open(competition_file, "r") as comp_file:
        competition_stats = yaml.safe_load(comp_file)
    competition_stats["sign ups"] = {}
    folder = competition_stats["ranking method"]
    if not os.path.isdir(os.environ["TENNIS_HOME"] + "//competitions//year " + start_date[:4] + "//" + folder):
        os.mkdir(os.environ["TENNIS_HOME"] + "//competitions//year " + start_date[:4] + "//" + folder)
    # TODO: Create qualifying section
    if competition_stats["qualifying number"] > 0:
        qualifying_number = competition_stats["qualifying number"] * 2 ** competition_stats["qualifying rounds"]
        weekend_qualification = True if competition_stats["ranking points"]["W"] < 2000 else False
        schedule_qualification = create_schedule(qualifying_number, competition_stats["qualifying seeds"], start_date,
                                                 weekend_qualification, competition_stats["qualifying rounds"])
        schedule_qualification.update(competition_stats)
        with open(os.environ["TENNIS_HOME"] + "//competitions//year " + start_date[:4] + "//" + folder + "//" +
                  schedule_qualification["days"][0] + " " + competition.split("((")[0] + "-qualification.yaml",
                  "w") as file:
            yaml.safe_dump(schedule_qualification, file)
    # TODO: Create actual competition
    schedule = create_schedule(competition_stats["numbers"], competition_stats["seeded"], start_date)
    # with open(os.environ["TENNIS_HOME"] + "//competitions//year " + year + "//" + competition["file name"] + ".yaml",
    # "w") as file:
    #     yaml.safe_dump(competition_stats, file)
    # Create file for qualification and for normal competition
    # end the file name with qualification.  Should I also include the date?
    # Stick with this folder structure all in one.  Or go by month.  Or go by type of competition?
    # TODO:  Do sign ups (not here obviously)
    schedule.update(competition_stats)
    with open(os.environ["TENNIS_HOME"] + "//competitions//year " + start_date[:4] + "//" + folder + "//" +
              schedule["days"][0] + " " + competition.split("((")[0] + ".yaml", "w") as file:
        yaml.safe_dump(schedule, file)


def create_schedule(numbers, seeded_players, start_date, weekend_qualification=False, qualification_rounds=999):
    # 0 = Sunday,....
    sorting = create_groups(numbers, seeded_players)
    final = []
    start_day = 1
    for i in range(len(sorting)):
        final += sorting[i]
    sub_set = final[int(len(final) / 2):]
    sub_set = sub_set[::-1]
    final = final[:int(len(final) / 2)] + sub_set
    days = [(start_day + x * 2) % 7 for x in range(int(log(numbers, 2)))]
    days = days[:min(qualification_rounds, len(days))]
    if weekend_qualification:
        days = [-1] * (len(days) - int(len(days) / 2.0)) + [0] * int(len(days) / 2.0)
    elif qualification_rounds < 999:
        days = [days[i] - 7 for i in range(len(days))]
    if days[len(days) - 1] == 6 or days[len(days) - 1] == 1:
        days[len(days) - 1] = 0
    days = [(datetime.datetime.strptime(start_date, "%Y-%m-%d") + datetime.timedelta(days[i])).strftime("%Y-%m-%d")
            for i in range(len(days))]
    # TODO: Turn days into strings
    ans = {"round 1": final, "days": days}
    return ans


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
            if score_one < score_two:
                next_round.append(players_left[2 * i])
            else:
                next_round.append(players_left[2 * i + 1])
        competition["round " + str(competition["rounds played"] + 1)] = next_round
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


# create_competition_config_file(name="Qatar Open", numbers=128, seeded=8, qualifying_rounds=2,
#                                ranking_points={"F": 1200, "Q": 25, "Q1": 0, "Q2": 8, "Q3": 16, "QF": 360, "R1": 10,
#                                                "R2": 45, "R3": 90, "R4": 180, "SF": 720, "W": 2000},
#                                ranking_restrictions={}, age_restrictions={}, ranking_method="senior", surface="hard",
#                                file_name="Qatar Open", qualifying_number=16, qualifying_seeds=32)

# create_competition_files()
# Grand Slam	2000	1200	720	360	180	90	45	10	25
# ATP World Tour Finals	+500
#                     (1500 max)	+400
#                                (1000 max)	(200 for each round robin match win)
#                                              (600 max)
# Masters       1000	1000	600	360	180	90	45	10 (25)	(10)	25 (16)
# 500 Series	 500	300	180	90	45	(20)			20 (10)
# 250 Series	 250	150	 90	45	20	(5)			12 (5)
#                       125	75	45	25	10	5
# Challenger 125,000	110	65	40	20	9	5
# Challenger 100,000	100	60	35	18	8	5
# Challenger 75,000	     90	55	33	17	8	5
# Challenger 50,000	     80	48	29	15	7	3
# Challenger 35,000 +H	 80	48	29	15	6	3
# Futures 15,000 +H	35	20	10	4	1
# Futures 15,000	27	15	8	3	1
# Futures 10,000 +H	27	15	8	3	1
# Futures 10,000	18	10	6	2	1
# -	                  A	   1	2	3	4	5	B1	B2	B3
# Winner	         250  150  100	60	40	30	180	120	80
# Runner-up	         180  100	75	45	30	20	120	80	50
# Semi-Finalist	     120   80	50	30	20	15	80	60	30
# Quarter-Finalist	  80   60	30	20	15	10	60	40	15
# Losers in last 16	  50   30	20	15	10	5	30	25	5
# Losers in last 32	  30   20	10	7.5	-	-	20	10	-
# Grade A Bonus Points (Youth Olympic Games, Italian Open & Orange Bowl)
# -	                 Singles      	Doubles
# Winner	           62.5	          45
# Runner-up	           45	          30
# Semi-Finalist	       30	          20
# Quarter-Finalist	   20	          12.5
# Losers in last 16	   12.5	           7.5
# Grand Slam Bonus Points
# -	                  Singles        	Doubles
# Winner               	125	              90
# Runner-up	             90	              60
# Semi-Finalist	         60	              40
# Quarter-Finalist	     40	              25
# Losers in last 16	     25	              15
# Qualifiers losing in the first round of the main draw will receive 25 ranking points.
# Players losing in the final round of qualifying will receive 20 ranking points.
