import json

from frc449server.dataconstants import TBA_SAVE_FILE
from frc449server.tba.tba import Event


class TBASaver:
    def __init__(self, event_id):
        try:
            self.data = json.load(open(TBA_SAVE_FILE))
        except FileNotFoundError:
            self.data = {"teams": [], "schedule": {}}
        self.event = Event(event_id)

    def update(self):
        self.data = {
            "teams": self.event.get_team_list(),
            "schedule": self.event.get_full_schedule(),
        }
        self.save()

    def save(self):
        with open(TBA_SAVE_FILE, "w") as f:
            json.dump(self.data, f)

    def team_list(self):
        return self.data["teams"]

    def match_schedule(self):
        return self.data["schedule"]

    def schedule_for_team(self, team):
        return [
            m
            for m in self.all_matches()
            if team
            in self.data["schedule"][m]["red"] + self.data["schedule"][m]["blue"]
        ]

    def teams_in_match(self, match):
        return self.data["schedule"][str(match)]

    def all_matches(self):
        return self.data["schedule"].keys()
