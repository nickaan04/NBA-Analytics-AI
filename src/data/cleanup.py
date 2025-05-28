import os
import glob
import pandas as pd

TEAMS = ["OKC", "IND"]

# Values that indicate the player did not play
EXCLUDE_VALUES = {"Did Not Play", "Inactive", "Did Not Dress", "", None}

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