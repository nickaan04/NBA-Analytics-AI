from typing import Dict, Tuple, List
from autogluon.tabular import TabularPredictor
import pandas as pd

from model.model_registry import ModelRegistry
from api.model import *

class ParlayEvaluator:
    def __init__(self):
        self.model_registry = ModelRegistry()
        
    def train_player_prop_model(self, player_id: str, prop: PropStat, historical_data: pd.DataFrame) -> None:
        """
        Train a model for a specific player and prop
        
        Args:
            player_id: Player id 
            prop: Property statistic (pts, reb, ast, etc.)
            historical_data: dataframe with historical performance and features
        """
        # Define features and label
        label = prop
        
        # initialize predictor with quantile regression levels 
        predictor = TabularPredictor(
            path=f"model/{player_id}/{prop}/",
            label=label,
            problem_type='quantile', 
            quantile_levels=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        )
        
        # Train model
        predictor.fit(
            train_data=historical_data,
            sample_weight=historical_data["is_playoff"].map({True:1.5,False:1.0}),
            presets='best_quality',
            time_limit=300 # 5 min
        )
        
        # Save model
        self.model_registry.save_model(predictor, player_id, prop)

    def predict(self, player_id: str, prop: PropStat, row: pd.DataFrame):
        predictor = TabularPredictor.load(f"./model/{player_id}/{prop}")

        return predictor.predict(row)