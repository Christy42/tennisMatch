import os
import yaml

from competitions import run_competition


class Competition:
    def __init__(self, identity, file=None, stats=None, config_file=None):
        if file:
            with open(file, "r") as comp_file:
                stats = yaml.safe_load(comp_file)
        elif config_file:
            with open(config_file, "r") as comp_file:
                stats = yaml.safe_load(comp_file)
        self._attributes = stats
        self._identity = identity
        self._surface = stats.get("surface", "")
        self._numbers = stats.get("numbers", 0)
        self._qualifying_file = ""
        self._main_file = file
        self._config_file = config_file
        self._qualifying_number = stats.get("qualifying number", 0)
        self._qualifying_rounds = stats.get("qualifying rounds", 0)
        self._qualifying_seeds = stats.get("qualifying seeds", 0)
        self._days = stats.get("days", "")
        self._sign_ups = stats.get("sign ups", dict())
        self._ranking_points = stats.get("ranking points", dict())
        round_number = 1
        self._rounds = dict()
        while "round " + str(round_number) in stats:
            self._rounds.update({round_number: stats["round " + str(round_number)]})
        self._seeded = stats.get("seeded", 0)
        self._sets = stats.get("sets", 1)
        self._tie_breaks = stats.get("tie breaks", ["true"])

    def create_files_from_config(self, start_date):
        if not os.path.isdir(os.environ["TENNIS_HOME"] + "//competitions//year " + start_date[:4] + "//senior"):
            os.mkdir(os.environ["TENNIS_HOME"] + "//competitions//year " + start_date[:4] + "//senior")
        schedule = run_competition.create_schedule(self._numbers, self._seeded, start_date)
        if self._qualifying_number > 0:
            qualifying_number = self._qualifying_number * 2 ** self._qualifying_rounds
            schedule_qualification = run_competition.create_schedule(qualifying_number, self._qualifying_seeds,
                                                                     start_date, weekend_qualification=True,
                                                                     qualification_rounds=self._qualifying_rounds)
            schedule_qualification.update(self._attributes)
            schedule_qualification["sets"] = 3
            schedule_qualification["tie breaks"] = [True, True, True]
            schedule_qualification["actual file"] = os.environ["TENNIS_HOME"] + "//competitions//year " + \
                start_date[:4] + "//senior//" + schedule["days"][0] + " " + self._identity.split("((")[0] + " " + \
                self._identity.split("((")[1][:2].replace("-", "") + ".yaml"
            schedule["qualification file"] = os.environ["TENNIS_HOME"] + "//competitions//year " + start_date[:4] + \
                "//senior//" + schedule_qualification["days"][0] + " " + self._identity.split("((")[0] + \
                "-qualification " + self._identity.split("((")[1][:2].replace("-", "") + ".yaml"

            with open(schedule["qualification file"], "w") as file:
                yaml.safe_dump(schedule_qualification, file)
        schedule.update(self._attributes)
        with open(os.environ["TENNIS_HOME"] + "//competitions//year " + start_date[:4] + "//senior//" +
                  schedule["days"][0] + " " + self._identity.split("((")[0] + " " +
                  self._identity.split("((")[1][:2].replace("-", "") + ".yaml", "w") as file:
            yaml.safe_dump(schedule, file)

    def create_match_files(self):
        pass
