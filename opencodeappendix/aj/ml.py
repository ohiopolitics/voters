import polars as pl
import pandas as pd
from shapely.geometry import Point
import geopandas as gpd
from datetime import date
import datetime


year = datetime.date.today().year

df = pl\
    .read_parquet("SWVF_full.parquet")\
    .with_columns(pl.from_epoch(pl.col("date_of_birth")))\
    .with_columns(pl.col("date_of_birth").dt.year())\
    .with_columns(pl.col("date_of_birth").cast(pl.Int64))\
    .with_columns((year - pl.col("date_of_birth")).alias('age'))\
    .with_columns(pl.from_epoch(pl.col("registration_date")))\
    .with_columns(pl.col("registration_date").dt.year())\
    .with_columns(pl.col("registration_date").cast(pl.Int64))\
    .with_columns((year - pl.col("registration_date")).alias('age'))\
    .select(["sos_voter_id", "latitude", "longitude","general_2020", "party_affiliation"])\
    .to_pandas()

geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]

geo_df = gpd.GeoDataFrame(df, geometry=geometry)

shapefile_gdf = gpd\
    .read_file("tl_2021_39_bg")\
    .to_crs("EPSG:4269")


joined_gdf = gpd.sjoin(geo_df,
                       shapefile_gdf,
                       how="inner",
                       predicate="within")\
                .filter(items=["sos_voter_id",
                               "GEOID",
                               "general_2020",
                               "party_affiliation"])\
                .rename(columns={"GEOID":"block_group_id"})\
                .assign(block_group_id = lambda x: x.block_group_id.astype(int))

df = pl.from_pandas(joined_gdf)

df_features = pl.read_parquet("/content/df_features.parquet")\
                .with_columns([
                    pl.col("block_group_id")\
                      .cast(pl.Int64, strict=False)\
                      .alias("block_group_id")
                ])

df_features = df_features.select(pl.col(pl.NUMERIC_DTYPES))
df_big = pl.read_parquet("/content/drive/MyDrive/data_ohio/SWVF_full.parquet")
df_full = df.join(df_features, how="left", on="block_group_id")

df_full_with_features = df_full.join(df_big, how="left", on="sos_voter_id")
