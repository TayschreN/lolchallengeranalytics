import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY   = os.getenv("RIOT_API_KEY")
REGION    = os.getenv("RIOT_REGION", "br1")
REGION_V5 = os.getenv("RIOT_REGION_V5", "americas")

BASE_V4 = f"https://{REGION}.api.riotgames.com"
BASE_V5 = f"https://{REGION_V5}.api.riotgames.com"

HEADERS = {"X-Riot-Token": API_KEY}

def _get(url, params=None, retries=3):
    for attempt in range(retries):
        resp = requests.get(url, headers=HEADERS, params=params)
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code == 429:
            wait = int(resp.headers.get("Retry-After", 10))
            print(f"Rate limit. Aguardando {wait}s...")
            time.sleep(wait)
            continue
        resp.raise_for_status()
    raise Exception(f"Falhou após {retries} tentativas: {url}")

def get_challenger_players(queue="RANKED_SOLO_5x5"):
    url = f"{BASE_V4}/lol/league/v4/challengerleagues/by-queue/{queue}"
    return _get(url)["entries"]

def get_puuid(summoner_id):
    url = f"{BASE_V4}/lol/summoner/v4/summoners/{summoner_id}"
    return _get(url)["puuid"]

def get_match_ids(puuid, count=20):
    url = f"{BASE_V5}/lol/match/v5/matches/by-puuid/{puuid}/ids"
    return _get(url, {"queue": 420, "count": count})

def get_match(match_id):
    url = f"{BASE_V5}/lol/match/v5/matches/{match_id}"
    return _get(url)