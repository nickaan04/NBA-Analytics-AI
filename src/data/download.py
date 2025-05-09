import os
import pandas as pd
from typing import List
import time
import requests
from bs4 import BeautifulSoup
import re

teams = [
  "HOU",
  "ATL",
  "CHI",
  "CLE",
  "DAL",
  "LAL"
]

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

def get_player_data(player: str, year: int):
    try:
        # Create player URL (convert spaces to hyphens, lowercase)
        player_url = player.lower().replace(' ', '-')
        # Handle special characters in names
        player_url = re.sub(r'[^\w\-]', '', player_url)
        # Get first 5 letters of last name + first 2 of first name
        name_parts = player.split(' ')
        if len(name_parts) >= 2:
            last_name = name_parts[-1][:5]
            first_name = name_parts[0][:2]
            player_id = f"{last_name}{first_name}01".lower()
            
            url = f"https://www.basketball-reference.com/players/{player_id[0]}/{player_id}/gamelog/{year}"
            response = requests.get(url)
            
            if response.status_code != 200:
                print(f"Could not find game log data for {player}")
                return None
                
            soup = BeautifulSoup(response.content, 'html5lib')
            game_log_table = soup.find('table', {'class': 'stats_table'})
            
            if not game_log_table:
                print(f"No game log table found for {player}")
                return None
                
            # Extract headers
            headers = []
            header_row = game_log_table.find('thead').find_all('th')
            for header in header_row:
                headers.append(header.get('data-stat'))
                
            # Extract data
            rows = []
            for row in game_log_table.find('tbody').find_all('tr', class_=lambda x: x != 'thead'):
                if 'class' in row.attrs and 'thead' in row.attrs['class']:
                    continue
                    
                row_data = {}
                for cell in row.find_all(['th', 'td']):
                    stat = cell.get('data-stat')
                    value = cell.text.strip()
                    row_data[stat] = value
                    
                if row_data:
                    rows.append(row_data)
                    
            # Create DataFrame
            game_logs = pd.DataFrame(rows)
            
            # Convert to CSV string
            csv_content = game_logs.to_csv(index=False)
            return csv_content
        else:
            print(f"Invalid player name format: {player}")
            return None
    except Exception as e:
        print(f"Error downloading game log for {player}: {str(e)}")
        return None

def download_roster_data(team: str):
    roster = pd.read_csv(f"./src/data/csv/roster_{team}.csv")
    for player in roster['Player']:
        print(f"\n\n\n{player}")
        player_data = get_player_data(player, 2025)
        if player_data:
            # Create directory if it doesn't exist
            os.makedirs("./src/data/csv/players", exist_ok=True)
            # Save to file
            with open(f"./src/data/csv/players/{player.lower().replace(' ','')}.csv", "w+") as f:
                f.write(player_data)
        time.sleep(6)  # Rate limiting to be respectful to the server

download_roster_data("LAL")

