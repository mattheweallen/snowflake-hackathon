select * from DATAOPS_EVENT_PROD.HACKATHON_DATASETS.FACILITIES_CAPACITIES where facility_type ilike'Hospitals'

----------

Create or replace view DATAOPS_EVENT_PROD.HACKATHON_DATASETS.FACILITIES_CAPACITIES as
(Select NAME, 
       ADDRESS,
	   CITY,
	   STATE,
	   ZIP,
    STATUS,
     IFF(BEDS <0,0, BEDS) as Capacity_Proxy,
--    TOT_RES,
    COUNTY ,
	COUNTYFIPS,
	LATITUDE ,
	LONGITUDE,
    'Nursing Homes' as FACILITY_TYPE
from DATAOPS_EVENT_PROD.HACKATHON_DATASETS.NURSING_HOMES
where STATE in ('LA', 'MS') 

UNION

Select NAME, 
       ADDRESS,
	   CITY,
	   STATE,
	   ZIP,
    STATUS,
    IFF(BEDS <0,0, BEDS), 
    COUNTY ,
	COUNTYFIPS,
	LATITUDE ,
	LONGITUDE,
    'Hospitals' as FACILITY_TYPE
from DATAOPS_EVENT_PROD.HACKATHON_DATASETS.HOSPITAL_LOCATIONS
where STATE in ('LA', 'MS') 

UNION

Select NAME, 
       ADDRESS,
	   CITY,
	   STATE,
	   TRIM(ZIP,5),
    'NA',
   IFF(TOTALMLTRC <0,0, TOTALMLTRC) , 
    COUNTYNAME ,
	FIPS,
	LATITUDE ,
	LONGITUDE,
    'FQHC Sites' as FACILITY_TYPE
from DATAOPS_EVENT_PROD.HACKATHON_DATASETS.FQHC_SITES
where STATE in ('LA', 'MS') 

UNION

Select NAME, 
       ADDRESS,
	   CITY,
	   STATE,
	   trim(ZIP,5),
    STATUS,
    NULL,
    NULL ,
	NULL,
	Y, --LATITUDE ,
	X, --LONGITUDE,
    'Dialysis Centers' as FACILITY_TYPE
from DATAOPS_EVENT_PROD.HACKATHON_DATASETS.DIALYSIS_CENTERS
where STATE in ('LA', 'MS') 

UNION

Select SHELTER_NAME, 
       ADDRESS_1,
	   CITY,
	   STATE,
	   ZIP,
    SHELTER_STATUS_CODE,
    IFF(GENERAL_POPULATION < 0, 0, GENERAL_POPULATION), 
    COUNTY_PARISH ,
	FIPS_CODE,
	LATITUDE ,
	LONGITUDE,
    'Shelters' as FACILITY_TYPE
from DATAOPS_EVENT_PROD.HACKATHON_DATASETS.NATIONAL_SHELTER_FACILITIES
where STATE in ('LA', 'MS') 
)

----------
-- https://github.com/sfc-gh-mjohnson/summit-2025-hackathon

-- https://go.dataops.live/summit-hackathon-2025
-- https://app.dataops.live/artifacts/e0/32/e03261f846989d76ba100e2847d2d2730c8aafc9b974d69e06d46c0de3277d8b/2025_05_29/56575972/115614385/Homepage/dataops/event/homepage/site/index.html
