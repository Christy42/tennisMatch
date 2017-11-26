from random import randint
from math import log
import os
import yaml
import datetime
import pandas


# TODO: Change competition into a classes?  Need to fully plan out how it looks

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


# Creates competition files for the next 21 dats
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


# Creates a specific competition file and its qualification file
def create_competition_file(competition, start_date):
    competition_file = os.environ["TENNIS_HOME"] + "//competitions//competition_config//" + \
                       competition.split("((")[0] + "_Config.yaml"
    with open(competition_file, "r") as comp_file:
        competition_stats = yaml.safe_load(comp_file)
    competition_stats["sign ups"] = {}
    folder = competition_stats["ranking method"]
    if not os.path.isdir(os.environ["TENNIS_HOME"] + "//competitions//year " + start_date[:4] + "//" + folder):
        os.mkdir(os.environ["TENNIS_HOME"] + "//competitions//year " + start_date[:4] + "//" + folder)
    # TODO: Can I do this in one?
    schedule = create_schedule(competition_stats["numbers"], competition_stats["seeded"], start_date)
    if competition_stats["qualifying number"] > 0:
        qualifying_number = competition_stats["qualifying number"] * 2 ** competition_stats["qualifying rounds"]
        # weekend_qualification = True if competition_stats["ranking points"]["W"] < 2000 else False
        schedule_qualification = create_schedule(qualifying_number, competition_stats["qualifying seeds"], start_date,
                                                 weekend_qualification=True,
                                                 qualification_rounds=competition_stats["qualifying rounds"])
        schedule_qualification.update(competition_stats)
        schedule_qualification["sets"] = 3
        schedule_qualification["tie breaks"] = [True, True, True]
        schedule_qualification["actual file"] = os.environ["TENNIS_HOME"] + "//competitions//year " + start_date[:4] + \
            "//" + folder + "//" + schedule["days"][0] + " " + competition.split("((")[0] + " " + \
            competition.split("((")[1][:2].replace("-", "") + ".yaml"
        with open(os.environ["TENNIS_HOME"] + "//competitions//year " + start_date[:4] + "//" + folder + "//" +
                  schedule_qualification["days"][0] + " " + competition.split("((")[0] + "-qualification " +
                  competition.split("((")[1][:2].replace("-", "") + ".yaml", "w") as file:
            yaml.safe_dump(schedule_qualification, file)
        schedule["qualification file"] = os.environ["TENNIS_HOME"] + "//competitions//year " + start_date[:4] + "//" + \
            folder + "//" + schedule_qualification["days"][0] + " " + competition.split("((")[0] + "-qualification " + \
            competition.split("((")[1][:2].replace("-", "") + ".yaml"
    # with open(os.environ["TENNIS_HOME"] + "//competitions//year " + year + "//" + competition["file name"] + ".yaml",
    # "w") as file:
    #     yaml.safe_dump(competition_stats, file)
    # Create file for qualification and for normal competition
    schedule.update(competition_stats)
    with open(os.environ["TENNIS_HOME"] + "//competitions//year " + start_date[:4] + "//" + folder + "//" +
              schedule["days"][0] + " " + competition.split("((")[0] + " " +
              competition.split("((")[1][:2].replace("-", "") + ".yaml", "w") as file:
        yaml.safe_dump(schedule, file)


# Create the schedule for a competition (or qualification)
def create_schedule(numbers, seeded_players, start_date, weekend_qualification=False, qualification_rounds=999):
    # TODO: Maybe redo?  Have two days as a specific pointer?
    sorting = create_groups(numbers, seeded_players)
    final = []
    start_day = 0
    for i in range(len(sorting)):
        final += sorting[i]
    sub_set = final[int(len(final) / 2):]
    sub_set = sub_set[::-1]
    final = final[:int(len(final) / 2)] + sub_set
    days = [(start_day + x) % 7 for x in range(int(log(numbers, 2)))]
    days = days[:min(qualification_rounds, len(days))]
    if qualification_rounds < 999 and weekend_qualification:
        days = [days[i] - 2 for i in range(len(days))]
    elif qualification_rounds < 999:
        days = [days[i] - 7 for i in range(len(days))]
    if days[len(days) - 1] == 6 or days[len(days) - 1] == 1:
        days[len(days) - 1] = 0
    days = [(datetime.datetime.strptime(start_date, "%Y-%m-%d") + datetime.timedelta(days[i])).strftime("%Y-%m-%d")
            for i in range(len(days))]
    days.sort()
    ans = {"round 1": final, "days": days}
    return ans


def get_rankings(number_required, sign_ups, ranking_style):
    with open(os.environ["TENNIS_HOME"] + "//players//" + ranking_style + ".yaml", "r") as ranking_file:
        rank = yaml.safe_load(ranking_file)
    sign_up_ranking = {i: rank[i]["id"] for i in rank if rank[i]["id"] in sign_ups}
    while len(sign_ups) > number_required:
        del sign_up_ranking[max(sign_up_ranking)]
    return sign_up_ranking


def create_competition_config_file(name, numbers, seeded, qualifying_rounds, ranking_points, surface, file_name,
                                   ranking_restrictions, age_restrictions, ranking_method, qualifying_seeds,
                                   qualifying_number, sets, tie_breaks):
    if sets != len(tie_breaks):
        return "Error"
    config = {"name": name, "numbers": numbers, "seeded": seeded, "qualifying rounds": qualifying_rounds,
              "ranking points": ranking_points, "surface": surface, "ranking method": ranking_method,
              "ranking restrictions": ranking_restrictions, "age restrictions": age_restrictions,
              "qualifying seeds": qualifying_seeds, "qualifying number": qualifying_number, "sets": sets}
    with open(os.environ["TENNIS_HOME"] + "//competitions//competition_config//" + file_name + "_Config.yaml", "w") \
            as config_file:
        yaml.safe_dump(config, config_file)


def sort_out_seeding(date):
    # date format is a string YYYY-MM-DD
    # TODO: Only deals with qualification rounds?
    # Too big of a function?
    styles = ["senior", "junior"]
    pandas_dict = {i: {} for i in styles}
    data_frame = {}
    for style in styles:
        for file in os.listdir(os.environ["TENNIS_HOME"] + "//competitions//year " + date[:4] + "//" + style):
            if date in file:
                with open(os.environ["TENNIS_HOME"] + "//competitions//year " + date[:4] + "//" + style + "//" + file,
                          "r") as comp:
                    competition = yaml.safe_load(comp)
                pandas_dict[style].update({file: [competition["ranking points"]["W"]]})
        data_frame[style] = pandas.DataFrame(pandas_dict[style])
        data_frame[style] = data_frame[style].T
        if len(data_frame[style]) > 0:
            data_frame[style].columns = ["ranking points"]
            data_frame[style] = data_frame[style].sort_values(by="ranking points", ascending=False)
    print("Y")
    used_list = []
    rankings = {style: pandas.read_csv(os.environ["TENNIS_HOME"] + "//players//" + style + ".yaml") for style in styles}
    style_ranks = {style: {rankings[style]["id"][rank]: rankings[style]["index"][rank]
                           for rank in rankings[style]["id"]} for style in styles}
    for style in styles:
        for file in data_frame[style].index:
            for i in range(1 + ("-qualification" in file)):
                if "-qualification" in file and i == 0:
                    with open(os.environ["TENNIS_HOME"] + "//competitions//year " + date[:4] + "//" + style + "//" +
                              file, "r") as qualification_file:
                        actual_file = yaml.safe_load(qualification_file)["actual file"]
                else:
                    actual_file = os.environ["TENNIS_HOME"] + "//competitions//year " + date[:4] + "//" + style + \
                                  "//" + file
                with open(actual_file, "r") as comp_file:
                    competition = yaml.safe_load(comp_file)
                if "qualification" in actual_file:
                    print("qualification {}".format(file))
                    number = 2 ** competition["qualifying rounds"] * competition["qualifying number"]
                else:
                    print("normal {}".format(file))
                    number = competition["numbers"] - competition["qualifying number"]
                competition["sign ups"] = {id_number: competition["sign ups"][id_number]
                                           for id_number in competition["sign ups"] if id_number not in used_list}
                players = cut_players(style_ranks[style], competition["sign ups"], number)
                if type(players) != str:
                    competition["ranks"] = {i + 1:
                                            [str(players["id"][players.index[i]]),
                                             str(players.index[i])]
                                            for i in range(len(players.index))}
                    used_list += [players.index[i] for i in range(len(players.index))]
                    with open(actual_file, "w") as comp_file:
                        yaml.safe_dump(competition, comp_file)


def cut_players(ranks, sign_ups, number):
    # Take sign ups and make them into panda frame with ranks
    section = {}
    for element in sign_ups:
        section[element] = [sign_ups[element], ranks[element]]
    data_frame = pandas.DataFrame(section)
    data_frame = data_frame.T
    if len(data_frame) == 0:
        return ""
    data_frame.columns = ["id", "rank"]
    data_frame = data_frame.sort_values(by="rank", ascending=True)
    data_frame = data_frame[:number]
    # data_frame = data_frame.reset_index()
    # print(data_frame)
    return data_frame


def create_match(player_1, player_2, year, competition_file, competition, round_number, rank_nos, competition_folder):
    with open(os.environ["TENNIS_HOME"] + "//players//players//Player_" + str(player_1) + ".yaml", "r") as player_file:
        player = yaml.safe_load(player_file)
    name = [player["name"]]
    with open(os.environ["TENNIS_HOME"] + "//players//players//Player_" + str(player_2) + ".yaml", "r") as player_file:
        player = yaml.safe_load(player_file)
    with open(competition_folder + "//" + competition_file) as comp_file:
        round_date = yaml.safe_load(comp_file)["days"][int(round_number) - 1]
    name.append(player["name"])
    details = {"stats": {}, "player_ids": [player_1, player_2], "court": competition["surface"],
               "sets": competition["sets"], "tie breaks": competition["tie breaks"],
               "style": competition["ranking method"], "competition name": competition_file,
               "commentary file": os.environ["TENNIS_HOME"] + "//matches//commentary//year " + str(year) + "//" +
               competition_file.replace(".yaml", "") + "_commentary.yaml", "date": round_date,
               "player names": name, "rank numbers": rank_nos}
    if not os.path.isdir(os.environ["TENNIS_HOME"] + "//matches//year " + str(year)):
        print("hi")
        os.makedirs(os.environ["TENNIS_HOME"] + "//matches//year " + str(year))
    if not os.path.isdir(os.environ["TENNIS_HOME"] + "//matches//year " + str(year) + "//" + competition_file):
        os.makedirs(os.environ["TENNIS_HOME"] + "//matches//year " + str(year) + "//" + competition_file)
    with open(os.environ["TENNIS_HOME"] + "//matches//year " + str(year) + "//" + competition_file + "//" + "round " +
              str(round_number) + " " + str(player_1) + "vs" + str(player_2) + " " + details["date"] + ".yaml", "w") \
            as match_file:
        yaml.safe_dump(details, match_file)


def create_bye(player_1, year, competition_file, competition, round_number, rank_nos, competition_folder):
    with open(competition_folder + "//" + competition_file) as comp_file:
        round_date = yaml.safe_load(comp_file)["days"][int(round_number) - 1]
    with open(os.environ["TENNIS_HOME"] + "//players//players//Player_" + player_1 + ".yaml", "r") as player_file:
        player = yaml.safe_load(player_file)
    name = [player["name"], "BYE"]
    details = {"stats": {}, "player_ids": [player_1, "BYE"], "court": competition["surface"],
               "sets": competition["sets"], "tie breaks": competition["tie breaks"],
               "style": competition["ranking method"], "competition name": competition_file,
               "commentary file": os.environ["TENNIS_HOME"] + "//matches//commentary//year " + str(year) + "//" +
               competition_file.replace(".yaml", "") + "_commentary.yaml", "date": round_date,
               "player names": name, "rank numbers": rank_nos}
    with open(os.environ["TENNIS_HOME"] + "//matches//year " + str(year) + "//" + competition_file + "//" +
              "round " + str(round_number) + " " + str(player_1) + "vs" + "BYE " + details["date"] + ".yaml", "w") \
            as match_file:
        yaml.safe_dump(details, match_file)


def make_match_files(competition_folder, competition_file, year, roun):
    with open(competition_folder + "//" + competition_file, "r") as file:
        competition = yaml.safe_load(file)
    if "ranks" not in competition:
        return 0

    for i in range(int(len(competition["round " + str(roun)]) / 2)):
        seeds_playing = [competition["round " + str(roun)][2 * i], competition["round " + str(roun)][2 * i + 1]]
        if competition["round " + str(roun)][2 * i] not in competition["ranks"]:
            create_bye(competition["ranks"][competition["round " + str(roun)][2 * i + 1]][1], year, competition_file,
                       competition, roun, seeds_playing, competition_folder)
        elif competition["round " + str(roun)][2 * i + 1] not in competition["ranks"]:
            create_bye(competition["ranks"][competition["round " + str(roun)][2 * i]][1], year, competition_file,
                       competition, roun, seeds_playing, competition_folder)
        else:
            create_match(competition["ranks"][competition["round " + str(roun)][2 * i]][1],
                         competition["ranks"][competition["round " + str(roun)][2 * i + 1]][1], year, competition_file,
                         competition, roun, seeds_playing, competition_folder)


def all_match_files(date, round_number):
    for style in ["junior", "senior"]:
        for file in os.listdir(os.environ["TENNIS_HOME"] + "//competitions//year " + str(date[:4]) + "//" + style):
            if date in file:
                make_match_files(os.environ["TENNIS_HOME"] + "//competitions//year " + str(date[:4]) + "//" + style,
                                 file, date[:4], round_number)


def generate_mapping(ranking_points, round_1):
    basic_mapping = {"W": 1, "F": 2, "SF": 4, "QF": 8}
    cur_round = 1
    while True:
        if "R" + str(cur_round) not in ranking_points:
            break
        basic_mapping.update({"R" + str(cur_round): int(len(round_1) / cur_round)})
        cur_round += 1
    final_mapping = {basic_mapping[element]: ranking_points[element] for element in basic_mapping}
    return final_mapping


def split_into_matches(round_list):
    match = []
    if len(round_list) <= 1 or len(round_list) % 2 == 1:
        return [round_list]
    for i in range(int(len(round_list) / 2.0)):
        match.append([round_list[2 * i], round_list[2 * i + 1]])
    return match


def get_opponents(round_list, seed):
    matches = split_into_matches(round_list)
    for element in matches:
        if seed in element:
            for player in element:
                if player != seed:
                    return player
    return seed


def generate_points(competition):
    # TODO: Need to output the level they reached as well I guess
    # TODO: Add in the ATP level of the competition
    # TODO: Need to deal with qualification ranking points
    key = {b: competition["ranks"][b][1] for b in competition["ranks"]}
    mapping = generate_mapping(competition["ranking points"], competition["round 1"])
    rounds = {round_no: competition[round_no] for round_no in competition if "round" in round_no}
    seeds_to_points = {}
    for i in range(len(rounds) - 1, 0, -1):
        if i > 1:
            split_into_matches(rounds["round " + str(i - 1)])
        for element in rounds["round " + str(i)]:
            opponent = get_opponents(rounds["round " + str(i - 1)], element) if i > 1 else element
            if element not in seeds_to_points and opponent in key:
                seeds_to_points[element] = mapping[len(rounds["round " + str(i)])]
    id_to_points = {key[element]: seeds_to_points[element] for element in key}
    return id_to_points


# print(create_schedule(32, 8, "2000-01-08", True, 2))
# print(create_schedule(32, 8, "2000-01-08"))
# sort_out_seeding("2000-01-05")
# all_match_files("2000-01-07", 1)
# create_competition_files()
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
