import os
import pandas as pd
from typing import List, Dict
import time
import requests
from bs4 import BeautifulSoup
import re

EXCEPTIONS: Dict[str, str] = {
    "Jalen Williams": "willija06",
}

def generate_player_id(name: str) -> str:
    """
    Generates a Basketball-Reference-style player ID from full name.
    Pattern: first five letters of last name + first two letters of first name + "01"
    """
    if name in EXCEPTIONS:
        return EXCEPTIONS[name]

    parts = name.split()
    first, last = parts[0], parts[-1]
    last_key = last[:5].lower() if len(last) >= 5 else last.lower()
    first_key = first[:2].lower()
    return f"{last_key}{first_key}01"

def get_player_ids_from_rosters(teams: List[str], roster_dir: str = "./src/data/csv/rosters") -> Dict[str, str]:
    """
    Build a mapping from full player names to unique IDs using roster CSVs.
    """
    os.makedirs(roster_dir, exist_ok=True)
    player_ids: Dict[str, str] = {}
    
    for team in teams:
        csv_path = os.path.join(roster_dir, f"roster_{team}.csv")
        if not os.path.isfile(csv_path):
            print(f"Roster file not found: {csv_path}")
            continue
        
        df = pd.read_csv(csv_path)
        if 'Player' not in df.columns and 'player' not in df.columns:
            print(f"Missing Player column in {csv_path}")
            continue
        
        name_col = 'Player' if 'Player' in df.columns else 'player'
        for name in df[name_col].dropna().unique():
            pid = generate_player_id(name.rstrip())
            player_ids[name.rstrip()] = pid
    
    return player_ids

def download_rosters(teams: List[str], output_dir: str = "./src/data/csv/rosters"):
    """
    Download roster CSVs for each team if not already present,
    excluding two-way players marked with '(TW)' in the roster listing.
    """
    os.makedirs(output_dir, exist_ok=True)

    for team in teams:
        out_path = os.path.join(output_dir, f"roster_{team}.csv")
        if os.path.exists(out_path):
            print(f"Roster for {team} already exists, skipping.")
            continue

        try:
            url = f"https://www.basketball-reference.com/teams/{team}/2025.html"
            resp = requests.get(url)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, 'html5lib')
            table = soup.find('table', id='roster')
            players = []

            for row in table.find('tbody').find_all('tr'):
                # Find the player cell
                name_cell = row.find('td', {'data-stat': 'player'})
                if not name_cell or not name_cell.a:
                    continue
                # Exclude two-way players marked by "(TW)"
                if '(TW)' in name_cell.get_text():
                    continue
                # Append only the player's name (anchor text)
                players.append(name_cell.a.text.strip())

            # Save to CSV
            pd.DataFrame({'Player': players}).to_csv(out_path, index=False)
            print(f"Downloaded roster for {team}: {len(players)} players (excluding two-way).")
            time.sleep(6)  # Rate limiting

        except Exception as e:
            print(f"Error downloading roster for {team}: {e}")

def parse_table(table) -> pd.DataFrame:
    """
    Parse a basketball-reference stats table into a pandas DataFrame.
    """
    headers = [th.get('data-stat') for th in table.find('thead').find_all('th')]
    rows = []
    for tr in table.find('tbody').find_all('tr'):
        if 'class' in tr.attrs and 'thead' in tr.attrs['class']:
            continue
        row = {cell.get('data-stat'): cell.text.strip() for cell in tr.find_all(['th', 'td']) if cell.get('data-stat')}
        if row:
            rows.append(row)
    return pd.DataFrame(rows, columns=headers)

def get_player_data(player: str, year: int, player_ids: Dict[str, str], output_dir: str = "./src/data/csv/players"):
    """
    Download and save regular-season and playoff game logs for a given player and year.
    """
    try:
        pid = player_ids[player]
        url = f"https://www.basketball-reference.com/players/{pid[0]}/{pid}/gamelog/{year}"
        resp = requests.get(url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, 'html5lib')
        tables = {
            f"{pid}-{year}.csv": soup.find('table', {'class': 'stats_table'}),
            f"{pid}-playoffs-{year}.csv": soup.find('table', {'id': 'player_game_log_post'})
        }
        os.makedirs(output_dir, exist_ok=True)
        for fname, table in tables.items():
            if table:
                df = parse_table(table)
                df.to_csv(os.path.join(output_dir, fname), index=False)
                print(f"Saved {fname}")
            else:
                print(f"No table found for {fname}")
    except Exception as e:
        print(f"Failed to download data for {player} {year}: {e}")