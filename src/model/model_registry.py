import os
from autogluon.tabular import TabularPredictor

"""
Interface to store autogluon models in filesystem
"""
class ModelRegistry:
    def __init__(self, base_dir="model"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
        
    def get_model_path(self, player_id: str, prop: str) -> str:
        path = os.path.join(self.base_dir, player_id, prop)
        return path
    
    def model_exists(self, player_id: str, prop: str) -> bool:
        path = self.get_model_path(player_id, prop)
        return os.path.exists(path)
    
    def load_model(self, player_id: str, prop: str) -> TabularPredictor:
        if not self.model_exists(player_id, prop):
            raise ValueError(f"No model found for {player_id} - {prop}")
        
        path = self.get_model_path(player_id, prop)
        return TabularPredictor.load(path)
    
    def save_model(self, model: TabularPredictor, player_id: str, prop: str) -> None:
        path = self.get_model_path(player_id, prop)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        print("Saving model to dir:", path)
        model.save(path)