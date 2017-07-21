import yaml
import os


def update_rankings():
    rankings = {}
    for file in os.listdir("players//players"):
        with open("players//players//" + file, "r") as player_file:
            player = yaml.safe_load(player_file)
            tournaments = player["rankings"]
            name = player["name"]
        rankings.update({file[7:]: {"ranking points": sum(list(tournaments.values())), "name": name}})
    with open("players//rankings.yaml", "w") as ranking_file:
        yaml.safe_dump(rankings, ranking_file)
