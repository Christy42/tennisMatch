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
                    print("X")
                    run_match_competition(date, file, directory)


def run_match_competition(date, competition, directory):
    player_dict = {}
    match_details = []
    with open(os.environ["TENNIS_HOME"] + "//competitions//year " + date[:4] + "//" + directory + "//" + competition,
              "r") as comp_file:
        competition_stuff = yaml.safe_load(comp_file)
    print(competition_stuff)
    for match in os.listdir(os.environ["TENNIS_HOME"] + "//matches//year " + date[:4] + "//" + competition):
        print(match[-15:-5])
        if match[-15:-5] == date:
            with open(os.environ["TENNIS_HOME"] + "//matches//year " + date[:4] + "//" + competition + "//" + match) as\
              file:
                match_details.append(yaml.safe_load(file))
            print("CCCC")
            for player in match_details[len(match_details) - 1]["player_ids"]:
                player_dict.update({player: Player(file=os.environ["TENNIS_HOME"] + "//players//players/Player_" +
                                    player + ".yaml").create_game_dict()})
    winner_list = []
    print(match_details)
    print("BBB")
    for match in match_details:
        match_players = [player_dict[player] for player in match_details[len(match_details) - 1]["player_ids"]]
        print(match_details)
        winner = singles_match(match_players, max_sets=match["sets"],
                               tie_break_last_set=match["tie breaks"]
                               [len(match["tie breaks"]) - 1])["winner"]
        print(winner)
        print("B")
        winner_list.append(match["rank numbers"][winner])
    print(competition_stuff["days"])
    roun = competition_stuff["days"].index(date) + 1
    next_round = [seed for seed in competition_stuff["round " + str(roun)] if seed in winner_list]
    competition_stuff.update({"round " + str(roun + 1): next_round})
    print(next_round)
    print(winner_list)
    with open(os.environ["TENNIS_HOME"] + "//competitions//year " + date[:4] + "//" + directory + "//" + competition,
              "w") as comp_file:
        yaml.safe_dump(competition_stuff, comp_file)
    print(winner_list)
    print("c")


run_matches("2000-01-06")
# OK How to reset?
#it's not to feel like I'm just giving up
# on?
# college#
# sweetie you have a degree (And you can go back after the break)I GUESS I kinda feel like if I take a break maybe it will be really hard to go back and I just won't end up doing  it and then I will ahve wasted however long it takes me t come to that decision as well as all the time I've been doing it
#And yes I have a degree but I would be giving up ine the one I'm pursuing at the mment
# Maybe if it is too hard to go back not going back is a good idea.  Also the time was spent figuring stuff out.  Sometimes it has to be done
# Maybe the one you are pursuing is a bad idea (maybe) at which point it is just making a good decision and not going for the sunk cost fallacy

#I get stressed wondering wat it would have been like to try do this without the accompnaying massive depression
#Like I've been cheated out of giving it a better go because I feel like even when I'm better this is gonna colour it,
#Like at the moment the whole thing is just such a negative for me it's really hard to imagine being in a place where I could go back into it with an open mind
#And then I worry that what if I always would have been rubbish at it and the depression is just a convenient shield (or the fact that Im rubbish caused the depression)

# You were not in long enough to find out if you were rubbish at it.
# Yeah it sucks that you were not able to give it a good go to the best of your ability.  It just sucks and is what it is
# I can see it being tough for this not to colour your experience of it.  All you can do is try and have an open mind if you do decide to go back
