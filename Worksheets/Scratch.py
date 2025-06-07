# The Snowpark package is required for Python Worksheets. 
# You can add more packages by selecting them using the Packages control and then importing them.

import snowflake.snowpark as snowpark
from snowflake.snowpark.functions import col

def main(session: snowpark.Session): 
    power_outages = session.table('hackathon_datasets.power_outage')
    uslatlong = session.table('HACKATHON_DATASETS.US_COUNTY_LATLNG')
    power_outagespd = (
        power_outages
        .join(
            uslatlong,
            on=uslatlong.fips_code == power_outages.us_full_fips,
            how="left",
        )
        .drop("countyname", "lastupdateddatetime", "statename")
    )
    return power_outagespd