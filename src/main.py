from model.parlay_evaluator import ParlayEvaluator
from model.model_registry import ModelRegistry
from data.player_dataset import PlayerDataset
from api.model import PropStat
from autogluon.tabular import TabularPredictor


BRUNSON_ID = "brunsja01"

brunson_dataset = PlayerDataset(BRUNSON_ID)
evaluator = ParlayEvaluator()

#print(brunson_dataset.get_season(2024))
# evaluator.train_player_prop_model(BRUNSON_ID, "pts", brunson_dataset.get_playoffs())

# OLD
# LEGACY predictor = TabularPredictor.load("/Users/star/Library/CSC/CSC480/NBA-Analytics-AI/AutogluonModels/ag-20250516_231857")
# Brunson2024, PTS predictor = TabularPredictor.load("/Users/star/Library/CSC/CSC480/NBA-Analytics-AI/AutogluonModels/ag-20250516_234048")
# print("leaderboard", predictor.leaderboard())
# print(predictor.predict(brunson_dataset.get_playoffs()))

# regular szn run, 1ra
predictor = TabularPredictor.load("/Users/star/Library/CSC/CSC480/NBA-Analytics-AI/model/brunsja01/pts1")
# print("leaderboard", predictor.leaderboard())
pts_guess = 10
prediction_row = brunson_dataset.get_playoffs_avg(10)

print(evaluator.predict(BRUNSON_ID, "pts", prediction_row))