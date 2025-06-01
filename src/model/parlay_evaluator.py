from typing import Dict, Tuple, List
from autogluon.tabular import TabularPredictor
import pandas as pd
import numpy as np

from model.quantile_converter import QuantileConverter

from data.player_dataset import PlayerDataset
from data.download import generate_player_id

from api.model import players as player_list
from api.model import ParlayLeg
from api.model import ParlayLegProbability
from api.model import PropStat

QUANTILE_LEVELS = [0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99]

def add_noise(df, std=0.8):
    ignore = {"player_game_num_career", "date", "is_playoff"}
    noisy_df = df.copy()

    # ignore gamenum, date, weight
    stat_cols = [col for col in df.select_dtypes(include='number').columns if col not in ignore]
    for col in stat_cols:
        noisy_df[col] += np.random.normal(0, std, size=len(df))
    return noisy_df

def inflate_quantiles(quantiles, inflation=1.3):
    mid = np.mean(quantiles)
    return [mid + (q - mid) * inflation for q in quantiles]


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

        noisy_data = add_noise(historical_data)
        
        # initialize predictor with quantile regression levels 
        predictor = TabularPredictor(
            path=f"model/{player_id}/{prop}/",
            label=label,
            problem_type='quantile', 
            quantile_levels=QUANTILE_LEVELS,
            sample_weight="is_playoff",
            eval_metric="pinball_loss"
        )
        
        # Train model
        predictor.fit(
            train_data=noisy_data,
            presets='medium_quality',
            time_limit=300,
            num_bag_folds=5,
            num_stack_levels=1,
            verbosity=2
        )

    def predict(self, player_id: str, prop: PropStat, row: pd.DataFrame) -> List[float]:
        predictor = TabularPredictor.load(f"./model/{player_id}/{prop}")

        return predictor.predict(row).iloc[0].values.tolist()

    def evaluate_leg(self, parlayLeg: ParlayLeg):
        player_id = generate_player_id(parlayLeg.player)
        prediction_row = self.player_datasets[player_id].get_playoffs_avg(10)

        quantile_values = self.predict(player_id, parlayLeg.prop.lower(), prediction_row)
        print(f"quantile values\n{quantile_values}")

        # Inflate the predicted quantiles to increase spread
        inflated = inflate_quantiles(quantile_values, inflation=1.3)
        print(f"inflated quantiles\n{inflated}")

        result = self.quantile_converter.quantiles_to_hit_probability(inflated, float(parlayLeg.value))

        return ParlayLegProbability(
            **parlayLeg.model_dump(),
            probability=result[parlayLeg.overUnder]
        )
