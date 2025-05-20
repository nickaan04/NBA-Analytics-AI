import pandas as pd
import os

# Define file paths
regular_season_files = [
    "./src/data/csv/players/brunsja01-2021.csv",
    "./src/data/csv/players/brunsja01-2022.csv",
    "./src/data/csv/players/brunsja01-2023.csv",
    "./src/data/csv/players/brunsja01-2024.csv",
    "./src/data/csv/players/brunsja01-2025.csv"
]

playoff_files = [
    "./src/data/csv/players/brunsja01-playoffs-2021.csv",
    "./src/data/csv/players/brunsja01-playoffs-2022.csv",
    "./src/data/csv/players/brunsja01-playoffs-2023.csv",
    "./src/data/csv/players/brunsja01-playoffs-2024.csv",
    "./src/data/csv/players/brunsja01-playoffs-2025.csv"
]

# Values that indicate the player did not play
EXCLUDE_VALUES = {"Did Not Play", "Inactive", "Did Not Dress", "", None}

# Columns to keep
KEEP_COLS = [
    "ranker", "player_game_num_career", "date",
    "pts", "blk", "orb", "drb", "ast", "stl", "tov", "fg3", "fg", "ft"
]

def clean_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        if 'is_starter' in df.columns:
            df = df[~df['is_starter'].astype(str).isin(EXCLUDE_VALUES)]
        return df[KEEP_COLS]
    except Exception as e:
        print(f"Failed to process {file_path}: {e}")
        return pd.DataFrame(columns=KEEP_COLS)

# Combine and save
def combine_and_save(file_list, output_path):
    combined_df = pd.concat([clean_csv(file) for file in file_list], ignore_index=True)
    combined_df.to_csv(output_path, index=False)
    print(f"Saved combined file: {output_path}")

# Combine regular season and playoff files
combine_and_save(regular_season_files, "./src/data/csv/players/brunson_regular.csv")
combine_and_save(playoff_files, "./src/data/csv/players/brunson_playoffs.csv")
