import time
from typing import List
from download import get_player_ids_from_rosters, get_player_data
from cleanup import combine_and_clean_player

TEAMS = ["OKC", "IND"]
SEASONS = [2022, 2023, 2024, 2025]

def main(teams: List[str], seasons: List[int]) -> None: #download player data, clean and combine csvs
    #Build player name → ID map from existing rosters
    player_map = get_player_ids_from_rosters(teams)
    print(f"Found {len(player_map)} players across teams: {teams}")

    #Download per-year logs for each player & season
    for player_name in player_map:
        print(f"\nDownloading data for {player_name}")
        for year in seasons:
            get_player_data(player_name, year, player_map)
            time.sleep(6)  #rate-limit

    #Combine and clean into comprehensive CSVs per player
    print("\nCombining and cleaning per-player CSVs...")
    for name, pid in player_map.items():
        print(f"Processing player: {name} ({pid})")
        combine_and_clean_player(pid)

if __name__ == "__main__":
    main(TEAMS, SEASONS)
