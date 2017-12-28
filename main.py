import block
from pprint import pprint
from z3 import *
import itertools
import csv
import os
from collections import defaultdict

blocks = block.load_blocks("blocks.json")
teams = 12

for _, block in blocks.items():
    block.init_teams(teams)


s = Solver()
for _, block in blocks.items():
    block.constraints(s)

for block1, block2 in itertools.combinations(blocks.values(), 2):
    for slot1 in block1.slots:
        for slot2 in block2.slots:
            if slot1.conflicts(slot2):
                s.add(slot1.team_var != slot2.team_var)

print(s.check())
m = s.model()
pprint(m)

for _, block in blocks.items():
    block.print_debug(m)

os.makedirs("out", exist_ok=True)

def dump_csv_block(block, m):
    with open("out/{}.csv".format(block.name), "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["start_time"] + [str(column) for column in range(block.columns)])

        for row in block.grid_slots:
            writer.writerow([row[0].start_time] + [str(m[slot.team_var]) for slot in row])

def dump_csv_teams(blocks, m):
    team_slots = defaultdict(dict)

    for name, block in blocks.items():
        for slot in block.slots:
            team_slots[m[slot.team_var]][name] = slot

    with open("out/teams.csv", "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["team"] + list(blocks.keys()))
        writer.writeheader()

        for team, slots in team_slots.items():
            d = {"team": team}
            d.update({name: slot.start_time for name, slot in slots.items()})
            writer.writerow(d)


for block in blocks.values():
    dump_csv_block(block, m)

dump_csv_teams(blocks, m)