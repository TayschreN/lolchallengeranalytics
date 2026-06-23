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

def run_extraction(max_players=10, matches_per_player=10):
    print("Buscando jogadores challenger BR...")
    players = get_challenger_players()[:max_players]

    # debug: mostra os campos disponíveis no primeiro jogador
    if players:
        print(f"Campos disponíveis: {list(players[0].keys())}")

    rows = []
    seen = set()

    for i, player in enumerate(players):
        # tenta pegar puuid direto da entry, senão busca pelo summonerId
        puuid = player.get("puuid")
        name  = player.get("summonerName", f"player_{i+1}")
        print(f"[{i+1}/{max_players}] {name} | puuid: {'sim' if puuid else 'não'}")

        try:
            if not puuid:
                from ingestion.riot_client import get_puuid
                puuid = get_puuid(player["summonerId"])
                time.sleep(0.5)

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
                    rows.append(extract_participant_row(p, match_id, patch, duration))

        except Exception as e:
            print(f"  Erro: {e}")
            continue

    df = pd.DataFrame(rows)
    save_bronze(df)
    print(f"\nTotal: {len(df)} linhas extraídas")
    return df

def save_bronze(df):
    path = Path("data/bronze")
    path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    file = path / f"matches_{timestamp}.parquet"
    df.to_parquet(file, index=False)
    print(f"Salvo em {file}")

if __name__ == "__main__":
    run_extraction(max_players=50, matches_per_player=20)