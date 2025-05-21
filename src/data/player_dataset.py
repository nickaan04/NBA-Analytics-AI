import pandas as pd

seasons = [2021, 2022, 2023, 2024, 2025]

"""
Creates a dictionary of dataframes for each year's regular / postseason
"""
class PlayerDataset:
    def __init__(self, player_id):
        self.regular = pd.read_csv(f"./src/data/csv/players/{player_id}-regular.csv")
        self.playoffs = pd.read_csv(f"./src/data/csv/players/{player_id}-playoffs.csv")

    def get_regular(self):
        return self.regular

    def get_playoffs(self):
        return self.playoffs


    def get_playoffs_avg(self, n):
        """
        Get average of n most recent playoffs game stats
        
        Args:
            year: season
            n: numGames
        """
        return self.playoffs.iloc[-n:, 2:].mean().to_frame().T # 3: ignores first 3 columns since they are non-numeric (date)
