#%%
import pandas as pd
voters = pd.read_parquet('../SWVF_full.parquet')
# %%
voters = voters[voters['latitude'].notna()]
#%%
import folium
from folium.plugins import MarkerCluster
from folium.plugins import TagFilterButton

DISPLAY_NUMBER = 1000
ohio = [40.229851,-82.531116]
my_map = folium.Map(location = ohio, zoom_start = 6,tiles='stamentoner')
display = voters.sample(n=DISPLAY_NUMBER)
for i in range(DISPLAY_NUMBER):
    folium.Marker([display.iloc[i].latitude,display.iloc[i].longitude],
                  popup=display.iloc[i].sos_voter_id,
                  tags=[display.iloc[i].party_affiliation]
                  ).add_to(my_map)
    
TagFilterButton(display.party_affiliation.unique()).add_to(my_map)

#Display the map
my_map
# %%
voters