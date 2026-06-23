{{ config(materialized='view', schema='bronze') }}

select * from read_parquet('C:/Users/gabri/Desktop/lol-data-lake/data/bronze/*.parquet')