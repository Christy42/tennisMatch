import os
import yaml
import datetime
import random


def generate_pro_tour(first_jan, tour):
    first_monday = 1 + (first_jan == "Tuesday") * 6 + (first_jan == "Wednesday") * 5 + (first_jan == "Thursday") * 4 + \
                   (first_jan == "Friday") * 3 + (first_jan == "Saturday") * 2 + (first_jan == "Sunday")
    for event in tour:
        tour[event]["date"] = datetime.date(2000, tour[event]["start month"], tour[event]["start date"])
    cur_date = datetime.date(2000, 1, first_monday)
    calender = {}
    while cur_date < datetime.date(2001, 1, 1):
        calender[str(cur_date)] = []
        for event in tour:
            if tour[event]["date"] < cur_date < tour[event]["date"] + datetime.timedelta(days=7):
                calender[str(cur_date)].append(event)
        cur_date += datetime.timedelta(days=7)
    return calender


def generate_senior_competitions(calender, seasons):
    season = seasons["default"]
    for cur_date in calender:
        number_of_comps_futures = random.randint(4, 9)
        cur_date = datetime.datetime.strptime(cur_date, '%Y-%m-%d').date()
        number_of_comps = random.randint(2, 5) if cur_date < datetime.date(2000, 11, 20) else 0
        for i in range(max(number_of_comps, number_of_comps_futures)):
            if i < number_of_comps:
                level_num = random.randint(1, 9)
                court = ["clay", "grass", "hard", "indoor"][random.randint(0, 3)]
                court = ["clay", "grass", "hard", "indoor"][random.randint(0, 3)] if court != season else court
                hospitality = "+h" if level_num % 2 == 1 else ""
                level = str(int((level_num + 2) / 2.0)) + hospitality
                calender[str(cur_date)].append("CH" + str(level) + " (" + court + ")")
            if i < number_of_comps_futures:
                level_future = random.randint(1, 3)
                court_future = ["clay", "grass", "hard", "indoor"][random.randint(0, 3)]
                hospitality_future = "+h" if level_future == 3 else ""
                level_future = str(int((level_future + 1) / 2.0)) + hospitality_future
                calender[str(cur_date)].append("F" + str(level_future) + " (" + court_future + ")")
        for competition in seasons:
            season = seasons[competition] if competition in calender[str(cur_date)] else season
    return calender


def generate_junior_tour(calender):
    for cur_date in calender:
        number_of_comps = random.randint(6, 15)
        for competition in range(number_of_comps):
            level = random.randint(1, 5)
            court = ["clay", "grass", "hard", "indoor"][random.randint(1, 3)]
            calender[str(cur_date)].append("JG" + str(level) + " (" + court + ")")
    return calender


def generate_calender(first_jan, year):
    with open(os.environ["TENNIS_HOME"] + "//competitions//competition_config//ATPTour.yaml", "r") as tour_file:
        tour = yaml.safe_load(tour_file)
    with open(os.environ["TENNIS_HOME"] + "//competitions//competition_config//Seasons.yaml", "r") as season_file:
        season_change = yaml.safe_load(season_file)
    calender = generate_pro_tour(first_jan, tour)
    calender = generate_senior_competitions(calender, season_change)
    calender = generate_junior_tour(calender)
    for element in calender:
        for i in range(len(calender[element])):
            calender[element][i] += "((" + str(i) + "-" + str(element) + "))"
    with open(os.environ["TENNIS_HOME"] + "//competitions//year " + str(year) + "//calender.yaml", "w") as cal_file:
        yaml.safe_dump(calender, cal_file)


# generate_calender("Tuesday", 2000)
