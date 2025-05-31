from typing import Dict, Tuple, List
from autogluon.tabular import TabularPredictor
import pandas as pd

from model.quantile_converter import QuantileConverter

from data.player_dataset import PlayerDataset
from data.download import generate_player_id

from api.model import players as player_list
from api.model import ParlayLeg
from api.model import ParlayLegProbability
from api.model import PropStat

QUANTILE_LEVELS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

class ParlayEvaluator:
    def __init__(self):
        self.quantile_converter = QuantileConverter(quantile_levels=QUANTILE_LEVELS)

        player_ids = [generate_player_id(player) for player in player_list]
        self.player_datasets = {player_id: PlayerDataset(player_id) for player_id in player_ids}
        
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
            quantile_levels=QUANTILE_LEVELS,
            sample_weight="is_playoff"
        )
        
        # Train model
        predictor.fit(
            train_data=historical_data,
            presets='best_quality',
            time_limit=300 # 5 min
        )

    def predict(self, player_id: str, prop: PropStat, row: pd.DataFrame) -> List[float]:
        predictor = TabularPredictor.load(f"./model/{player_id}/{prop}")

        return predictor.predict(row).iloc[0].values.tolist()

    def evaluate_leg(self, parlay_leg: ParlayLeg):
        player_id = generate_player_id(parlay_leg.player)
        
        prediction_row = self.player_datasets[player_id].get_playoffs_avg(10)
        quantile_values = self.predict(player_id, parlay_leg.prop.lower(), prediction_row)
        result = self.quantile_converter.quantiles_to_hit_probability(quantile_values, float(parlay_leg.value))

        return ParlayLegProbability(
            **parlay_leg.model_dump(),
            probability=result[parlay_leg.overUnder]
        )
