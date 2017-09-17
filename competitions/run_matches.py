import os
import datetime
import yaml
from player.player import Player
from tennis_match.match import Match


def run_matches(date):
    for directory in os.listdir(os.environ["TENNIS_HOME"] + "//competitions//year " + date[:4] + "//"):
        if os.path.isdir(os.environ["TENNIS_HOME"] + "//competitions//year " + date[:4] + "//" + directory):
            for file in os.listdir(os.environ["TENNIS_HOME"] + "//competitions//year " + date[:4] + "//" + directory):
                if "ENDED" not in file and \
                   datetime.datetime.strptime(date, "%Y-%m-%d") >= datetime.datetime.strptime(file[:10], "%Y-%m-%d"):
                    run_match_competition(date, file, directory)


def run_match_competition(date, competition, directory):
    print("C")
    print(os.environ["TENNIS_HOME"] + "//matches//year " + date[:4] + "//" + competition)
    if not os.path.isdir(os.environ["TENNIS_HOME"] + "//matches//year " + date[:4] + "//" + competition):
        return 0
    print("D")
    player_dict = {}
    match_details = []
    with open(os.environ["TENNIS_HOME"] + "//competitions//year " + date[:4] + "//" + directory + "//" + competition,
              "r") as comp_file:
        competition_stuff = yaml.safe_load(comp_file)
    print("b")
    for match in os.listdir(os.environ["TENNIS_HOME"] + "//matches//year " + date[:4] + "//" + competition):
        if match[-15:-5] == date:
            with open(os.environ["TENNIS_HOME"] + "//matches//year " + date[:4] + "//" + competition + "//" + match) as\
              file:
                stuff = yaml.safe_load(file)
                stuff["commentary file"] = os.environ["TENNIS_HOME"] + "//matches//year " + date[:4] + "//" + \
                    competition + "//" + match.replace(".yaml", "-commentary.txt")
                match_details.append(stuff)
            for player in match_details[len(match_details) - 1]["player_ids"]:
                player_dict.update({player: Player(file=os.environ["TENNIS_HOME"] + "//players//players/Player_" +
                                    player + ".yaml").create_game_dict()})
    print("X")
    for i in range(len(match_details)):
        print(match_details[i]["player_ids"])

    winner_list = []
    for match in match_details:
        deuce = match["deuce"] if "deuce" in match else True
        let = match["let"] if "let" in match else True
        games_required = match["games required"] if "games required" in match else 6
        match_players = [player_dict[player] for player in match["player_ids"]]
        print(match_players[0]["name"])
        print(match_players[1]["name"])
        print(match_players[0]["id"])
        print(match_players[1]["id"])
        match_class = Match(max_sets=match["sets"], players=match_players, tie_breaks=match["tie breaks"],
                            comm_file=match["commentary file"], games_required=games_required, deuce=deuce, let=let)
        game = match_class.singles_match()
        winner = game["winner"]
        stats = game["statistics"]
        for i in range(len(match["player_ids"])):
            Player(file=os.environ["TENNIS_HOME"] + "//players//players/Player_" + match["player_ids"][i] + ".yaml").\
                update_player_stats(stats[i], competition, date[:4])
        winner_list.append(match["rank numbers"][winner])
    roun = competition_stuff["days"].index(date) + 1
    next_round = [seed for seed in competition_stuff["round " + str(roun)] if seed in winner_list]
    competition_stuff.update({"round " + str(roun + 1): next_round})

    with open(os.environ["TENNIS_HOME"] + "//competitions//year " + date[:4] + "//" + directory + "//" + competition,
              "w") as comp_file:
        yaml.safe_dump(competition_stuff, comp_file)


run_matches("2000-01-06")
# OK How to reset?
