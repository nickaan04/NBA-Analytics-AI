import os
import pandas as pd
from typing import List
import time
import requests
from bs4 import BeautifulSoup
import re

teams = [
    "MIN",
    "NYK",
    "IND",
    "DEN"
]

player_ids = {
    "Jalen Brunson": "brunsja01",
    "Stephen Curry" : "curryst01"
}

def download_rosters(teams: List[str]):
    for team in teams:
        if os.path.exists(f"./src/data/csv/roster_{team}.csv"):
            continue
        try:
            # Get roster using BeautifulSoup
            url = f"https://www.basketball-reference.com/teams/{team}/2025.html"
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html5lib')
            
            # Find the roster table
            roster_table = soup.find('table', {'id': 'roster'})
            players = []
            
            # Extract player names
            for row in roster_table.find_all('tr')[1:]:  # Skip header row
                name_cell = row.find('td', {'data-stat': 'player'})
                if name_cell and name_cell.a:
                    players.append(name_cell.a.text)
            
            # Create DataFrame and save to CSV
            players_df = pd.DataFrame({'Player': players})
            players_df.to_csv(f"./src/data/csv/roster_{team}.csv", index=False)
            
            print(f"Successfully downloaded roster for {team}")
            time.sleep(6)  # Rate limiting to be respectful to the server
        except Exception as e:
            print(f"Error downloading roster for {team}: {str(e)}")

def parse_table(table) -> pd.DataFrame:
    """Parse a basketball-reference stats table into a pandas DataFrame."""
    headers = [th.get('data-stat') for th in table.find('thead').find_all('th')]
    rows = []
    for tr in table.find('tbody').find_all('tr'):
        # Skip header rows within tbody
        if 'class' in tr.attrs and 'thead' in tr.attrs['class']:
            continue
        row_data = {}
        for cell in tr.find_all(['th', 'td']):
            stat = cell.get('data-stat')
            value = cell.text.strip()
            if stat:
                row_data[stat] = value
        if row_data:
            rows.append(row_data)
    return pd.DataFrame(rows, columns=headers)

def get_player_data(player: str, year: int, output_dir: str= "./src/data/csv/players"):
    try:
        player_id = player_ids[player]

        url = f"https://www.basketball-reference.com/players/{player_id[0]}/{player_id}/gamelog/{year}"
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html5lib')
        
        # Process both regular and playoff tables
        tables = {
            f"{player_id}-{year}.csv": soup.find('table', {'class': 'stats_table'}),
            f"{player_id}-playoffs-{year}.csv": soup.find('table', {'id': 'player_game_log_post'})
        }

        for filename, table in tables.items():
            if table:
                df = parse_table(table)
                df.to_csv(f"{output_dir}/{filename}", index=False)
                print(f"Saved data to {output_dir}/{filename}")
            else:
                print(f"No table found for {filename}")
                
    except KeyError:
        print(f"Unknown player: {player}")
    except requests.HTTPError as http_err:
        print(f"HTTP error for {player}: {http_err}")
    except Exception as e:
        print(f"Error downloading game log for {player}: {e}")

def download_roster_data(team: str):
    roster = pd.read_csv(f"./src/data/csv/roster_{team}.csv")
    for player in roster['Player']:
        print(f"\n\n\n{player}")
        if "tw" in player:
            print("two-way player - Skipping")
            continue
        player_data = get_player_data(player, 2025)
        if player_data:
            # Create directory if it doesn't exist
            os.makedirs("./src/data/csv/players", exist_ok=True)
            # Save to file
            with open(f"./src/data/csv/players/{player.lower().replace(' ','')}.csv", "w+") as f:
                f.write(player_data)
        time.sleep(6)  # Rate limiting to be respectful to the server


seasons = [2021, 2022, 2023, 2024, 2025]
for season in seasons:
    get_player_data("Stephen Curry", season)
    time.sleep(6)  # Rate limiting to be respectful to the server