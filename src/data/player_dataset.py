import pandas as pd
import os

"""
Creates a dictionary of dataframes for each year's regular / postseason
"""
class PlayerDataset:
    def __init__(self, player_id):
        # Determine the folder of THIS file (player_dataset.py)
        base_folder = os.path.dirname(__file__)  
        # Move up one level to “src/data/”
        data_folder = os.path.abspath(os.path.join(base_folder, os.pardir))  
        # Now build path to “src/data/csv/players/<player_id>-combined.csv”
        combined_csv = os.path.join(data_folder, "data", "csv", "players", f"{player_id}-combined.csv")
        
        if not os.path.isfile(combined_csv):
            raise FileNotFoundError(f"Cannot find combined CSV for {player_id} at {combined_csv}")
        self.combined = pd.read_csv(combined_csv)
        

    def get_stats(self):
        """
        Get all stats for the player
        
        Returns:
            DataFrame: All stats for the player
        """
        return self.combined
    
    def get_career_averages(self):
        """
        Compute the average of each prop (“pts”, “reb”, etc.) for all games
        Returns a dict { "pts": float, "reb": float, … }.
        """
        #compute mean of each column
        averages = {}
        for prop in ["pts", "reb", "ast", "stl", "blk", "tov", "fg3", "fg", "ft"]:
            if prop in self.combined.columns:
                averages[prop] = round(self.combined[prop].mean(), 2)
            else:
                averages[prop] = 0.0
        return averages
    
    def get_recent_averages(self, num_games=5):
        """
        Take the last num_games (by date) in the combined CSV and average them.
        Returns a dict { "pts": float, "reb": float, … }.
        """
        # Sort by date descending
        df_sorted = self.combined.sort_values(by="date", ascending=False)
        df_recent = df_sorted.head(num_games)
        if df_recent.empty:
            return { prop: 0.0 for prop in ["pts", "reb", "ast", "stl", "blk", "tov", "fg3", "fg", "ft"] }

        averages = {}
        for prop in ["pts", "reb", "ast", "stl", "blk", "tov", "fg3", "fg", "ft"]:
            if prop in df_recent.columns:
                averages[prop] = round(df_recent[prop].mean(), 2)
            else:
                averages[prop] = 0.0
        return averages

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