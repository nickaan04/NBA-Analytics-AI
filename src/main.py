from model.parlay_evaluator import ParlayEvaluator
from model.model_registry import ModelRegistry
from data.player_dataset import PlayerDataset
from api.model import PropStat
from autogluon.tabular import TabularPredictor


HALIBURTON_ID = "halibty01"
haliburton_dataset = PlayerDataset(HALIBURTON_ID)
evaluator = ParlayEvaluator()


#print(brunson_dataset.get_season(2024))l
# evaluator.train_player_prop_model(BRUNSON_ID, "pts", brunson_dataset.get_playoffs())

# OLD
# LEGACY predictor = TabularPredictor.load("/Users/star/Library/CSC/CSC480/NBA-Analytics-AI/AutogluonModels/ag-20250516_231857")
# Brunson2024, PTS predictor = TabularPredictor.load("/Users/star/Library/CSC/CSC480/NBA-Analytics-AI/AutogluonModels/ag-20250516_234048")
# print("leaderboard", predictor.leaderboard())
# print(predictor.predict(brunson_dataset.get_playoffs()))

# print(brunson_dataset.get_playoffs(2024).info())

# evaluator.train_player_prop_model(BRUNSON_ID, "pts", brunson_dataset.get_regular())


# evaluator.train_player_prop_model(HALIBURTON_ID, "pts", haliburton_dataset.get_stats())
predictionRow = haliburton_dataset.get_playoffs_avg(10)
print(evaluator.predict(HALIBURTON_ID, "pts", predictionRow))
# print(predictionRow)