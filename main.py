import block
from pprint import pprint
from z3 import *
import itertools

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