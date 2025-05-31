import pandas as pd

seasons = [2021, 2022, 2023, 2024, 2025]

"""
Creates a dictionary of dataframes for each year's regular / postseason
"""
class PlayerDataset:
    def __init__(self, player_id):
        self.combined = pd.read_csv(f"./src/data/csv/players/{player_id}-combined.csv")

    def get_all(self):
        return self.combined

    def get_playoffs_avg(self, n):
        """
        Get average of n most recent playoffs game stats, excluding 'date',
        and return a single-row DataFrame including the first 2 columns (metadata).
        
        Args:
            n: Number of most recent playoff games to average
        """
        df = self.combined.iloc[-n:]

        # Extract numeric average from columns 3 onward (skip 'date')
        stats_avg = df.drop(columns=["date"]).iloc[:, 2:].mean().to_frame().T

        print(stats_avg)

        # Get first two columns from the last row
        meta_cols = df.iloc[-1, :2].to_frame().T
        meta_cols.columns = df.columns[:2]

        # Combine meta + averaged stats into one row
        return pd.concat([meta_cols.reset_index(drop=True), stats_avg.reset_index(drop=True)], axis=1)