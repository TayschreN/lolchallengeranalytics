{{ config(materialized='table', schema='gold') }}

with base as (
    select
        patch,
        champion_name,
        team_position,
        games_played,
        win_rate,
        avg_kda,
        avg_cs_min,
        pick_rate
    from {{ ref('fct_champion_stats') }}
    where games_played >= 10
),

normalized as (
    select
        *,
        -- normaliza cada métrica entre 0 e 1 por posição
        round((win_rate  - min(win_rate)  over (partition by team_position))
            / nullif(max(win_rate)  over (partition by team_position)
            -        min(win_rate)  over (partition by team_position), 0), 3) as wr_norm,

        round((avg_kda   - min(avg_kda)   over (partition by team_position))
            / nullif(max(avg_kda)   over (partition by team_position)
            -        min(avg_kda)   over (partition by team_position), 0), 3) as kda_norm,

        round((pick_rate - min(pick_rate) over (partition by team_position))
            / nullif(max(pick_rate) over (partition by team_position)
            -        min(pick_rate) over (partition by team_position), 0), 3) as pr_norm
    from base
),

scored as (
    select
        *,
        -- peso: win_rate 50%, kda 30%, pick_rate 20%
        round(
            (coalesce(wr_norm,  0) * 0.50) +
            (coalesce(kda_norm, 0) * 0.30) +
            (coalesce(pr_norm,  0) * 0.20)
        , 3) as score
    from normalized
),

ranked as (
    select
        *,
        rank() over (partition by team_position order by score desc) as position_rank,
        case
            when score >= 0.75 then 'S'
            when score >= 0.55 then 'A'
            when score >= 0.35 then 'B'
            when score >= 0.15 then 'C'
            else                    'D'
        end as tier
    from scored
)

select
    patch,
    champion_name,
    team_position,
    tier,
    position_rank,
    score,
    win_rate,
    avg_kda,
    pick_rate,
    games_played
from ranked
order by team_position, position_rank