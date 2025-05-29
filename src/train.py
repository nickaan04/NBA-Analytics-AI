from model.parlay_evaluator import ParlayEvaluator
from model.model_registry import ModelRegistry
from data.player_dataset import PlayerDataset
from api.model import PropStat
from autogluon.tabular import TabularPredictor


DORTLU_ID = "dortlu01"

dortlu_dataset = PlayerDataset(DORTLU_ID)
evaluator = ParlayEvaluator()

#print(brunson_dataset.get_season(2024))
# evaluator.train_player_prop_model(DORTLU_ID, "pts", dortlu_dataset.get_all())

# OLD
# LEGACY predictor = TabularPredictor.load("/Users/star/Library/CSC/CSC480/NBA-Analytics-AI/AutogluonModels/ag-20250516_231857")
# Brunson2024, PTS predictor = TabularPredictor.load("/Users/star/Library/CSC/CSC480/NBA-Analytics-AI/AutogluonModels/ag-20250516_234048")
# print("leaderboard", predictor.leaderboard())
# print(predictor.predict(brunson_dataset.get_playoffs()))

# # regular szn run, 1ra
# predictor = TabularPredictor.load("/Users/star/Library/CSC/CSC480/NBA-Analytics-AI/model/brunsja01/pts1")
# # print("leaderboard", predictor.leaderboard())
# pts_guess = 10
prediction_row = dortlu_dataset.get_playoffs_avg(10)
# 
print(evaluator.predict(DORTLU_ID, "pts", prediction_row))