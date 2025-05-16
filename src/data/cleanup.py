import pandas as pd

# List of your 7 CSV files (adjust filenames and paths as needed)
csv_files = [
    "./src/data/csv/players/brunsja01-2021.csv",
    "./src/data/csv/players/brunsja01-2022.csv",
    "./src/data/csv/players/brunsja01-2023.csv",
    "./src/data/csv/players/brunsja01-2024.csv",
    "./src/data/csv/players/brunsja01-2025.csv",
    "./src/data/csv/players/brunsja01-playoffs-2021.csv",
    "./src/data/csv/players/brunsja01-playoffs-2022.csv",
    "./src/data/csv/players/brunsja01-playoffs-2023.csv",
    "./src/data/csv/players/brunsja01-playoffs-2024.csv",
    "./src/data/csv/players/brunsja01-playoffs-2025.csv",
]

# Values that indicate the player did not play
EXCLUDE_VALUES = {"Did Not Play", "Inactive", "Did Not Dress", "", None}
KEEP_COLS = [
    "ranker", "player_game_num_career", "date",
    "pts", "blk", "orb", "drb", "ast", "stl", "tov", "fg3", "fg", "ft"]


def clean_and_filter(file_path):
    try:
        df = pd.read_csv(file_path)
        if 'is_starter' in df.columns:
            df = df[~df['is_starter'].astype(str).isin(EXCLUDE_VALUES)]
        df = df[KEEP_COLS]
        df.to_csv(file_path, index=False)
        print(f"Cleaned & filtered: {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

for file in csv_files:
    clean_and_filter(file)
