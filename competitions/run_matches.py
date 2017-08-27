import os
import datetime
import yaml
from player.player import Player
from tennis_match.match import singles_match


def run_matches(date):
    for directory in os.listdir(os.environ["TENNIS_HOME"] + "//competitions//year " + date[:4] + "//"):
        if os.path.isdir(os.environ["TENNIS_HOME"] + "//competitions//year " + date[:4] + "//" + directory):
            for file in os.listdir(os.environ["TENNIS_HOME"] + "//competitions//year " + date[:4] + "//" + directory):
                if "ENDED" not in file and \
                  datetime.datetime.strptime(date, "%Y-%m-%d") >= datetime.datetime.strptime(file[:10], "%Y-%m-%d"):
                    pass


def run_match_competition(date, competition):
    player_dict = {}
    match_details = []
    # Need competition file
    for match in os.listdir(os.environ["TENNIS_HOME"] + "matches//year " + date[:4] + "//" + competition):
        if match[-10:] == date:
            with open(os.environ["TENNIS_HOME"] + "matches//year " + date[:4] + "//" + competition + "//" + match) as \
              file:
                match_details.append(yaml.safe_load(file))
                for player in match_details[len(match_details) - 1]["player_ids"]:
                    player_dict.update({player: Player(file=os.environ["TENNIS_HOME"] + "//players//players/Player_" +
                                              player + ".yaml")})
    # TODO: Create players properly
    # TODO: Or more likely fix match to simply take in players correctly
    winner_list = []
    for match in match_details:
        match_players = [player_dict[player] for player in match_details[len(match_details) - 1]["player_ids"]]
        winner = \
            singles_match(match_players, max_sets=match["sets"],
                          tie_break_last_set=match_details[match]["tie breaks"][len(match_details[match]["tie breaks"])
                                                                                - 1])["winner"]
        winner_list.append(match_details[match]["rank numbers"][winner])
    # ok I have the winner [as say winner, now what.  Add number to the line (correct order)
    # put stuff back into competition file
