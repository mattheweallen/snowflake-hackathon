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

tooltip = {
   "html": """<b>Name:</b> {NAME} <br> <b>USA Wind:</b> {USA_WIND} <br> <b>Hurricane Date:</b> {HURRICANE_DATE}""",
   "style": {
       "width":"50%",
        "backgroundColor": "steelblue",
        "color": "white",
       "text-wrap": "balance"
   }
}

hurricane_points = session.table('HACKATHON_DATASETS.HURRICANE_POINTS')

hurricane_pointspd = hurricane_points.to_pandas()
center = hurricane_points.agg(avg('LAT'),avg('LON'))

LAT = center.collect()[0][0]
LON = center.collect()[0][1]


h_points = pdk.Layer(
    'HeatmapLayer',
    data=hurricane_pointspd,
    get_position=['LON','LAT'],
    get_color='[41,181,232]',
    get_radius=10,
    pickable=True,
)

map = pdk.Deck(
    initial_view_state=pdk.ViewState(
        latitude=LAT,
        longitude=LON,
        zoom=5,
        height=800,
    ),
    layers= [h_points],tooltip=tooltip,
    map_style=None
)

st.pydeck_chart(map)
