import yaml
import os
import datetime
import random
import pandas


# tie breaks, 1000 + events score, highest score, second highest score etc, random 1, random 2
# I need format to be competitions = {date: {event level: level, ranking points: score, event name: name, court: court}}
def update_rankings(rankings, style):
    ans = pandas.DataFrame(rankings[style])
    ans = ans.T
    sort_by = ['ranking', 'ATP Score', 'Levels']
    level = 1
    while "Level " + str(level) in ans.columns:
        sort_by.append("Level " + str(level))
        level += 1
    sort_by.append("random 1")
    sort_by.append("random 2")
    ascending = [False] * len(sort_by)
    ascending[2] = True
    ans = ans.sort_values(by=sort_by, ascending=ascending)
    print(ans)
    del ans["ATP Score"]
    level = 1
    while "Level " + str(level) in ans.columns:
        del ans["Level " + str(level)]
        level += 1
    del ans["Levels"]
    del ans["random 1"]
    del ans["random 2"]
    ans = ans.assign(index=range(1, len(ans) + 1))
    ans = ans.set_index("index")
    ans.to_csv(os.environ["TENNIS_HOME"] + "//players//" + style + ".yaml")


def update_player_rankings(last_year):
    senior_rankings = {}
    doubles_rankings = {}
    junior_rankings = {}
    wimbledon_rankings = {}
    with open(os.environ["TENNIS_HOME"] + "//competitions//competition_config//mandatoryCompetitions.yaml", "r") as fi:
        mandatory_competitions = yaml.safe_load(fi)
    for file in os.listdir(os.environ["TENNIS_HOME"] + "//players//players"):
        with open(os.environ["TENNIS_HOME"] + "//players//players//" + file, "r") as player_file:
            player = yaml.safe_load(player_file)
        mandatory = player["mandatory"]
        competitions_all = player["tournaments"]
        competitions = {competition: competitions_all[competition] for competition in competitions_all
                        if competitions_all[competition]["name"] != "World Tour Finals"}
        junior = get_ranking_points("junior", 6, 1000, competitions, last_year)
        junior_doubles = get_ranking_points("junior doubles", 6, 1000, competitions, last_year)
        doubles = get_ranking_points("junior doubles", 14, 1000, competitions, last_year)
        if junior is not None:
            junior = {"points": junior["points"] + junior_doubles["points"] / 4.0,
                      "tie breakers": junior["tie breakers"]}
        if not mandatory:
            senior = get_ranking_points("singles", 18, 1000, competitions, last_year)
            senior_tie_breaks = get_ranking_points("singles", 18, 1000, competitions_all, last_year)
            senior = {"points": senior["points"], "tie breakers": senior_tie_breaks["tie breakers"]}
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
            other_comps = {week: competitions_all[week] for week in competitions_all
                           if competitions_all[week]["name"] not in mandatory_competitions}
            other_comps = get_ranking_points("singles", 4, 0, other_comps, last_year)["tie breakers"]
            del other_comps["random 1"]
            del other_comps["random 2"]
            del other_comps["ATP Score"]
            list_comps = [other_comps[tier]["name"] for tier in other_comps]
            main_comps = {week: competitions_all[week] for week in competitions
                          if competitions[week]["name"] in mandatory_competitions + list_comps}
            senior_tie_breaks = get_ranking_points("singles", 18, 1000, main_comps, last_year)
            senior = {"points": senior["points"], "tie breakers": senior_tie_breaks["tie breakers"]}
        competitions = {date_comp: competitions[date_comp] for date_comp in competitions
                        if competitions[date_comp]["court"] == "grass"}
        wimbledon_two_year = get_ranking_points("singles", 9999, 1000, competitions,
                                                last_year - datetime.timedelta(days=365))
        wimbledon_one_year = get_ranking_points("singles", 9999, 1000, competitions,
                                                last_year)
        wimbledon = {"points": senior["points"] + 0.75 * wimbledon_two_year["points"] +
                     0.25 * wimbledon_one_year["points"], "tie breakers": wimbledon_two_year["tie breakers"]}
        player["ranking points"] = {"senior": senior, "doubles": doubles, "junior": junior, "wimbledon": wimbledon}
        finals = {competition_name: competitions[competition_name] for competition_name in competitions
                  if competitions[competition_name]["name"] == "World Tour Finals"}
        if finals != {}:
            senior["points"] += finals["World Tour Finals"]["score"]
        with open(os.environ["TENNIS_HOME"] + "//players//players//" + file, "w") as player_file:
            yaml.safe_dump(player, player_file)

        senior_rankings.update({player["id"]: rankings_construction(senior, player)})
        wimbledon_rankings.update({player["id"]: rankings_construction(wimbledon, player)})
        junior_rankings.update({player["id"]: rankings_construction(junior, player)})
        doubles_rankings.update({player["id"]: rankings_construction(doubles, player)})
        senior_rankings[player["id"]]["Levels"] = len(senior_rankings[player["id"]]) - 5
        wimbledon_rankings[player["id"]]["Levels"] = len(wimbledon_rankings[player["id"]]) - 5
        junior_rankings[player["id"]]["Levels"] = len(junior_rankings[player["id"]]) - 5
        doubles_rankings[player["id"]]["Levels"] = len(doubles_rankings[player["id"]]) - 5

    return {"senior rankings": senior_rankings, "junior rankings": junior_rankings,
            "doubles rankings": doubles_rankings, "wimbledon rankings": wimbledon_rankings}


def rankings_construction(rankings, player):
    senior_construction = {"name": player["name"], "ranking": rankings["points"]}
    tie_break_construction = {"Level " + str(level): rankings["tie breakers"][level]["score"]
                              for level in range(1, 18) if level in rankings["tie breakers"].keys()}
    tie_break_construction.update({"ATP Score": rankings["tie breakers"]["ATP Score"],
                                   "random 1": rankings["tie breakers"]["random 1"],
                                   "random 2": rankings["tie breakers"]["random 2"], "id": player["id"]})
    senior_construction.update(tie_break_construction)
    return senior_construction


def get_ranking_points(style, number, tie_break_level, competitions, last_year):
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
