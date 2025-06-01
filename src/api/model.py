from pydantic import BaseModel
from enum import Enum
from typing import List, Literal

players = ["Pascal Siakam", "Tyrese Haliburton", "Myles Turner", "Andrew Nembhard", "Aaron Nesmith", "Shai Gilgeous-Alexander", "Luguentz Dort", "Jalen Williams", "Isaiah Hartenstein", "Chet Holmgren"]

Player = Enum('Player', {name.replace(' ', '_'): name for name in players}, type=str)

class PropStat(str, Enum):
    pts = "pts"
    reb = "reb"
    ast = "ast"
    stl = "stl"
    blk = "blk"
    tov = "tov"
    fg3 = "fg3"
    fg = "fg"
    ft = "ft"

class ParlayLeg(BaseModel):
    player: Player
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
