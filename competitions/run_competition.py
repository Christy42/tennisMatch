from random import randint
from math import log
import os
import yaml
import datetime
import pandas


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
        schedule_qualification["sets"] = 3
        schedule_qualification["tie breaks"] = [True, True, True]
        with open(os.environ["TENNIS_HOME"] + "//competitions//year " + start_date[:4] + "//" + folder + "//" +
                  schedule_qualification["days"][0] + " " + competition.split("((")[0] + "-qualification" +
                  competition.split("((")[1][:2].replace("-", "") + ".yaml", "w") as file:
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
              schedule["days"][0] + " " + competition.split("((")[0] + " " +
              competition.split("((")[1][:2].replace("-", "") + ".yaml", "w") as file:
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
    # TODO: Need to sort out ordering of competitions first
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
                if i == 0 and "-qualification" in file:
                    file_signifier = file[10:].replace("-qualification", " ")
                    for file_c in os.listdir(os.environ["TENNIS_HOME"] + "//competitions//year " + date[:4] + "//" +
                                             style):
                        if file_signifier in file_c:
                            if datetime.datetime.strptime(file_c[:10], "%Y-%m-%d") <= \
                               datetime.datetime.strptime(file[:10], "%Y-%m-%d") + datetime.timedelta(days=7):
                                file_temp = file_c
                else:
                    file_temp = file

                with open(os.environ["TENNIS_HOME"] + "//competitions//year " + date[:4] + "//" + style + "//" +
                          file_temp, "r") \
                        as comp_file:
                    competition = yaml.safe_load(comp_file)
                if "qualification" in file:
                    number = 2 ** competition["qualifying rounds"] * competition["qualifying number"]
                else:
                    number = competition["number"] - competition["qualifying number"]
                competition["sign ups"] = {id_number: competition["sign ups"][id_number]
                                           for id_number in competition["sign ups"] if id_number not in used_list}
                print(file_temp)
                players = cut_players(style_ranks[style], competition["sign ups"], number)
                if type(players) != str:
                    competition["ranks"] = {i + 1:
                                            [str(players["id"][players.index[i]]),
                                             str(players.index[i])]
                                            for i in range(len(players.index))}
                    used_list += [players.index[i] for i in range(len(players.index))]
                    with open(os.environ["TENNIS_HOME"] + "//competitions//year " + date[:4] + "//" + style + "//" +
                              file_temp, "w") as comp_file:
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


def create_match(player_1, player_2, year, competition_file, competition, round_number, rank_nos):
    with open(os.environ["TENNIS_HOME"] + "//players//players//Player_" + str(player_1) + ".yaml", "r") as player_file:
        player = yaml.safe_load(player_file)
    name = [player["name"]]
    with open(os.environ["TENNIS_HOME"] + "//players//players//Player_" + str(player_2) + ".yaml", "r") as player_file:
        player = yaml.safe_load(player_file)
    name.append(player["name"])
    details = {"stats": {}, "player_ids": [player_1, player_2], "court": competition["surface"],
               "sets": competition["sets"], "tie breaks": competition["tie breaks"],
               "style": competition["ranking method"], "competition name": competition_file,
               "commentary file": os.environ["TENNIS_HOME"] + "//matches//commentary//year " + str(year) + "//" +
               competition_file.replace(".yaml", "") + "_commentary.yaml", "date": competition_file[:10],
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


def create_bye(player_1, year, competition_file, competition, round_number, rank_nos):
    with open(os.environ["TENNIS_HOME"] + "//players//players//Player_" + player_1 + ".yaml", "r") as player_file:
        player = yaml.safe_load(player_file)
    name = [player["name"], "BYE"]
    details = {"stats": {}, "player_ids": [player_1, "BYE"], "court": competition["surface"],
               "sets": competition["sets"], "tie breaks": competition["tie breaks"],
               "style": competition["ranking method"], "competition name": competition_file,
               "commentary file": os.environ["TENNIS_HOME"] + "//matches//commentary//year " + str(year) + "//" +
               competition_file.replace(".yaml", "") + "_commentary.yaml", "date": competition_file[:10],
               "player names": name, "rank numbers": rank_nos}
    with open(os.environ["TENNIS_HOME"] + "//matches//year " + str(year) + "//" + competition_file + "//" +
              "round " + str(round_number) + " " + str(player_1) + "vs" + "BYE " + details["date"] + ".yaml", "w") \
            as match_file:
        yaml.safe_dump(details, match_file)


def make_match_files(competition_folder, competition_file, year, roun):
    # TODO: Ensure that it dates later round matches correctly
    with open(competition_folder + "//" + competition_file, "r") as file:
        competition = yaml.safe_load(file)
    if "ranks" not in competition:
        return 0

    for i in range(int(len(competition["round " + str(roun)]) / 2)):
        seeds_playing = [competition["round " + str(roun)][2 * i], competition["round " + str(roun)][2 * i + 1]]
        if competition["round " + str(roun)][2 * i] not in competition["ranks"]:
            create_bye(competition["ranks"][competition["round " + str(roun)][2 * i + 1]][1], year, competition_file,
                       competition, roun, seeds_playing)
        elif competition["round " + str(roun)][2 * i + 1] not in competition["ranks"]:
            create_bye(competition["ranks"][competition["round " + str(roun)][2 * i]][1], year, competition_file,
                       competition, roun, seeds_playing)
        else:
            create_match(competition["ranks"][competition["round " + str(roun)][2 * i]][1],
                         competition["ranks"][competition["round " + str(roun)][2 * i + 1]][1], year, competition_file,
                         competition, roun, seeds_playing)


def all_match_files(date, round_number):
    for style in ["junior", "senior"]:
        for file in os.listdir(os.environ["TENNIS_HOME"] + "//competitions//year " + str(date[:4]) + "//" + style):
            if date in file:
                make_match_files(os.environ["TENNIS_HOME"] + "//competitions//year " + str(date[:4]) + "//" + style,
                                 file, date[:4], round_number)
# sort_out_seeding("2000-01-06")
# all_match_files("2000-01-06", 1)
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
