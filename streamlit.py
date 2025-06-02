# Import python packages
import streamlit as st
import pandas as pd
import pydeck as pdk 
import json

from snowflake.snowpark.functions import *
from snowflake.snowpark.types import *
from snowflake.snowpark import Window

# We can also use Snowpark for our analyses!
from snowflake.snowpark.context import get_active_session

session = get_active_session()

st.title("Emergency Response")

tooltip = {
   "html": """<b>Name:</b> {NAME} <br> <b>USA Wind:</b> {USA_WIND} <br> <b>Hurricane Date:</b> {HURRICANE_DATE}""",
   "style": {
       "width":"50%",
        "backgroundColor": "steelblue",
        "color": "white",
       "text-wrap": "balance"
   }
}

service = st.selectbox(
    "label",
    options=["Hydro", "Ambulance"],
    index=0,
    key=None,
    help=None,
    on_change=None,
    args=None,
    kwargs=None,
)

st.text(service)

# Hurricanes
hurricane_points = session.table('hackathon_datasets.hurricane_points')
hurricane_pointspd = hurricane_points.to_pandas()
center = hurricane_points.agg(avg('LAT'),avg('LON'))

LAT = center.collect()[0][0]
LON = center.collect()[0][1]

hurricane_points_layer = pdk.Layer(
    'HeatmapLayer',
    data=hurricane_pointspd,
    get_position=['LON','LAT'],
    get_color='[41,181,232]',
    get_radius=10,
    pickable=True,
)

# Power outages
df_outage = session.table('hackathon_datasets.power_outage').drop("countyname", "lastupdateddatetime", "statename").to_pandas()
df_coords = session.table('hackathon_datasets.us_county_latlng').to_pandas()
#power_outagespd = (
#    power_outages
#    .join(
#        uslatlong,
#        on=uslatlong.fips_code == power_outages.us_full_fips,
#        how="left",
#    )
#    
#    .limit(10)
#    .to_pandas()
#)
#center = power_outages.agg(avg('lat'),avg('lon'))
##st.dataframe(center[0])
#
#power_outages_layer = pdk.Layer(
#    'HeatmapLayer',
#    data=power_outagespd,
#    get_position=['lng', 'lat'],
#    get_color='[41,181,232]',
#    get_radius=10,
#    pickable=True,
#)



# Adapter les noms de colonnes si besoin
# Par exemple, si les colonnes sont 'fips', 'lat', 'lng' :
# df_coords.rename(columns={"fips": "US_FULL_FIPS", "lat": "latitude", "lng": "longitude"}, inplace=True)

# Fusionner sur le code FIPS (adapte les noms de colonnes si besoin)
df = pd.merge(
    df_outage,
    df_coords,
    left_on="US_FULL_FIPS",
    right_on="FIPS_CODE",
    how="left"
)
df = df.dropna(subset=["LAT", "LNG"])

st.dataframe(df)

# Centrer la vue sur la moyenne des points
LAT = df["LAT"].mean()
LON = df["LNG"].mean()

# Définir le tooltip
tooltip = {
    "html": """<b>Comté:</b> {COUNTYNAME} <br> <b>Coupures:</b> {OUTAGECOUNT} <br> <b>%:</b> {PERCENTOUTAGE}""",
    "style": {
        "backgroundColor": "steelblue",
        "color": "white"
    }
}

# Créer la Heatmap
heatmap = pdk.Layer(
    "HeatmapLayer",
    data=df,
    get_position='[lng,lat]',
    get_color='[41,181,232]',
    get_weight="PERCENTOUTAGE",  # ou "PERCENTOUTAGE" pour la proportion
    radiusPixels=60,
    pickable=True,
)





map = pdk.Deck(
    initial_view_state=pdk.ViewState(
        latitude=LAT,
        longitude=LON,
        zoom=5,
        height=800,
    ),
    layers= [
        #hurricane_points_layer,
        heatmap,
    ],
    tooltip=tooltip,
    map_style=None,
)

st.pydeck_chart(map)
