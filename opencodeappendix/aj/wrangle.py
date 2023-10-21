
import pandas as pd
import numpy as np
from datetime import datetime

df = pd\
    .read_parquet("SWVF_full.parquet")\
    .assign(date_of_birth=lambda x: pd.to_datetime(x.date_of_birth, unit='s'))\
    .assign(age=lambda x: datetime.now().year - x['date_of_birth'].dt.year)


d_probs = pd.read_parquet("D_probs_df.parquet")
r_probs = pd.read_parquet("R_probs_df.parquet")
vt_probs = pd.read_parquet("OH_VT_Predictions.parquet")

df = df\
    .merge(d_probs, how='left', on='sos_voter_id')\
    .merge(r_probs, how='left', on='sos_voter_id')\
    .merge(vt_probs, how='left', on='sos_voter_id')

df = df\
    .fillna(0)\
    .assign(age=lambda x:
         np.where(x['age'] <= 25, '18-25',
         np.where(x['age'] <= 40, '26-40',
         np.where(x['age'] <= 64, '41-64', '65+'))))\


summary_df = df\
    .filter(items=["party_affiliation","age","general_2020","sos_voter_id"])\
    .groupby(["party_affiliation","age","general_2020"], as_index=False)\
    .count()


summary_df = df\
    .groupby(["party_affiliation","age","general_2020"], as_index=False)\
    .agg(
      r_TO = pd.NamedAgg(column = 'r_probs', aggfunc = np.sum),
      d_TO = pd.NamedAgg(column = 'd_probs', aggfunc = np.sum)
    )


summary_df.to_csv("summary.csv", index=False)