import polars as pl
import numpy as np
import datetime
import plotly.express as px

df1 = pl.read_parquet("data/SWVF_1_full.parquet")
df2 = pl.read_parquet("data/SWVF_2_full.parquet")
df3 = pl.read_parquet("data/SWVF_3_full.parquet")
df4 = pl.read_parquet("data/SWVF_4_full.parquet")

df = pl.concat([
                df1, 
                df2, 
                df3, 
                df4
                ])

def from_unix_timestamp(unix_timestamp):
    epoch = datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
    delta = datetime.timedelta(seconds=unix_timestamp)
    return epoch + delta

df = df\
    .with_columns([
        pl.col("date_of_birth").apply(from_unix_timestamp),
        pl.col("registration_date").apply(from_unix_timestamp)
    ])

sample = df\
    .filter(pl.col("party_affiliation").is_in(["R","D"]))\
    .sample(100_000)



sample.write_csv("sample.csv")



