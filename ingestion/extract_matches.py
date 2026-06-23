import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import pandas as pd
from pathlib import Path
from datetime import datetime
from ingestion.riot_client import get_challenger_players, get_match_ids, get_match

def extract_participant_row(participant, match_id, patch, duration):
    return {
        "match_id":      match_id,
        "patch":         ".".join(patch.split(".")[:2]),
        "champion_name": participant["championName"],
        "team_position": participant["teamPosition"],
        "win":           participant["win"],
        "kills":         participant["kills"],
        "deaths":        participant["deaths"],
        "assists":       participant["assists"],
        "total_damage":  participant["totalDamageDealtToChampions"],
        "cs":            participant["totalMinionsKilled"] + participant["neutralMinionsKilled"],
        "vision_score":  participant["visionScore"],
        "game_duration": duration,
    }

def extract_ban_rows(match, match_id, patch):
    rows = []
    for team in match["info"]["teams"]:
        for ban in team.get("bans", []):
            champ_id = ban.get("championId", -1)
            if champ_id > 0:
                rows.append({
                    "match_id":    match_id,
                    "patch":       ".".join(patch.split(".")[:2]),
                    "champion_id": champ_id,
                })
    return rows

def run_extraction(max_players=50, matches_per_player=20):
    print("Buscando jogadores challenger BR...")
    players = get_challenger_players()[:max_players]

    match_rows = []
    ban_rows   = []
    seen       = set()

    for i, player in enumerate(players):
        name = player.get("summonerName", f"player_{i+1}")
        puuid = player.get("puuid")
        print(f"[{i+1}/{max_players}] {name}")

        try:
            match_ids = get_match_ids(puuid, count=matches_per_player)
            time.sleep(0.5)

            for match_id in match_ids:
                if match_id in seen:
                    continue
                seen.add(match_id)

                match    = get_match(match_id)
                patch    = match["info"]["gameVersion"]
                duration = match["info"]["gameDuration"]
                time.sleep(1.2)

                for p in match["info"]["participants"]:
                    match_rows.append(extract_participant_row(p, match_id, patch, duration))

                ban_rows.extend(extract_ban_rows(match, match_id, patch))

        except Exception as e:
            print(f"  Erro: {e}")
            continue

    save_bronze(pd.DataFrame(match_rows), "matches")
    save_bronze(pd.DataFrame(ban_rows),   "bans")
    print(f"\nPartidas: {len(match_rows)} linhas | Bans: {len(ban_rows)} linhas")

def save_bronze(df, name):
    path = Path("data/bronze")
    path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    file = path / f"{name}_{timestamp}.parquet"
    df.to_parquet(file, index=False)
    print(f"Salvo em {file}")

if __name__ == "__main__":
    run_extraction(max_players=50, matches_per_player=20)