import csv


class Team:

    def __init__(self, i, name):
        self.i = i
        self.name = name

        self.slots = {}

    @staticmethod
    def from_csv(i, c):
        return Team(
            i=i,
            name=c["name"]
        )

    @staticmethod
    def load_teams_csv(filename):
        with open(filename) as file:
            reader = csv.DictReader(file)

            return [Team.from_csv(i, team_c) for i, team_c in enumerate(reader)]

    @staticmethod
    def dump_teams_csv(blocks, teams, filename):
        with open(filename, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["team"] + list(blocks.keys()))
            writer.writeheader()

            for team in teams:
                d = {"team": team.name}
                d.update({name: "{} ({})".format(slot.start_time, slot.column) for name, slot in team.slots.items()})
                writer.writerow(d)