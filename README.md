# LoL Challenger Analytics — Data Lake BR

Pipeline de engenharia de dados end-to-end que coleta partidas ranqueadas dos jogadores **Challenger brasileiros** via Riot Games API, processa os dados em camadas (Bronze → Silver → Gold) com **dbt + DuckDB**, e entrega métricas analíticas de campeões por patch.

---

## Visão geral

O projeto responde perguntas como:
- Quais campeões têm maior win rate no Challenger BR no patch atual?
- Como o meta evolui entre patches?
- Quais posições apresentam maior KDA médio?

---

## Arquitetura

```
Riot Games API
      │
      ▼
 Python (ingestão)
      │  requests + pandas
      ▼
 Bronze (raw .parquet)
      │
      ▼
 Silver (dbt — limpeza e tipagem)
      │
      ▼
 Gold (dbt — modelos analíticos)
      │
      ▼
 DuckDB (warehouse local)
      │
      ▼
 Power BI (dashboard)
```

Arquitetura **Medallion** (Bronze / Silver / Gold), padrão utilizado em data lakes modernos.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Ingestão | Python 3.11, requests, pandas |
| Armazenamento | Apache Parquet |
| Transformação | dbt-duckdb 1.8 |
| Warehouse | DuckDB 1.5 |
| Orquestração | (em desenvolvimento) Apache Airflow |
| Visualização | Power BI |

---

## Estrutura do projeto

```
lol-data-lake/
├── ingestion/
│   ├── riot_client.py        # cliente HTTP da Riot API
│   └── extract_matches.py    # extração de partidas challenger
├── dbt_project/
│   └── lol_lake/
│       └── models/
│           ├── bronze/       # raw_matches (view)
│           ├── silver/       # stg_matches (limpeza)
│           └── gold/         # fct_champion_stats (analytics)
├── data/
│   └── bronze/               # arquivos .parquet raw
├── warehouse/
│   └── lol.duckdb            # banco DuckDB local
├── .env                      # chave da API (não sobe pro git)
└── requirements.txt
```

---

## Como rodar

### Pré-requisitos

- Python 3.11
- Chave da [Riot Developer API](https://developer.riotgames.com) (gratuita)

### Instalação

```bash
git clone https://github.com/seu-usuario/lol-data-lake.git
cd lol-data-lake

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
```

### Configuração

Crie o arquivo `.env` na raiz:

```
RIOT_API_KEY=RGAPI-sua-chave-aqui
RIOT_REGION=br1
RIOT_REGION_V5=americas
```

> A chave de desenvolvimento expira em 24h. Renove em [developer.riotgames.com](https://developer.riotgames.com).

### Execução

**1. Ingestão** — coleta partidas dos challengers BR:
```bash
python ingestion/extract_matches.py
```

**2. Transformação** — processa as camadas dbt:
```bash
cd dbt_project/lol_lake
dbt run
```

**3. Consulta** — lê os dados analíticos:
```python
import duckdb

con = duckdb.connect("warehouse/lol.duckdb")
df = con.execute("""
    select champion_name, team_position, games_played, win_rate, avg_kda
    from main_gold.fct_champion_stats
    order by win_rate desc
    limit 15
""").df()
print(df)
```

---

## Modelos dbt

### Bronze — `raw_matches`
View sobre os arquivos `.parquet` raw. Nenhuma transformação aplicada.

### Silver — `stg_matches`
Limpeza e enriquecimento:
- Remove partidas com menos de 5 minutos (remakes)
- Calcula KDA normalizado (mortes = 0 → KDA = kills + assists)
- Calcula CS por minuto

### Gold — `fct_champion_stats`
Tabela analítica agregada por campeão, posição e patch:
- `win_rate` — percentual de vitórias
- `avg_kda` — KDA médio
- `avg_cs_min` — CS por minuto médio
- `avg_damage` — dano médio por partida
- Filtro mínimo de 5 jogos por campeão/posição

---

## Exemplo de output

```
    champion_name team_position  games_played  win_rate  avg_kda
0           Akali        MIDDLE             6      83.3     4.87
1          Thresh       UTILITY             6      83.3     4.46
2           Sivir        BOTTOM             6      83.3     3.20
3         Shyvana        JUNGLE             5      80.0     3.49
4           Varus        BOTTOM             5      80.0     8.69
5            Sona       UTILITY            11      72.7     4.99
```

---

## Próximos passos

- [ ] Adicionar testes dbt (`dbt test`) para validação de dados
- [ ] Agendamento automático com Apache Airflow (coleta semanal por patch)
- [ ] Dashboard interativo no Power BI
- [ ] Coleta histórica para análise de evolução do meta por patch
- [ ] Enriquecimento com Data Dragon (ícones, roles oficiais, stats base)

---

## Autor

**Gabriel França da Silva**
Estudante de Ciências e Tecnologia — UFABC
[LinkedIn](https://linkedin.com/in/seu-perfil) · [Portfolio](https://datascienceportfol.io/gabrielfsilva2609)
