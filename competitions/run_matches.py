import os
import datetime
import yaml
from player.player import Player


def run_matches(date):
    for directory in os.listdir(os.environ["TENNIS_HOME"] + "//competitions//year " + date[:4] + "//"):
        if os.path.isdir(os.environ["TENNIS_HOME"] + "//competitions//year " + date[:4] + "//" + directory):
            for file in os.listdir(os.environ["TENNIS_HOME"] + "//competitions//year " + date[:4] + "//" + directory):
                if "ENDED" not in file and \
                  datetime.datetime.strptime(date, "%Y-%m-%d") >= datetime.datetime.strptime(file[:10], "%Y-%m-%d"):
                    pass


def run_match_competition(date, competition):
    player_list = []
    match_details = []
    for match in os.listdir(os.environ["TENNIS_HOME"] + "matches//year " + date[:4] + "//" + competition):
        if match[-10:] == date:
            with open(os.environ["TENNIS_HOME"] + "matches//year " + date[:4] + "//" + competition + "//" + match) as \
              file:
                match_details.append(yaml.safe_load(file))
                for player in match_details[len(match_details) - 1]["player_ids"]:
                    player_list.append(Player(file=os.environ["TENNIS_HOME"] + "//players//players/Player_" +
                                              player + ".yaml"))



            pass
    pass
