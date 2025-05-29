# from model.parlay_evaluator import ParlayEvaluator
# from model.model_registry import ModelRegistry
# from data.player_dataset import PlayerDataset
# from api.model import PropStat
# from autogluon.tabular import TabularPredictor


# BRUNSON_ID = "brunsja01"

# brunson_dataset = PlayerDataset(BRUNSON_ID)
# evaluator = ParlayEvaluator()

# #print(brunson_dataset.get_season(2024))
# # evaluator.train_player_prop_model(BRUNSON_ID, "pts", brunson_dataset.get_playoffs())

# # OLD
# # LEGACY predictor = TabularPredictor.load("/Users/star/Library/CSC/CSC480/NBA-Analytics-AI/AutogluonModels/ag-20250516_231857")
# # Brunson2024, PTS predictor = TabularPredictor.load("/Users/star/Library/CSC/CSC480/NBA-Analytics-AI/AutogluonModels/ag-20250516_234048")
# # print("leaderboard", predictor.leaderboard())
# # print(predictor.predict(brunson_dataset.get_playoffs()))

# # regular szn run, 1ra
# predictor = TabularPredictor.load("/Users/star/Library/CSC/CSC480/NBA-Analytics-AI/model/brunsja01/pts1")
# # print("leaderboard", predictor.leaderboard())
# pts_guess = 10
# prediction_row = brunson_dataset.get_playoffs_avg(10)

# print(evaluator.predict(BRUNSON_ID, "pts1", prediction_row))

from model.parlay_evaluator import ParlayEvaluator
from model.model_registry import ModelRegistry
from data.player_dataset import PlayerDataset
from api.model import PropStat
from autogluon.tabular import TabularPredictor
import numpy as np
import pandas as pd

# Import the quantile converter (save the previous code as quantile_converter.py)
from quantile_converter import QuantileToHitProbability

BRUNSON_ID = "brunsja01"

brunson_dataset = PlayerDataset(BRUNSON_ID)
evaluator = ParlayEvaluator()

# Load your trained model
predictor = TabularPredictor.load("/Users/star/Library/CSC/CSC480/NBA-Analytics-AI/model/brunsja01/pts1")

# Get prediction data
pts_guess = 10
prediction_row = brunson_dataset.get_playoffs_avg(10)

# Get quantile predictions (your existing code)
print("Input features:")
print(prediction_row)

# Get the quantile predictions
quantile_predictions = evaluator.predict(BRUNSON_ID, "pts1", prediction_row)
print("\nQuantile Predictions:")
print(quantile_predictions)

# NEW: Convert to hit probabilities
print("\n" + "="*50)
print("HIT PROBABILITY ANALYSIS")
print("="*50)

# Initialize the converter
converter = QuantileToHitProbability()

# Extract the quantile values (assuming they're in the first row)
if isinstance(quantile_predictions, pd.DataFrame):
    quantile_values = quantile_predictions.iloc[0].values.tolist()
else:
    quantile_values = quantile_predictions

print(f"Extracted quantile values: {quantile_values}")

# Analyze specific prop lines
prop_lines = [27.5, 28.0, 28.5, 29.0, 29.5, 30.0, 30.5]

print(f"\nBrunson Points - Hit Probability Analysis:")
print("-" * 40)

for prop_line in prop_lines:
    result = converter.quantiles_to_hit_probability(quantile_values, prop_line)
    
    print(f"Prop Line: {prop_line} points")
    print(f"  OVER {prop_line}: {result['over_probability']:.3f} ({result['over_probability']*100:.1f}%)")
    print(f"  UNDER {prop_line}: {result['under_probability']:.3f} ({result['under_probability']*100:.1f}%)")
    
    # Add betting recommendation (simple example)
    if result['over_probability'] > 0.6:
        print(f"  💡 RECOMMENDATION: Strong OVER bet")
    elif result['over_probability'] < 0.4:
        print(f"  💡 RECOMMENDATION: Strong UNDER bet")
    else:
        print(f"  💡 RECOMMENDATION: Neutral/Pass")
    print()

# Find optimal prop lines
print("OPTIMAL PROP LINES:")
print("-" * 20)

# Find line for 60% over probability
line_60_over = converter.find_threshold_for_probability(quantile_values, 0.6, 'over')
print(f"60% chance of going OVER: {line_60_over:.1f} points")

# Find line for 70% over probability  
line_70_over = converter.find_threshold_for_probability(quantile_values, 0.7, 'over')
print(f"70% chance of going OVER: {line_70_over:.1f} points")

# Find median (50th percentile)
median = converter.find_threshold_for_probability(quantile_values, 0.5, 'over')
print(f"Median prediction (50/50 line): {median:.1f} points")

# Summary statistics
print(f"\nSUMMARY STATISTICS:")
print("-" * 18)
print(f"10th percentile: {quantile_values[0]:.1f}")
print(f"25th percentile: {np.interp(0.25, [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9], quantile_values):.1f}")
print(f"50th percentile: {quantile_values[4]:.1f}")  # 0.5 quantile
print(f"75th percentile: {np.interp(0.75, [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9], quantile_values):.1f}")
print(f"90th percentile: {quantile_values[8]:.1f}")

# Range analysis
range_10_90 = quantile_values[8] - quantile_values[0]
print(f"10th-90th percentile range: {range_10_90:.1f} points")

if range_10_90 < 4:
    print("📊 VARIANCE: Low variance prediction (tight distribution)")
elif range_10_90 > 8:
    print("📊 VARIANCE: High variance prediction (wide distribution)")
else:
    print("📊 VARIANCE: Moderate variance prediction")