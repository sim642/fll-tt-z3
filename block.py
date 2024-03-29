import csv
import json
from collections import OrderedDict

import isodate
from z3 import *


class Block:

    def __init__(self, name, columns, start_time, setup_time, row_time, cleanup_time):
        self.name = name
        self.columns = columns
        self.num_columns = len(columns)
        self.start_time = start_time
        self.setup_time = setup_time
        self.row_time = row_time
        self.cleanup_time = cleanup_time

        self.num_teams = None
        self.num_rows = None
        self.grid_slots = None
        self.slots = None

    def init_teams(self, num_teams):
        self.num_teams = num_teams
        self.num_rows = math.ceil(num_teams / self.num_columns)
        self.grid_slots = [[Slot(self, row, col) for col in range(self.num_columns)] for row in range(self.num_rows)]
        self.slots = [slot for row in self.grid_slots for slot in row]

    @staticmethod
    def from_json(name, j):
        columns = j["columns"]
        if isinstance(columns, int):
            columns = [str(i) for i in range(columns)]

        return Block(
            name=name,
            columns=columns,
            start_time=isodate.parse_datetime(j["start_time"]),
            setup_time=isodate.parse_duration(j["setup_time"]),
            row_time=isodate.parse_duration(j["row_time"]),
            cleanup_time=isodate.parse_duration(j["cleanup_time"]),
        )

    @staticmethod
    def load_blocks_json(filename):
        with open(filename) as file:
            j = json.load(file, object_pairs_hook=OrderedDict)

            return OrderedDict((name, Block.from_json(name, block_j)) for name, block_j in j.items())

    @property
    def num_fake_teams(self):
        return len(self.slots) - self.num_teams

    def constraints(self, s):
        team_vars = [slot.team_var for slot in self.slots]
        for team_var in team_vars:
            s.add(And(-self.num_fake_teams <= team_var, team_var < self.num_teams))

        s.add(Distinct(*team_vars))

    def print_debug(self, m):
        print(self.name)
        for row in self.grid_slots:
            for slot in row:
                print(m[slot.team_var], end="\t")
            print()
        print()

    def dump_csv(self, filename):
        with open(filename, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["start_time"] + self.columns)

            for row in self.grid_slots:
                writer.writerow([row[0].start_time] + [slot.team.name if slot.team else "" for slot in row])

    @staticmethod
    def dump_blocks_csv(blocks, dirname):
        for block in blocks.values():
            filename = dirname + "/" + block.name + ".csv" # TODO: path concatenation
            block.dump_csv(filename)


class Slot:

    def __init__(self, block, row, col):
        self.block = block
        self.row = row
        self.col = col

        self.team_var = Int("{}_{}_{}".format(block.name, row, col).encode("utf-8"))
        self.team = None

    @property
    def column(self):
        return self.block.columns[self.col]

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