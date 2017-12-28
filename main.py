import os

from block import Block
from schedule import Schedule
from team import Team


blocks = Block.load_blocks_json("blocks.json")
teams = Team.load_teams_csv("teams.csv")

schedule = Schedule(blocks, teams)

if schedule.solve():
    print("Solved")

    os.makedirs("out", exist_ok=True)
    Block.dump_blocks_csv(blocks, "out")
    Team.dump_teams_csv(blocks, teams, "out/teams.csv")
else:
    print("Unsolvable")
