from model.parlay_evaluator import ParlayEvaluator
from model.model_registry import ModelRegistry
from data.player_dataset import PlayerDataset
from api.model import PropStat

BRUNSON_ID = "brunsja01"

brunson_dataset = PlayerDataset(BRUNSON_ID)
evaluator = ParlayEvaluator()

print(brunson_dataset.get_season(2024))

evaluator.train_player_prop_model(BRUNSON_ID, "blk", brunson_dataset.get_season(2024))

