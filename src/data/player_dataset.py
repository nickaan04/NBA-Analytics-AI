import pandas as pd

seasons = [2021, 2022, 2023, 2024, 2025]

"""
Creates a dictionary of dataframes for each year's regular / postseason
"""
class PlayerDataset:
    def __init__(self, player_id):
        self.gamelogs = {}
        for season in seasons:
            self.gamelogs[season] = {
                "regular": pd.read_csv(f"./src/data/csv/players/{player_id}-{season}.csv"),
                "playoffs" : pd.read_csv(f"./src/data/csv/players/{player_id}-playoffs-{season}.csv")
            }

    def get_season(self, year):
        return self.gamelogs[year]["regular"]

    def get_playoffs(self, year):
        return self.gamelogs[year]["playoffs"]
