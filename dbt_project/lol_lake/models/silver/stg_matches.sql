{{ config(materialized='table', schema='silver') }}

select
    match_id,
    patch,
    champion_name,
    championId,
    team_position,
    win,
    kills,
    deaths,
    assists,
    case
        when deaths = 0 then kills + assists
        else round((kills + assists) / deaths::float, 2)
    end                                             as kda,
    cs,
    round(cs / (game_duration / 60.0), 1)          as cs_per_min,
    total_damage,
    vision_score,
    game_duration
from {{ ref('raw_matches') }}
where champion_name is not null
  and game_duration > 300