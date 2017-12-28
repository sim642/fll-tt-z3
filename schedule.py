import itertools

from z3 import *


class Schedule:

    def __init__(self, blocks, teams):
        self.blocks = blocks
        self.teams = teams

        for block in blocks.values():
            block.init_teams(len(teams))

        self.m = None

    def solve(self):
        s = Solver()

        for block in self.blocks.values():
            block.constraints(s)

        self.constraints(s)

        if s.check() == sat:
            self.m = s.model()

            self.fill_blocks()
            self.fill_teams()

            return True
        else:
            return False

    def constraints(self, s):
        for block1, block2 in itertools.combinations(self.blocks.values(), 2):
            for slot1 in block1.slots:
                for slot2 in block2.slots:
                    if slot1.conflicts(slot2):
                        var1 = slot1.team_var
                        var2 = slot2.team_var
                        s.add(Implies(And(var1 >= 0, var2 >= 0), var1 != var2))

    def fill_blocks(self):
        for block in self.blocks.values():
            block.fill(self.m)

    def fill_teams(self):
        for block in self.blocks.values():
            for slot in block.slots:
                team = self.teams[self.m[slot.team_var].as_long()]

                team.slots[block.name] = slot
                slot.team = team

