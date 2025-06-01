import os
from model.parlay_evaluator import ParlayEvaluator
from data.player_dataset import PlayerDataset
from api.model import PropStat
from data.download import get_player_ids_from_rosters
import os

evaluator = ParlayEvaluator()

props = PropStat._member_names_ # get list of all prop values from our enum in api/model.py

def train_player_props(player_id: str):
    for prop in props:
        if os.path.exists(f"./model/{player_id}/{prop}"):
            print(f"{player_id}/{prop} model already trained. Continuing")
            continue
        player_data = PlayerDataset(player_id)
        evaluator.train_player_prop_model(player_id, prop, player_data.get_stats())

def train_all():
    player_ids = get_player_ids_from_rosters()

    for player_id in player_ids:
        train_player_props(player_id)

train_player_props("halibty01")