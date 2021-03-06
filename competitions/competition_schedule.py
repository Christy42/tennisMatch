import os
import yaml
from competitions import run_competition


def find_competitions_for_week():
    pass


def find_rankings(sign_ups):
    with open(os.environ["TENNIS_HOME"] + "//players//competition_configs//player_rankings.yaml", "r") as config:
        ranks = yaml.safe_load(config)
    new_ranks = {rank: ranks[rank] for rank in ranks if ranks[rank][0] in sign_ups.keys()}
    return new_ranks


def start_competition(competition_name, year):
    with open(os.environ["TENNIS_HOME"] + "//competitions//competition_configs//" + competition_name + ".yaml", "r") as\
            config:
        comp_config = yaml.safe_load(config)
    with open(os.environ["TENNIS_HOME"] + "//competitions//" + year + "//" + competition_name + ".yaml", "r") as\
            config:
        comp_details = yaml.safe_load(config)
    get_ranks = find_rankings(comp_details["sign ups"])


def sign_up_for_competition(player_id, player_name, player_junior, player_rank, competition_folder, competition_name):
    with open(competition_folder + "//" + competition_name, "r") as competition_file:
        competition = yaml.safe_load(competition_file)
    if "age" in competition["ranking restrictions"].keys() and not player_junior:
        if competition["ranking restrictions"] == ["less than", 18]:
            return False
    if "rank" in competition["ranking restrictions"].keys():
        if int(competition["ranking restrictions"]["rank"][1]) >= player_rank:
            return False
    competition["sign ups"].update({player_id: player_name})
    with open(competition_folder + "//" + competition_name, "w") as \
            competition_file:
        yaml.safe_dump(competition, competition_file)
    return True


def run_relevant_rounds():
    pass
