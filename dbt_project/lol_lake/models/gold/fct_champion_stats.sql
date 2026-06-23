{{ config(materialized='table', schema='gold') }}

with matches as (
    select
        patch,
        champion_name,
        team_position,
        count(*)                            as games_played,
        round(avg(win::int) * 100, 1)       as win_rate,
        round(avg(kda), 2)                  as avg_kda,
        round(avg(cs_per_min), 1)           as avg_cs_min,
        round(avg(total_damage), 0)         as avg_damage,
        round(avg(kills), 1)                as avg_kills,
        round(avg(deaths), 1)               as avg_deaths,
        round(avg(assists), 1)              as avg_assists
    from {{ ref('stg_matches') }}
    group by 1, 2, 3
    having count(*) >= 5
),

total_games_per_patch as (
    select
        patch,
        count(distinct match_id)            as total_games
    from {{ ref('stg_matches') }}
    group by 1
),

bans as (
    select
        patch,
        champion_id,
        count(*)                            as total_bans
    from {{ ref('raw_bans') }}
    group by 1, 2
),

champion_map as (
    select distinct
        patch,
        champion_name,
        championId                          as champion_id
    from {{ ref('stg_matches') }}
)

select
    m.patch,
    m.champion_name,
    m.team_position,
    m.games_played,
    m.win_rate,
    m.avg_kda,
    m.avg_cs_min,
    m.avg_damage,
    m.avg_kills,
    m.avg_deaths,
    m.avg_assists,
    round(m.games_played * 100.0 / t.total_games, 1)   as pick_rate,
    round(coalesce(b.total_bans, 0) * 100.0 / t.total_games, 1) as ban_rate
from matches m
join total_games_per_patch t on m.patch = t.patch
left join champion_map cm    on m.champion_name = cm.champion_name and m.patch = cm.patch
left join bans b             on cm.champion_id = b.champion_id and cm.patch = b.patch
order by m.patch desc, m.games_played desc