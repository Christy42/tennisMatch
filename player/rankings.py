import yaml
import os
import datetime
import random
import pandas


# tie breaks, 1000 + events score, highest score, second highest score etc, random 1, random 2
# I need format to be competitions = {date: {event level: level, ranking points: score, event name: name, court: court}}
def update_rankings(rankings, style):
    ans = pandas.DataFrame(rankings)
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


# TODO: Add Next Gen Race, Main Race, Doubles Race, Challenger Race
def update_player_rankings(last_year):
    last_year = datetime.datetime.strptime(last_year, "%Y-%m-%d")
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
                        if competitions_all[competition]["event name"] != "World Tour Finals"}
        junior = get_ranking_points("junior", 6, 1000, competitions, last_year)
        junior_doubles = get_ranking_points("junior doubles", 6, 1000, competitions, last_year)
        doubles = get_ranking_points("doubles", 14, 1000, competitions, last_year)
        if junior is not None:
            junior = {"points": junior["points"] + junior_doubles["points"] / 4.0,
                      "tie breakers": junior["tie breakers"]}
        if not mandatory:
            senior = get_ranking_points("singles", 18, 1000, competitions, last_year)
            senior_tie_breaks = get_ranking_points("singles", 18, 1000, competitions_all, last_year)
            senior = {"points": senior["points"], "tie breakers": senior_tie_breaks["tie breakers"]}
        else:
            other_comps = {week: competitions[week] for week in competitions
                           if competitions[week]["event name"] not in mandatory_competitions}
            other_comps = get_ranking_points("singles", 4, 0, other_comps, last_year)["tie breakers"]
            del other_comps["random 1"]
            del other_comps["random 2"]
            del other_comps["ATP Score"]
            list_comps = [other_comps[tier]["event name"] for tier in other_comps]
            main_comps = {week: competitions[week] for week in competitions
                          if competitions[week]["event name"] in mandatory_competitions + list_comps}
            senior = get_ranking_points("singles", 18, 1000, main_comps, last_year)
            other_comps = {week: competitions_all[week] for week in competitions_all
                           if competitions_all[week]["event name"] not in mandatory_competitions}
            other_comps = get_ranking_points("singles", 4, 0, other_comps, last_year)["tie breakers"]
            del other_comps["random 1"]
            del other_comps["random 2"]
            del other_comps["ATP Score"]
            list_comps = [other_comps[tier]["event name"] for tier in other_comps]
            main_comps = {week: competitions_all[week] for week in competitions
                          if competitions[week]["event name"] in mandatory_competitions + list_comps}
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
                  if competitions[competition_name]["event name"] == "World Tour Finals"}
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
    update_rankings(senior_rankings, "senior")
    update_rankings(junior_rankings, "junior")
    update_rankings(doubles_rankings, "doubles")
    update_rankings(wimbledon_rankings, "wimbledon")
    return {"senior rankings": senior_rankings, "junior rankings": junior_rankings,
            "doubles rankings": doubles_rankings, "wimbledon rankings": wimbledon_rankings}


def rankings_construction(rankings, player):
    senior_construction = {"event name": player["name"], "ranking": rankings["points"]}
    tie_break_construction = {"Level " + str(level): rankings["tie breakers"][level]["ranking points"]
                              for level in range(1, 18) if level in rankings["tie breakers"].keys()}
    tie_break_construction.update({"ATP Score": rankings["tie breakers"]["ATP Score"],
                                   "random 1": rankings["tie breakers"]["random 1"],
                                   "random 2": rankings["tie breakers"]["random 2"], "id": player["id"]})
    senior_construction.update(tie_break_construction)
    return senior_construction


def get_ranking_points(style, number, tie_break_level, competitions, last_year):
    # TODO: Need to add in max tournament score, a todo later though

    main_tie_break = 0
    max_tournament_score = 0
    # Default N number of competitions to replace
    tie_breakers = {i: {"event level": style, "ranking points": 0, "event name": "default"}
                    for i in range(1, number + 1)}
    if competitions is None:
        return {"tie breakers": {"random 1": random.random(), "random 2": random.random(), "ATP Score": 0}, "points": 0}
    senior_comps = {date_comp: competitions[date_comp] for date_comp in competitions
                    if datetime.datetime.strptime(date_comp, "%Y-%m-%d") > last_year and
                    competitions[date_comp]["event level"] == style}
    if senior_comps is None:
        return {"tie breakers": {"random 1": random.random(), "random 2": random.random(), "ATP Score": 0}, "points": 0}
    # weird way to do this, redo it

    for competition in senior_comps:
        print(senior_comps[competition])
        # This tie break is how many points from 1000+ level events in total
        if senior_comps[competition].get("ATP level", 0) >= tie_break_level:
            main_tie_break += senior_comps[competition]["ranking points"]
        print(tie_breakers)
        for tier in tie_breakers:
            if tie_breakers[tier]["ranking points"] < senior_comps[competition]["ranking points"]:
                tie_breakers = {level: tie_breakers[level - 1 * (level > tier)] for level in tie_breakers}
                tie_breakers[tier] = {"ranking points": senior_comps[competition]["ranking points"],
                                      "event name": senior_comps[competition]["event name"],
                                      "level": senior_comps[competition].get("ATP level", 0)}
                break
    ranking_points = sum([tie_breakers[score]["ranking points"] for score in tie_breakers])

    tie_breakers = {element: tie_breakers[element] for element in tie_breakers
                    if tie_breakers[element]["event name"] != "default"}
    tie_breakers.update({"random 1": random.random(), "random 2": random.random(), "ATP Score": main_tie_break})
    result = {"points": ranking_points, "tie breakers": tie_breakers}
    return result


# I need format to be competitions = {date: {event level: level, ranking points: score, event name: name, court: court}}
def assign_ranking_points(ranking_points, competition_name, surface, level, competition_date, result=""):
    for player in ranking_points:
        tournament_dict = {competition_date: {"event level": level, "ranking points": ranking_points[player],
                           "event name": competition_name, "court": surface, "result": result}}
        with open(os.environ["TENNIS_HOME"] + "//players//players//Player_" + str(player) + ".yaml", "r") as player_fil:
            player_stuff = yaml.safe_load(player_fil)
        player_stuff["tournaments"].update(tournament_dict)
        with open(os.environ["TENNIS_HOME"] + "//players//players//Player_" + str(player) + ".yaml", "w") as player_fil:
            yaml.safe_dump(player_stuff, player_fil)


update_player_rankings("1999-01-01")
