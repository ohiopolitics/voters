import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
from datetime import datetime
now = datetime.now()

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn import metrics as m
import shap


import folium
from shapely.geometry import Point
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import plotly.express as px


import fiona


# with fiona.Env():
#     layers = fiona.listlayers("./ACS_2021_5YR_BG_39_OHIO.gdb")
#     for layer in layers:
#         print(layer)


urban_classifications = {
    11: "city_large", 12: "city_midsize", 13: "city_small", 21: "suburban_large", 22: "suburban_midsize", 23: "suburban_small", 31: "town_fringe", 32: "town_distant", 33: "town_remote", 41: "rural_fringe", 42: "rural_distant", 43: "rural_remote"}

# Locale
locale_gdf = gpd\
    .read_file("./edge_locale21_nces_OH/edge_locale21_nces_OH.shp")\
    .filter(items=["LOCALE","geometry"])\
    .to_crs("EPSG:4326")\
    # .assign(LOCALE = lambda x: x.LOCALE.astype(int).replace(urban_classifications))



# Block Groups
gdf_bgs = gpd\
    .read_file("tl_2021_39_bg/tl_2021_39_bg.shp")\
    .filter(items=["GEOID","COUNTYFP","geometry"])\
    .to_crs("EPSG:4326")\
    .assign(COUNTYFP = lambda x: x.COUNTYFP.astype(int))\
    .rename(columns={"GEOID": "block_group_id"})



# Tracts
gdf_ts = gpd\
    .read_file("tl_rd22_39_tract/tl_rd22_39_tract.shp")\
    .filter(items=["GEOID","COUNTYFP","geometry"])\
    .to_crs("EPSG:4326")\
    .assign(COUNTYFP = lambda x: x.COUNTYFP.astype(int))\
    .rename(columns={"GEOID": "tract_id"})

###

## Income
income_bgs = gpd\
    .read_file("./ACS_2021_5YR_BG_39_OHIO.gdb", layer='X19_INCOME')\
    .filter(items=["GEOID","B19013e1","B19013m1"])\
    .dropna()\
    .rename(columns={
                "GEOID": "temp",   
                "B19013e1": "median_income",
                "B19013m1": "median_income_moe"})\
    .assign(GEOID = lambda x: x.temp.str.split("US").str.get(1))\
    .drop(columns=["temp"])\
    .rename(columns={"GEOID": "block_group_id"})

## Earnings
earnings_bgs = gpd\
    .read_file("./ACS_2021_5YR_BG_39_OHIO.gdb", layer='X20_EARNINGS')\
    .filter(items=["GEOID","B20002e1","B20002m1"])\
    .dropna()\
    .rename(columns={
                "GEOID": "temp",   
                "B20002e1": "median_earnings",
                "B20002m1": "median_earnings_moe"})\
    .assign(GEOID = lambda x: x.temp.str.split("US").str.get(1))\
    .drop(columns=["temp"])\
    .rename(columns={"GEOID": "block_group_id"})

## Employment
employment_bgs = gpd\
    .read_file("./ACS_2021_5YR_BG_39_OHIO.gdb", layer='X23_EMPLOYMENT_STATUS')\
    .filter(items=["GEOID", "B23025e1", "B23025e2", "B23025e3", "B23025e4", "B23025e6"])\
    .dropna()\
    .rename(columns={
                "GEOID": "temp",   
                "B23025e1": "pop_over_16",
                "B23025e2": "pop_over_16_laborforce",
                "B23025e3": "pop_civilian_laborforce",
                "B23025e4": "pop_civilian_laborforce_employed",
                "B23025e6": "pop_civilian_laborforce_armedforces"})\
    .assign(GEOID = lambda x: x.temp.str.split("US").str.get(1))\
    .assign(
        percent_employed_total = lambda x: x.pop_over_16_laborforce / x.pop_over_16,
        percent_employed_civilian = lambda x: x.pop_civilian_laborforce_employed / x.pop_civilian_laborforce)\
    .drop(columns=["temp","pop_over_16"])\
    .rename(columns={"GEOID": "block_group_id"})

## Poverty
poverty_bgs = gpd\
    .read_file("./ACS_2021_5YR_BG_39_OHIO.gdb", layer='X17_POVERTY')\
    .filter(items=["GEOID","B17017e1","B17017e2","B17017e3","B17017e4"])\
    .dropna()\
    .rename(columns={
        "GEOID": "temp",
        "B17017e1": "total_households",
        "B17017e2": "income_below_poverty",
        "B17017e3": "family_below_poverty",
        "B17017e4": "family_married_below_poverty"})\
    .assign(GEOID = lambda x: x.temp.str.split("US").str.get(1))\
    .assign(
        percent_family_below_poverty = lambda x: x.family_below_poverty / x.total_households,
        percent_family_married_below_poverty = lambda x: x.family_married_below_poverty / x.total_households)\
    .drop(columns=["temp","total_households"])\
    .rename(columns={"GEOID": "block_group_id"})

## Industry
industry_bgs = gpd\
    .read_file("./ACS_2021_5YR_BG_39_OHIO.gdb", layer='X24_INDUSTRY_OCCUPATION')\
    .filter(items=["GEOID","C24010e1","C24010e5","C24010e6","C24010e8","C24010e9","C24010e10","C24010e12","C24010e13","C24010e14","C24010e15","C24010e17","C24010e18","C24010e20","C24010e21","C24010e22","C24010e23","C24010e24","C24010e25","C24010e26","C24010e27","C24010e28","C24010e29","C24010e30","C24010e31","C24010e32","C24010e33","C24010e34","C24010e35","C24010e36","C24010e37"])\
    .dropna()\
    .rename(columns={
        "GEOID": "temp",
        "C24010e1": "employed_pop",
        "C24010e5": "employed_management",
        "C24010e6": "employed_business",
        "C24010e8": "employed_compsci",
        "C24010e9": "employed_engineering",
        "C24010e10": "employed_socialscience",
        "C24010e12": "employed_socialservice",
        "C24010e13": "employed_legal",
        "C24010e14": "employed_education",
        "C24010e15": "employed_arts",
        "C24010e17": "employed_healthcare_practitioners",
        "C24010e18": "employed_health_technologists",
        "C24010e20": "employed_healthcaresupport",
        "C24010e21": "employed_protectiveservice",
        "C24010e22": "employed_firefighting",
        "C24010e23": "employed_lawenforcement",
        "C24010e24": "employed_foodpreparation",
        "C24010e25": "employed_buildingcleaning",
        "C24010e26": "employed_personalcare",
        "C24010e27": "employed_salesoffice",
        "C24010e28": "employed_salesrelated",
        "C24010e29": "employed_officeadmin",
        "C24010e30": "employed_naturalresources",
        "C24010e31": "employed_farming",
        "C24010e32": "employed_construction",
        "C24010e33": "employed_installationmaintenance",
        "C24010e34": "employed_productiontransportation",
        "C24010e35": "employed_production",
        "C24010e36": "employed_transportation",
        "C24010e37": "employed_materialmoving"})\
    .assign(GEOID = lambda x: x.temp.str.split("US").str.get(1))\
    .assign(
        percent_employed_management = lambda x: x.employed_management / x.employed_pop,
        percent_employed_business = lambda x: x.employed_business / x.employed_pop,
        percent_employed_compsci = lambda x: x.employed_compsci / x.employed_pop,
        percent_employed_engineering = lambda x: x.employed_engineering / x.employed_pop,
        percent_employed_socialscience = lambda x: x.employed_socialscience / x.employed_pop,
        percent_employed_socialservice = lambda x: x.employed_socialservice / x.employed_pop,
        percent_employed_legal = lambda x: x.employed_legal / x.employed_pop,
        percent_employed_education = lambda x: x.employed_education / x.employed_pop,
        percent_employed_arts = lambda x: x.employed_arts / x.employed_pop,
        percent_employed_healthcare_practitioners = lambda x: x.employed_healthcare_practitioners / x.employed_pop,
        percent_employed_health_technologists = lambda x: x.employed_health_technologists / x.employed_pop,
        percent_employed_healthcaresupport = lambda x: x.employed_healthcaresupport / x.employed_pop,
        percent_employed_protectiveservice = lambda x: x.employed_protectiveservice / x.employed_pop,
        percent_employed_firefighting = lambda x: x.employed_firefighting / x.employed_pop,
        percent_employed_lawenforcement = lambda x: x.employed_lawenforcement / x.employed_pop,
        percent_employed_foodpreparation = lambda x: x.employed_foodpreparation / x.employed_pop,
        percent_employed_buildingcleaning = lambda x: x.employed_buildingcleaning / x.employed_pop,
        percent_employed_personalcare = lambda x: x.employed_personalcare / x.employed_pop,
        percent_employed_salesoffice = lambda x: x.employed_salesoffice / x.employed_pop,
        percent_employed_salesrelated = lambda x: x.employed_salesrelated / x.employed_pop,
        percent_employed_officeadmin = lambda x: x.employed_officeadmin / x.employed_pop,
        percent_employed_naturalresources = lambda x: x.employed_naturalresources / x.employed_pop,
        percent_employed_farming = lambda x: x.employed_farming / x.employed_pop,
        percent_employed_construction = lambda x: x.employed_construction / x.employed_pop,
        percent_employed_installationmaintenance = lambda x: x.employed_installationmaintenance / x.employed_pop,
        percent_employed_productiontransportation = lambda x: x.employed_productiontransportation / x.employed_pop,
        percent_employed_production = lambda x: x.employed_production / x.employed_pop,
        percent_employed_transportation = lambda x: x.employed_transportation / x.employed_pop,
        percent_employed_materialmoving = lambda x: x.employed_materialmoving / x.employed_pop)\
    .drop(columns=["temp"])\
    .rename(columns={"GEOID": "block_group_id"})


### RACE DF
df_race_raw = gpd\
    .read_file("./ACS_2021_5YR_BG_39_OHIO.gdb", layer = "X02_RACE")\
    .filter(items=["GEOID","B02001e1","B02001e2","B02001e3","B02001e4","B02001e5"])\
    .rename(columns={
                "GEOID": "temp",   
                "B02001e1": "total_pop",
                "B02001e2": "white_raw",
                "B02001e3": "black_raw",
                "B02001e4": "amerindian_raw",
                "B02001e5": "asian_raw"})\
    .assign(
        white_percent = lambda x: x.white_raw / x.total_pop,
        black_percent = lambda x: x.black_raw / x.total_pop,
        amerindian_percent = lambda x: x.amerindian_raw / x.total_pop,
        asian_percent = lambda x: x.asian_raw / x.total_pop)\
    .assign(GEOID = lambda x: x.temp.str.split("US").str.get(1))\
    .drop(columns=["temp"])

df_latino = gpd\
    .read_file("./ACS_2021_5YR_BG_39_OHIO.gdb", layer = "X03_HISPANIC_OR_LATINO_ORIGIN")\
    .filter(items=["GEOID","B03002e12"])\
    .rename(columns={
                "GEOID": "temp",   
                "B03002e12": "hispanic_raw"})\
    .assign(GEOID = lambda x: x.temp.str.split("US").str.get(1))\
    .drop(columns=["temp"])

race_bgs = df_race_raw\
    .merge(df_latino, on="GEOID", how="left")\
    .dropna()\
    .assign(
        hispanic_percent = lambda x: x.hispanic_raw / x.total_pop,
        nonwhite_percent = lambda x: 1 - x.white_percent)\
    .filter(items = ["GEOID","white_percent","black_percent","amerindian_percent","asian_percent","hispanic_percent","nonwhite_percent"])\
    .rename(columns={"GEOID": "block_group_id"})

###


## Bachelors
bachelors_bgs = gpd\
    .read_file("./ACS_2021_5YR_BG_39_OHIO.gdb", layer = "X15_EDUCATIONAL_ATTAINMENT")\
    .filter(items=["GEOID","C15010e1","C15010e3","C15010e4","C15010e5","C15010e6"])\
    .rename(columns={
                "GEOID": "temp",   
                "C15010e1": "num_bachelors",
                "C15010e3": "num_bachelors_stem",
                "C15010e4": "num_bachelors_business",
                "C15010e5": "num_bachelors_education",
                "C15010e6": "num_bachelors_arts"})\
    .assign(GEOID = lambda x: x.temp.str.split("US").str.get(1))\
    .drop(columns=["temp"])\
    .rename(columns={"GEOID": "block_group_id"})


## Veterans
veteran_bgs = gpd\
    .read_file("./ACS_2021_5YR_BG_39_OHIO.gdb", layer = "X21_VETERAN_STATUS")\
    .filter(items=["GEOID","B21001e1","B21001e2"])\
    .rename(columns={
                "GEOID": "temp",   
                "B21001e1": "total_civ",
                "B21001e2": "total_vet"})\
    .assign(GEOID = lambda x: x.temp.str.split("US").str.get(1))\
    .assign(percent_vet = lambda x: x.total_vet / x.total_civ)\
    .drop(columns=["temp","total_civ"])\
    .rename(columns={"GEOID": "block_group_id"})


## Voting
voting_bgs = gpd\
    .read_file("./ACS_2021_5YR_BG_39_OHIO.gdb", layer = "X29_VOTING_AGE_POPULATION")\
    .filter(items=["GEOID","B29001e1","B29001e2","B29001e3","B29001e4","B29001e5"])\
    .rename(columns={
                "GEOID": "temp",   
                "B29001e1": "total_civ",
                "B29001e2": "vote_18_29",
                "B29001e3": "vote_30_44",
                "B29001e4": "vote_45_64",
                "B29001e5": "vote_65"})\
    .assign(GEOID = lambda x: x.temp.str.split("US").str.get(1))\
    .assign(
        percent_vote_18_29 = lambda x: x.vote_18_29 / x.total_civ,
        percent_vote_30_44 = lambda x: x.vote_30_44 / x.total_civ,
        percent_vote_45_64 = lambda x: x.vote_45_64 / x.total_civ,
        percent_vote_65 = lambda x: x.vote_65 / x.total_civ)\
    .drop(columns=["temp","total_civ"])\
    .rename(columns={"GEOID": "block_group_id"})


## Fertility
fertility_ts = gpd\
    .read_file("./ACS_2021_5YR_TRACT_39_OHIO.gdb", layer = "X13_FERTILITY")\
    .filter(items=["GEOID","B13002e1","B13002e2"])\
    .rename(columns={
        "GEOID": "temp",
        "B13002e1":"total_women",
        "B13002e2":"women_births"})\
    .assign(GEOID = lambda x: x.temp.str.split("US").str.get(1))\
    .assign(
        pseudo_fertility_rate = lambda x: x.women_births/x.total_women)\
    .drop(columns=["temp"])\
    .rename(columns={"GEOID": "tract_id"})

sample = pd.read_csv("../sample.csv")
geometry = [Point(xy) for xy in zip(sample.longitude, sample.latitude)]

sample = (gpd.GeoDataFrame(sample, geometry=geometry)\
    .sjoin(gdf_bgs.drop(columns="COUNTYFP"), how="left", op="within")\
    # .assign(block_group_id = lambda x: x.block_group_id_right)\
    .drop(columns=["index_right"])\
    .sjoin(gdf_ts.drop(columns="COUNTYFP"), how="left", op="within")\
    # .assign(tract_id = lambda x: x.tract_id_right)\
    .drop(columns=["index_right"])\
    .sjoin(locale_gdf, how="left", op="within")\
    .drop(columns=["index_right"])\
    .assign(LOCALE = lambda x: x.LOCALE.astype(float))\
    .merge(income_bgs, how="left", on="block_group_id")\
    .merge(earnings_bgs, how="left", on="block_group_id")\
    .merge(employment_bgs, how="left", on="block_group_id")\
    .merge(poverty_bgs, how="left", on="block_group_id")\
    .merge(industry_bgs, how="left", on="block_group_id")\
    .merge(race_bgs, how="left", on="block_group_id")\
    .merge(bachelors_bgs, how="left", on="block_group_id")\
    .merge(veteran_bgs, how="left", on="block_group_id")\
    .merge(voting_bgs, how="left", on="block_group_id")\
    .merge(fertility_ts, how="left", on="tract_id")\
    .drop(columns=["geometry","match_type"])\
    .assign(date_of_birth=lambda x: pd.to_datetime(x['date_of_birth']),
            registration_date = lambda x: pd.to_datetime(x['registration_date']))\
    .assign(age=lambda x: (now.year - x['date_of_birth'].dt.year) - 
            ((now.month < x['date_of_birth'].dt.month) | 
             ((now.month == x['date_of_birth'].dt.month) & 
              (now.day < x['date_of_birth'].dt.day))))\
    .assign(years_since_registration=lambda x: (now.year - x['registration_date'].dt.year) - 
            ((now.month < x['registration_date'].dt.month) | 
             ((now.month == x['registration_date'].dt.month) & 
              (now.day < x['registration_date'].dt.day))))\
    .drop(columns=["date_of_birth","registration_date"])
)

suffix_mapping = {'JR': 'JR','SR': 'SR','III': 'numbers','II': 'numbers','IV': 'numbers','I': 'numbers','V': 'numbers'}

encoded_suffix = pd\
    .get_dummies(sample["suffix"].map(suffix_mapping).fillna(0), prefix="suffix")

sample = pd.concat(
        [sample.drop(columns='suffix'), 
         encoded_suffix],
    axis = 1
)

primaries_list = sample.loc[:,sample.columns.str.startswith("primary")].columns

list_dummy_primaries = []

for prim in primaries_list:
    dummies = pd.get_dummies(sample[prim], prefix=prim)
    list_dummy_primaries.append(dummies)

    primaries = pd.concat(list_dummy_primaries, axis=1)

sample = pd.concat(
    [sample.drop(columns = primaries_list),
     primaries.fillna(0)],
     axis = 1)

sample = sample.fillna(sample.mean())

sample = sample.loc[:,~sample.columns.str.startswith("special")]


X = sample\
        .select_dtypes(include = ["number"])\
        .drop(columns='sos_voter_id')

y = sample["party_affiliation"]=='R'




X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

clf = RandomForestClassifier(n_estimators=100, random_state=42)

clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)

m.accuracy_score(y_test, y_pred==1)
m.balanced_accuracy_score(y_test, y_pred==1)
m.f1_score(y_test, y_pred==1)

import plotly.express as px

features_df = pd.DataFrame({
    'Features': X.columns,
    'Importance': clf.feature_importances_
})

features_df = features_df.sort_values(by='Importance', ascending=False)

px.bar(features_df, x='Features', y='Importance', title='Feature Importances')

explainer = shap.TreeExplainer(clf)
shap_values = explainer.shap_values(X_test)

most_important_feature = X_test.columns[0] # You can change this to any feature of interest
shap.dependence_plot(most_important_feature, shap_values[1], X_test)


######
######
######

# X2 = sample\
#         .select_dtypes(include = ["number"])\
#         .drop(columns='sos_voter_id')

# X2 = X2.loc[:,~X2.columns.str.startswith("primary")]
# X2 = X2.loc[:,~X2.columns.str.startswith("general")]


# y2= sample["party_affiliation"]=='R'


# X_train2, X_test2, y_train2, y_test2 = train_test_split(X2, y2, test_size=0.3, random_state=42)

# clf2 = RandomForestClassifier()

# clf2.fit(X_train2, y_train2)

# y_pred2 = clf2.predict(X_test2)

# accuracy_score(y_test2, y_pred2)

# features_df2 = pd.DataFrame({
#     'Features': X2.columns,
#     'Importance': clf2.feature_importances_
# })

# features_df2 = features_df2.sort_values(by='Importance', ascending=False)

# px.bar(features_df2, x='Features', y='Importance', title='Feature Importances')

# explainer = shap.TreeExplainer(clf2)
# shap_values = explainer.shap_values(X)

# shap.summary_plot(shap_values[1], X)

# shap.force_plot(explainer.expected_value[1], shap_values[1][0,:], X.iloc[0,:])
