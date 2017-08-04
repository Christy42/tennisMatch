import os
import yaml
import datetime
import random


def generate_pro_tour(first_jan, year):
    first_monday = 1 + (first_jan == "Tuesday") * 6 + (first_jan == "Wednesday") * 5 + (first_jan == "Thursday") * 4 + \
                   (first_jan == "Friday") * 3 + (first_jan == "Saturday") * 2 + (first_jan == "Sunday")
    with open(os.environ["TENNIS_HOME"] + "//competitions//competition_config//ATPTour.yaml", "r") as tour_file:
        tour = yaml.safe_load(tour_file)
    for event in tour:
        tour[event]["date"] = datetime.date(2000, tour[event]["start month"], tour[event]["start date"])
    cur_date = datetime.date(2000, 1, first_monday)
    calender = {}
    while cur_date < datetime.date(2001, 1, 1):
        calender[str(cur_date)] = []
        print(cur_date)
        for event in tour:
            if tour[event]["date"] < cur_date < tour[event]["date"] + datetime.timedelta(days=7):
                calender[str(cur_date)].append(event)
        cur_date += datetime.timedelta(days=7)
    with open(os.environ["TENNIS_HOME"] + "//competitions//year " + str(year) + "//calender.yaml", "w") as cal_file:
        yaml.safe_dump(calender, cal_file)


def generate_senior_competitions(first_jan, year):
    first_monday = 1 + (first_jan == "Tuesday") * 6 + (first_jan == "Wednesday") * 5 + (first_jan == "Thursday") * 4 + \
                   (first_jan == "Friday") * 3 + (first_jan == "Saturday") * 2 + (first_jan == "Sunday")
    with open(os.environ["TENNIS_HOME"] + "//competitions//year " + str(year) + "//calender.yaml", "r") as cal_file:
        calender = yaml.safe_load(cal_file)
    cur_date = datetime.date(2000, 1, first_monday)
    season = "hard"
    while cur_date < datetime.date(2001, 1, 1):
        number_of_comps_futures = random.randint(4, 9)
        if cur_date < datetime.date(2000, 11, 20):
            print(season)
            number_of_comps = random.randint(2, 5)
            for i in range(number_of_comps):
                level = random.randint(1, 9)
                court = ["clay", "grass", "hard", "indoor"][random.randint(1, 3)]
                if court != season:
                    court = ["clay", "grass", "hard", "indoor"][random.randint(1, 3)]
                hospitality = "+h" if level % 2 == 1 else ""
                level = str(int((level + 1) / 2.0)) + hospitality
                calender[str(cur_date)].append("CH" + str(level) + " (" + court + ")")
        for i in range(number_of_comps_futures):
            level = random.randint(1, 3)
            court = ["clay", "grass", "hard", "indoor"][random.randint(1, 3)]
            hospitality = "+h" if level == 3 else ""
            level = str(int((level + 1) / 2.0)) + hospitality
            calender[str(cur_date)].append("F" + str(level) + " (" + court + ")")
        if "Miami Open" in calender[str(cur_date)]:
            season = "clay"
        elif "French Open" in calender[str(cur_date)]:
            season = "grass"
        elif "Hall of Fame Championships" in calender[str(cur_date)]:
            season = "hard"
        elif "US Open" in calender[str(cur_date)]:
            season = "indoor"
        cur_date += datetime.timedelta(days=7)

    with open(os.environ["TENNIS_HOME"] + "//competitions//year " + str(year) + "//calender.yaml", "w") as cal_file:
        yaml.safe_dump(calender, cal_file)


def generate_junior_tour(first_jan, year):
    first_monday = 1 + (first_jan == "Tuesday") * 6 + (first_jan == "Wednesday") * 5 + (first_jan == "Thursday") * 4 + \
                   (first_jan == "Friday") * 3 + (first_jan == "Saturday") * 2 + (first_jan == "Sunday")
    with open(os.environ["TENNIS_HOME"] + "//competitions//year " + str(year) + "//calender.yaml", "r") as cal_file:
        calender = yaml.safe_load(cal_file)
    cur_date = datetime.date(2000, 1, first_monday)
    while cur_date < datetime.date(2001, 1, 1):
        number_of_comps = random.randint(6, 15)
        for competition in range(number_of_comps):
            level = random.randint(1, 5)
            court = ["clay", "grass", "hard", "indoor"][random.randint(1, 3)]
            calender[str(cur_date)].append("JG" + str(level) + " (" + court + ")")
        cur_date += datetime.timedelta(days=7)
    with open(os.environ["TENNIS_HOME"] + "//competitions//year " + str(year) + "//calender.yaml", "w") as cal_file:
        yaml.safe_dump(calender, cal_file)


def generate_calender(first_jan, year):
    generate_pro_tour(first_jan, year)
    generate_senior_competitions(first_jan, year)
    generate_junior_tour(first_jan, year)

generate_calender("Tuesday", 0)
