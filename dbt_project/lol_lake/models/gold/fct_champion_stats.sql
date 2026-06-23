{{ config(materialized='table', schema='gold') }}

select
    patch,
    champion_name,
    team_position,
    count(*)                                        as games_played,
    round(avg(win::int) * 100, 1)                   as win_rate,
    round(avg(kda), 2)                              as avg_kda,
    round(avg(cs_per_min), 1)                       as avg_cs_min,
    round(avg(total_damage), 0)                     as avg_damage,
    round(avg(kills), 1)                            as avg_kills,
    round(avg(deaths), 1)                           as avg_deaths,
    round(avg(assists), 1)                          as avg_assists
from {{ ref('stg_matches') }}
group by 1, 2, 3
having count(*) >= 5
order by patch desc, games_played desc