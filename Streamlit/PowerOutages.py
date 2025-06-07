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

pretab, posttab = st.tabs(["Pre", "Post"])

with pretab:
    question = st.text_input(
        "Question",
        value="Out of all the high risk regions in Louisiana, what is the capacity of shelters?",
    )
    fema_results = session.sql("""
        SELECT
            CASE WHEN STATE = 'Louisiana' THEN 'LA' ELSE 'MS' END AS STATE,
            COUNTY,
            BUILDVALUE,
            AGRIVALUE,
            AREA,
            HRCN_EVNTS,
            HRCN_AFREQ,
            HRCN_RISKV,
            HRCN_RISKS,
            HRCN_RISKR,
            SHAPE_LENGTH,
            SHAPE_AREA
        FROM DATAOPS_EVENT_PROD.HACKATHON_DATASETS.FEMA_CENSUS_TRACTS
        WHERE HRCN_RISKR ILIKE '%High%'
    """).limit(100).collect()
    fema_results_csv = '\n'.join([
       f"{fema_result['HRCN_EVNTS']},{fema_result['HRCN_AFREQ']}," for fema_result in fema_results
    ])
    res = session.sql(f"""
        select
            SNOWFLAKE.CORTEX.COMPLETE(
            'snowflake-arctic',
            'Answer this question: {question} with the following data: {fema_results_csv}'
        ) as answer
    """);
    if res:
        st.dataframe(res)

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

    hospital_points = session.sql("""
        SELECT *, longitude as lon, latitude as lat FROM DATAOPS_EVENT_PROD.HACKATHON_DATASETS.FACILITIES_CAPACITIES
        WHERE FACILITY_TYPE ILIKE 'HOSPITALS'
    """)
    hospital_pointspd = hospital_points.to_pandas()
    hopital_lat = hospital_points['LAT']
    hospital_lon = hospital_points['LON']
    hospital_points_layer = pdk.Layer(
        "ScatterplotLayer",
        hospital_pointspd,
        latitude=hopital_lat,
        longitude=hospital_lon,
        pickable=True,
        opacity=0.8,
        stroked=True,
        filled=True,
        radius_scale=3*hospital_points['CAPACITY_PROXY'],
        radius_min_pixels=1,
        radius_max_pixels=500,
        line_width_min_pixels=1,
        get_position=['LON','LAT'],
        get_radius=hospital_points['CAPACITY_PROXY'],
        get_fill_color=[0, 255, 0],
        get_line_color=[0, 255, 0],
    )

    nursing_points = session.sql("""
        SELECT *, longitude as lon, latitude as lat FROM DATAOPS_EVENT_PROD.HACKATHON_DATASETS.FACILITIES_CAPACITIES
        WHERE FACILITY_TYPE ILIKE 'NURSING HOMES'
    """)
    
    nursing_pointspd = nursing_points.to_pandas()
    nursing_lat = nursing_points['LAT']
    nursing_lon = nursing_points['LON']
    nursing_points_layer = pdk.Layer(
        "ScatterplotLayer",
        nursing_pointspd,
        latitude=nursing_lat,
        longitude=nursing_lon,
        pickable=True,
        opacity=0.8,
        stroked=True,
        filled=True,
        radius_scale=nursing_points['CAPACITY_PROXY'],
        radius_min_pixels=1,
        radius_max_pixels=100,
        line_width_min_pixels=1,
        get_position=['LON','LAT'],
        get_radius=nursing_points['CAPACITY_PROXY'],
        get_fill_color=[0, 0, 255],
        get_line_color=[0, 0, 255],
    )
    show_hurricane = st.checkbox('Hurricane Points', value=True)
    show_hospital = st.checkbox('Hospital', value=True)   
    show_nursing = st.checkbox('Nursing Homes', value=True)   
    
    map = pdk.Deck(
        initial_view_state=pdk.ViewState(
            latitude=LAT,
            longitude=LON,
            zoom=5,
            height=800,
        ),
        layers= [
            *([hurricane_points_layer] if show_hurricane else []),
            *([hospital_points_layer] if show_hospital else []),
            *([nursing_points_layer] if show_nursing else [])
        ],
        tooltip=tooltip,
        map_style=None,
    )
    st.pydeck_chart(map)

with posttab:
    service = st.selectbox(
        "label",
        options=["Hydro", "Medical", "Fire"],
        index=0,
        key=None,
        help=None,
        on_change=None,
        args=None,
        kwargs=None,
    )
    if service == "Hydro":
        st.text(f"{service} - Showing current power outages")
    if service == "Medical":
        st.text(f"{service} - Showing hospitals and nursing homes")
    if service == "Fire":
        st.text(f"{service} - Showing shelters")

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
    power_outagespd = session.table('hackathon_datasets.power_outage').drop("countyname", "lastupdateddatetime", "statename").to_pandas()
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
    
    # POWER OUTAGES

    # Hospitals
    power_heatmap = None
    if service == "Hydro":
        power_outages_augmented_pd = pd.merge(
            power_outagespd,
            df_coords,
            left_on="US_FULL_FIPS",
            right_on="FIPS_CODE",
            how="left"
        )
        power_outages_augmented_pd = power_outages_augmented_pd.dropna(subset=["LAT", "LNG"])
        power_outages_latitude = power_outages_augmented_pd["LAT"]
        power_outages_longitude = power_outages_augmented_pd["LNG"]
        power_heatmap = pdk.Layer(
            "HeatmapLayer",
            data=power_outages_augmented_pd,
            #latitude=power_outages_latitude,
            #longitude=power_outages_longitude,
            get_position='[lng,lat]',
            get_color='[41,181,232]',
            get_weight="PERCENTOUTAGE",
            radiusPixels=10,
            pickable=True,
        )
    hospital_points_layer = None
    if service == "Medical":
        hospital_points = session.sql("""
            SELECT *, longitude as lon, latitude as lat FROM DATAOPS_EVENT_PROD.HACKATHON_DATASETS.FACILITIES_CAPACITIES
            WHERE FACILITY_TYPE ILIKE 'HOSPITALS'
        """)
        hospital_pointspd = hospital_points.to_pandas()
        hopital_lat = hospital_points['LAT']
        hospital_lon = hospital_points['LON']
        hospital_points_layer = pdk.Layer(
            "ScatterplotLayer",
            hospital_pointspd,
            latitude=hopital_lat,
            longitude=hospital_lon,
            pickable=True,
            opacity=0.8,
            stroked=True,
            filled=True,
    
            radius_scale=hospital_points['CAPACITY_PROXY'],
            radius_min_pixels=1,
            radius_max_pixels=100,
            line_width_min_pixels=1,
            get_position=['LON','LAT'],
            get_radius="exits_radius",
            get_fill_color=[255, 140, 50],
            get_line_color=[0, 0, 0],
        )
    
    map = pdk.Deck(
        initial_view_state=pdk.ViewState(
            latitude=LAT,
            longitude=LON,
            zoom=5,
            height=800,
        ),
        layers= [
            hurricane_points_layer,
            *([power_heatmap] if power_heatmap else []),
            *([hospital_points_layer] if hospital_points_layer else []),
        ],
        tooltip=tooltip,
        map_style=None,
    )
    
    st.pydeck_chart(map)
