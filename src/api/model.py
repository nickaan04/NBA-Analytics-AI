from pydantic import BaseModel
from enum import Enum
from typing import List, Literal

# TODO gather all player names from our team rosters, populate list
players = ["Jalen Brunson"]

Player = Enum('Player', {name.replace(' ', '_'): name for name in players}, type=str)

class PropStat(str, Enum):
    pts = "pts"
    reb = "reb"
    ast = "ast"
    stl = "stl"
    blk = "blk"
    to = "to"
    fg3 = "3pt"
    fg = "fg"
    ft = "ft"

class ParlayLeg(BaseModel):
    player: Player
    opponent: str
    prop: PropStat
    value: float
    overUnder: Literal["over", "under"]

class ParlayLegProbability(ParlayLeg):
    probability: float
    
class PostParlayRequest(BaseModel):
    parlayLegs: List[ParlayLeg]

class PostParlayResponse(BaseModel):
    parlayLegProbabilities: List[ParlayLegProbability]
    overallProbability: float
