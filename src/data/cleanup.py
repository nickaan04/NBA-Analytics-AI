import pandas as pd

# List of your 7 CSV files (adjust filenames and paths as needed)
csv_files = [
    "/Users/Ryan/Documents/CSC480/CSC-480/NBA-Analytics-AI/src/data/csv/players/brunsja01-2021.csv",
    "/Users/Ryan/Documents/CSC480/CSC-480/NBA-Analytics-AI/src/data/csv/players/brunsja01-2022.csv",
    "/Users/Ryan/Documents/CSC480/CSC-480/NBA-Analytics-AI/src/data/csv/players/brunsja01-2023.csv",
    "/Users/Ryan/Documents/CSC480/CSC-480/NBA-Analytics-AI/src/data/csv/players/brunsja01-2024.csv",
    "/Users/Ryan/Documents/CSC480/CSC-480/NBA-Analytics-AI/src/data/csv/players/brunsja01-2025.csv",
    "/Users/Ryan/Documents/CSC480/CSC-480/NBA-Analytics-AI/src/data/csv/players/brunsja01-playoffs-2021.csv",
    "/Users/Ryan/Documents/CSC480/CSC-480/NBA-Analytics-AI/src/data/csv/players/brunsja01-playoffs-2022.csv",
    "/Users/Ryan/Documents/CSC480/CSC-480/NBA-Analytics-AI/src/data/csv/players/brunsja01-playoffs-2023.csv",
    "/Users/Ryan/Documents/CSC480/CSC-480/NBA-Analytics-AI/src/data/csv/players/brunsja01-playoffs-2024.csv",
    "/Users/Ryan/Documents/CSC480/CSC-480/NBA-Analytics-AI/src/data/csv/players/brunsja01-playoffs-2025.csv",
]

# Values that indicate the player did not play
EXCLUDE_VALUES = {"Did Not Play", "Inactive", "Did Not Dress", "", None}

def clean_csv(file_path):
    try:
        df = pd.read_csv(file_path)

        if 'is_starter' in df.columns:
            df_clean = df[~df['is_starter'].astype(str).str.strip().isin(EXCLUDE_VALUES)]
            df_clean.to_csv(file_path, index=False)
            print(f"Cleaned: {file_path}")
        else:
            print(f" Skipped (no 'is_starter' column): {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

# Run the cleaner for each file
for file in csv_files:
    clean_csv(file)
