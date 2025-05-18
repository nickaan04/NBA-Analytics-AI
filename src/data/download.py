import os
import pandas as pd
from typing import List, Dict
import time
import requests
from bs4 import BeautifulSoup
import re

teams = ["MIN", "NYK", "IND", "DEN"]
seasons = [2021, 2022, 2023, 2024, 2025]

EXCEPTIONS: Dict[str, str] = {
    # Minnesota
    "Jaden McDaniels": "mcdanja02",
    "Jaylen Clark": "clarkja02",
    "Terrence Shannon Jr.": "shannte01",
    # New York
    "Anton Watson": "watsoan02",
    "Kevin McCullar Jr.": "mcculke01",
    "P.J. Tucker": "tuckepj01",
    # Indiana
    "T.J. McConnell": "mccontj01",
    "Jarace Walker": "walkeja02",
    # Denver
    "Michael Porter Jr.": "portemi01",
    "Jalen Pickett": "pickeja02",
    "Dario Šarić": "saricda01",
    "Nikola Jokić": "jokicni01",
    "Vlatko Čančar": "cancavl01",
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

def download_rosters(teams: List[str]):
    """
    Download roster CSVs for each team if not already present.
    """
    os.makedirs("./src/data/csv/rosters", exist_ok=True)
    for team in teams:
        out_path = f"./src/data/csv/rosters/roster_{team}.csv"
        if os.path.exists(out_path):
            continue
        try:
            url = f"https://www.basketball-reference.com/teams/{team}/2025.html"
            resp = requests.get(url)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, 'html5lib')
            table = soup.find('table', id='roster')
            players = [td.a.text for tr in table.find_all('tr')[1:] if (td := tr.find('td', {'data-stat': 'player'})) and td.a]
            pd.DataFrame({'Player': players}).to_csv(out_path, index=False)
            print(f"Downloaded roster for {team}")
            time.sleep(6)
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

def get_player_data(player: str, year: int, output_dir: str = "./src/data/csv/players"):
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

download_rosters(teams) #download rosters for all teams
player_ids = get_player_ids_from_rosters(teams) #generate unique player IDs from rosters
print("Generated player IDs:", player_ids)
for player in player_ids:
    for season in seasons:
        get_player_data(player, season)
        time.sleep(6)