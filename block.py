import math
import isodate
import json
from z3 import *

class Block:

    def __init__(self, name, columns, start_time, setup_time, row_time, cleanup_time):
        self.name = name
        self.columns = columns
        self.start_time = start_time
        self.setup_time = setup_time
        self.row_time = row_time
        self.cleanup_time = cleanup_time

        self.teams = None
        self.rows = None
        self.slots = None

    def init_teams(self, teams):
        self.teams = teams
        self.rows = math.ceil(teams / self.columns)
        self.grid_slots = [[Slot(self, row, column) for column in range(self.columns)] for row in range(self.rows)]
        self.slots = [slot for row in self.grid_slots for slot in row]

    @staticmethod
    def from_json(name, j):
        return Block(
            name=name,
            columns=j["columns"],
            start_time=isodate.parse_datetime(j["start_time"]),
            setup_time=isodate.parse_duration(j["setup_time"]),
            row_time=isodate.parse_duration(j["row_time"]),
            cleanup_time=isodate.parse_duration(j["cleanup_time"]),
        )

    def constraints(self, s):
        team_vars = [slot.team_var for slot in self.slots]
        for team_var in team_vars:
            s.add(And(0 <= team_var, team_var < self.teams))

        s.add(Distinct(*team_vars))

    def print_debug(self, m):
        print(self.name)
        for row in self.grid_slots:
            for slot in row:
                print(m[slot.team_var], end="\t")
            print()
        print()

class Slot:

    def __init__(self, block, row, column):
        self.block = block
        self.row = row
        self.column = column

        self.team_var = Int("{}_{}_{}".format(block.name, row, column).encode("utf-8"))

    @property
    def start_time(self):
        return self.block.start_time + self.slot_time * self.row

    @property
    def slot_time(self):
        return self.block.row_time + self.block.cleanup_time

    @property
    def end_time(self):
        return self.start_time + self.slot_time

    def during(self, t):
        return self.start_time - self.block.setup_time <= t < self.start_time + self.block.row_time

    def conflicts(self, other):
        return self.during(other.start_time) or other.during(self.start_time)


def load_blocks(filename):
    with open(filename) as file:
        j = json.load(file)

        return {name: Block.from_json(name, block_j) for name, block_j in j.items()}
