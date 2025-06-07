// Identify buildings higher than 20m
SELECT * FROM CARTO.BUILDING
WHERE height > '20';

// Identify buildings with solar panels in the roof
SELECT * FROM CARTO.BUILDING
WHERE roof_material = 'solar_panels';

//FIPS
select count(*) from POWER_OUTAGE
--62587

SELECT
  count(*)
FROM
  "DATAOPS_EVENT_PROD"."HACKATHON_DATASETS"."US_COUNTY_LATLNG" fips, "DATAOPS_EVENT_PROD"."HACKATHON_DATASETS".POWER_OUTAGE po
WHERE fips.fips_code = po.US_FULL_FIPS --and NAME != COUNTYNAME

--57011