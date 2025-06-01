import os
import glob
import pandas as pd

TEAMS = ["OKC", "IND"]

# Values that indicate the player did not play
EXCLUDE_VALUES = {"Did Not Play", "Inactive", "Did Not Dress", "", None}
REG_PATTERN = "{pid}-regular.csv"
PLAYOFF_PATTERN = "{pid}-playoffs.csv"

# Columns to keep in the final, cleaned CSV
KEEP_COLS = [
    "player_game_num_career",
    "date",
    "pts",
    "blk",
    "orb",
    "drb",
    "ast",
    "stl",
    "tov",
    "fg3",
    "fg",
    "ft"
]

def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    - Remove rows where 'reason' indicates no play.
    - Replace empty strings with NaN.
    - Drop any rows where ALL stat columns are NaN.
    - Keep only KEEP_COLS.
    - Parse and sort by date.
    """
    # 1) Exclude DNP/Inactives if 'reason' exists
    if 'reason' in df.columns:
        df = df[~df['reason'].isin(EXCLUDE_VALUES)]

    # 2) Normalize blanks to actual NaN
    df = df.replace({"": pd.NA, None: pd.NA})

    # 3) Drop rows where all stat columns are missing
    stat_cols = [c for c in KEEP_COLS if c not in ("ranker", "player_game_num_career", "date")]
    df = df.dropna(subset=stat_cols, how='all')

    # 4) Keep only the desired columns
    df = df[KEEP_COLS].copy()

    # 5) Parse 'date' and sort ascending
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)

    return df

def combine_and_clean_player(pid: str, player_dir: str = "./src/data/csv/players"):
    """
    - Globs per-year CSVs for <pid>-YYYY.csv and <pid>-playoffs-YYYY.csv
    - Concatenates, cleans, and sorts them via clean_df()
    - Writes out <pid>-regular.csv and <pid>-playoffs.csv
    - Deletes the original per-year files
    """
    patterns = {
        f"{pid}-regular.csv":  os.path.join(player_dir, f"{pid}-[0-9][0-9][0-9][0-9].csv"),
        f"{pid}-playoffs.csv": os.path.join(player_dir, f"{pid}-playoffs-[0-9][0-9][0-9][0-9].csv"),
    }

    for out_name, pattern in patterns.items():
        files = glob.glob(pattern)
        if not files:
            continue

        # Read & concat all per-year files
        df = pd.concat((pd.read_csv(f) for f in files), ignore_index=True)
        # Clean and sort
        df_clean = clean_df(df)

        # Save comprehensive file
        out_path = os.path.join(player_dir, out_name)
        df_clean.to_csv(out_path, index=False)
        print(f"Created cleaned {out_name} ({len(df_clean)} rows)")

        # Remove originals
        for f in files:
            os.remove(f)
            print(f"  deleted {os.path.basename(f)}")

def merge_player_csvs(pid: str, player_dir: str = "./src/data/csv/players") -> None:
    """
    Merge regular-season and playoff CSVs for a given player into a single
    comprehensive CSV with an 'is_playoff' flag, sorted by date (earliest first).

    Args:
        pid: Player identifier (e.g., 'brunsja01').
        player_dir: Directory where per-year CSVs are stored.
    """
    # Build file patterns
    reg_pattern = os.path.join(player_dir, REG_PATTERN.format(pid=pid))
    playoff_pattern = os.path.join(player_dir, PLAYOFF_PATTERN.format(pid=pid))

    # Collect DataFrames
    dfs = []
    # Regular-season files
    for filepath in glob.glob(reg_pattern):
        df = pd.read_csv(filepath)
        df['is_playoff'] = False
        dfs.append(df)
    # Playoff files
    for filepath in glob.glob(playoff_pattern):
        df = pd.read_csv(filepath)
        df['is_playoff'] = True
        dfs.append(df)

    if not dfs:
        print(f"No files found for player {pid}")
        return

    # Concatenate and sort
    merged = pd.concat(dfs, ignore_index=True)
    # Ensure 'date' is datetime and sort ascending
    if 'date' in merged.columns:
        merged['date'] = pd.to_datetime(merged['date'], errors='coerce')
        merged = merged.sort_values('date').reset_index(drop=True)
    else:
        print("Warning: 'date' column not found; skipping sort.")

    # Output path
    out_file = os.path.join(player_dir, f"{pid}-combined.csv")
    merged.to_csv(out_file, index=False)
    print(f"Merged CSV saved to {out_file}")

def update_rebound_column_in_combined_csvs(player_dir: str = "./src/data/csv/players") -> None:
    """
    Update existing combined CSVs by merging 'orb' and 'drb' into 'reb', dropping
    the original columns, and re-saving the files.

    Args:
        player_dir: Directory where combined CSVs are stored.
    """
    pattern = os.path.join(player_dir, "*-combined.csv")
    for filepath in glob.glob(pattern):
        try:
            df = pd.read_csv(filepath)
            # If orb and drb present, combine and drop
            if 'orb' in df.columns and 'drb' in df.columns:
                df['reb'] = df['orb'].fillna(0) + df['drb'].fillna(0)
                df.drop(columns=['orb', 'drb'], inplace=True)
                df.to_csv(filepath, index=False)
                print(f"Updated rebounds in {os.path.basename(filepath)}")
            else:
                print(f"No orb/drb columns in {os.path.basename(filepath)}, skipping.")
        except Exception as e:
            print(f"Failed to update {os.path.basename(filepath)}: {e}")

def gradient_weighting_by_season(player_dir: str = "./src/data/csv/players"):
    """
    Add season-based weights to player data where more recent seasons have higher weights.
    Weights start at 1.0 for the oldest season and increase by 0.2 for each newer season.
    Seasons are identified by when the game number resets to 1.
    
    Args:
        player_dir: Directory containing the combined player CSV files
    """
    pattern = os.path.join(player_dir, "*-combined.csv")
    for filepath in glob.glob(pattern):
        try:
            df = pd.read_csv(filepath)
            
            # Convert date to datetime if not already
            df['date'] = pd.to_datetime(df['date'])
            
            # Identify seasons by looking at when game number resets to 1
            df['season'] = (df['player_game_num_career'].diff() < 0).cumsum()
            
            # Calculate weights - start at 1.0 and increase by 0.4 each season
            df['weight'] = df['season'].apply(lambda x: 1.0 + (x * 0.4))
            
            # Save the updated dataframe
            df.to_csv(filepath, index=False)
            print(f"Added season weights to {os.path.basename(filepath)}")
            
        except Exception as e:
            print(f"Failed to update {os.path.basename(filepath)}: {e}")

gradient_weighting_by_season()