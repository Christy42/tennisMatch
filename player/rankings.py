import yaml
import os
import datetime
import random


# tie breaks, 1000 + events score, highest score, second highest score etc, random 1, random 2
# I need format to be competitions = {date: {event level: level, ranking points: score, event name: name, court: court}}
def update_rankings():
    rankings = {}
    for file in os.listdir("players//players"):
        with open("players//players//" + file, "r") as player_file:
            player = yaml.safe_load(player_file)
            tournaments = player["rankings"]
            name = player["name"]
            id = player["id"]
        rankings.update({file[7:]: {"ranking points": sum(list(tournaments.values())), "name": name}})
    with open("players//rankings.yaml", "w") as ranking_file:
        yaml.safe_dump(rankings, ranking_file)


def update_player_rankings(last_year):
    # format it as ranking points = {senior: {point: , tie breakers: {1000: 1:,...., random_one, random_two}}}
    with open(os.environ["TENNIS_HOME"] + "//competitions//competition_config//mandatoryCompetitions.yaml", "r") as fi:
        mandatory_competitions = yaml.safe_load(fi)
    for file in os.listdir(os.environ["TENNIS_HOME"] + "//players//players"):
        with open(os.environ["TENNIS_HOME"] + "//players//players//" + file, "r") as player_file:
            player = yaml.safe_load(player_file)
        mandatory = player["mandatory"]
        competitions = player["tournaments"]
        junior = get_ranking_points("junior", 6, 1000, competitions, last_year)
        junior_doubles = get_ranking_points("junior doubles", 6, 1000, competitions, last_year)
        doubles = get_ranking_points("junior doubles", 14, 1000, competitions, last_year)
        if junior is not None:
            junior = {"points": junior["points"] + junior_doubles["points"] / 4.0,
                      "tie breakers": junior["tie breakers"]}
        if not mandatory:
            senior = get_ranking_points("singles", 18, 1000, competitions, last_year)
        else:
            other_comps = {week: competitions[week] for week in competitions
                           if competitions[week]["name"] not in mandatory_competitions}
            other_comps = get_ranking_points("singles", 4, 0, other_comps, last_year)["tie breakers"]

            del other_comps["random 1"]
            del other_comps["random 2"]
            del other_comps["ATP Score"]
            list_comps = [other_comps[tier]["name"] for tier in other_comps]
            main_comps = {week: competitions[week] for week in competitions
                          if competitions[week]["name"] in mandatory_competitions + list_comps}
            senior = get_ranking_points("singles", 18, 1000, main_comps, last_year)
        competitions = {date_comp: competitions[date_comp] for date_comp in competitions
                        if competitions[date_comp]["court"] == "grass"}
        wimbledon_two_year = get_ranking_points("singles", 9999, 1000, competitions,
                                                last_year - datetime.timedelta(days=365))
        wimbledon_one_year = get_ranking_points("singles", 9999, 1000, competitions,
                                                last_year)
        wimbledon = {"points": senior["points"] + 0.75 * wimbledon_two_year["points"] +
                     0.25 * wimbledon_one_year["points"], "tie breakers": wimbledon_two_year["tie breakers"]}
        player["ranking_points"] = {"senior": senior, "doubles": doubles, "junior": junior, "wimbledon": wimbledon}
        print(senior)
        print(doubles)
        print(junior)
        print(wimbledon)
        # TODO: Add on tour finals as an extra, ensure it is not part of it
        with open(os.environ["TENNIS_HOME"] + "//players//players//" + file, "w") as player_file:
            yaml.safe_dump(player, player_file)


def get_ranking_points(style, number, tie_break_level, competitions, last_year, mandatory=None):
    main_tie_break = 0
    tie_breakers = {i: {"level": 0, "score": 0, "name": "default"} for i in range(1, number + 1)}
    if competitions is None:
        return {"tie breakers": {"random 1": random.random(), "random 2": random.random(), "ATP Score": 0}, "points": 0}
    senior_comps = {date_comp: competitions[date_comp] for date_comp in competitions
                    if date_comp > last_year and competitions[date_comp]["style"] == style}
    if senior_comps is None:
        return {"tie breakers": {"random 1": random.random(), "random 2": random.random(), "ATP Score": 0}, "points": 0}
    for competition in senior_comps:
        if senior_comps[competition]["level"] >= tie_break_level:
            main_tie_break += senior_comps[competition]["score"]
        for tier in tie_breakers:
            if tie_breakers[tier]["score"] < senior_comps[competition]["score"]:
                tie_breakers = {level: tie_breakers[level - 1 * (level > tier)] for level in tie_breakers}
                tie_breakers[tier] = {"score": senior_comps[competition]["score"],
                                      "name": senior_comps[competition]["name"],
                                      "level": senior_comps[competition]["level"]}
                break
    ranking_points = sum([tie_breakers[score]["score"] for score in tie_breakers])

    tie_breakers = {element: tie_breakers[element] for element in tie_breakers
                    if tie_breakers[element]["name"] != "default"}
    tie_breakers.update({"random 1": random.random(), "random 2": random.random(), "ATP Score": main_tie_break})
    result = {"points": ranking_points, "tie breakers": tie_breakers}
    return result
update_player_rankings(datetime.date(2000, 7, 15))
