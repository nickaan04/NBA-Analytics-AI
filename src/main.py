from model.parlay_evaluator import ParlayEvaluator
from model.model_registry import ModelRegistry
from data.player_dataset import PlayerDataset
from api.model import PropStat
from autogluon.tabular import TabularPredictor
import numpy as np
import pandas as pd

# Import the quantile converter (save the previous code as quantile_converter.py)
from quantile_converter import QuantileToHitProbability

HALIB_ID = "halibty01"

halib_dataset = PlayerDataset(HALIB_ID)
evaluator = ParlayEvaluator()

# Load your trained model
predictor = TabularPredictor.load("/Users/star/Library/CSC/CSC480/NBA-Analytics-AI/model/halibty01/pts")

# Get prediction data
pts_guess = 10
prediction_row = halib_dataset.get_playoffs_avg(10)

# Get quantile predictions (your existing code)
print("Input features:")
print(prediction_row)

# Get the quantile predictions
quantile_predictions = evaluator.predict(HALIB_ID, "pts", prediction_row)
print("\nQuantile Predictions:")
print(quantile_predictions)

# Initialize the converter
converter = QuantileToHitProbability()

# Extract the quantile values (assuming they're in the first row)
if isinstance(quantile_predictions, pd.DataFrame):
    quantile_values = quantile_predictions.iloc[0].values.tolist()
else:
    quantile_values = quantile_predictions

print(f"Extracted quantile values: {quantile_values}")

# Interactive prop line analysis
print("\n" + "="*50)
print("PROP LINE ANALYZER")
print("="*50)
print("Enter a prop line (e.g., 19.5) or 'quit' to exit")

while True:
    try:
        user_input = input("\nEnter prop line: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        # Convert input to float
        prop_line = float(user_input)
        
        # Get probabilities
        result = converter.quantiles_to_hit_probability(quantile_values, prop_line)
        
        # Print the 3 things requested
        print(f"\nProp Line: {prop_line}")
        print(f"Over Probability: {result['over_probability']:.3f} ({result['over_probability']*100:.1f}%)")
        print(f"Under Probability: {result['under_probability']:.3f} ({result['under_probability']*100:.1f}%)")
        
        # Betting suggestion
        if result['over_probability'] > 0.6:
            print(f"Betting Suggestion: BET OVER")
        elif result['over_probability'] < 0.4:
            print(f"Betting Suggestion: BET UNDER")
        else:
            print(f"Betting Suggestion: PASS")
        
    except ValueError:
        print("Invalid input. Please enter a valid number.")
    except KeyboardInterrupt:
        print("\nGoodbye!")
        break
    except Exception as e:
        print(f"Error: {e}")