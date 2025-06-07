-- alter session set geography_output_format = 'GEOJSON';

-- https://api.census.gov/data/2019/acs/acs5/groups/B19049.html
select * from acs_hh_median_income_tracts limit 100;
select * from acs_population_tracts limit 100;
select * from acs_poverty_status_tracts limit 100;
select * from acs_race_hispanic_origin_tracts limit 100;
select * from acs_vehicle_availability_tracts limit 100;
select * from county_health_rankings_2024 limit 100;
select * from dialysis_centers limit 100;
select * from fema_census_tracts limit 100;
select * from fqhc_sites limit 100;
select * from hospital_locations limit 100;
select * from hurricane_points;
select * from hurricane_tracks;
select * from hurricane_trajectory;
select distinct(activity_date) from mapbox_activity order by ;
select * from national_risk_index_counties limit 100;
select * from national_risk_index_tracts limit 100;
select * from national_shelter_facilities limit 100;
select * from nursing_homes limit 100;
select * from population_census_block limit 100;
select * from power_outage limit 100;
select * from social_vulnerability_index limit 100;
select * from wind_swathe limit 100;


-- Overture
select * from overture_maps__buildings.carto.building limit 100;
select * from overture_maps__buildings.carto.building_part limit 100;

select * from mapbox_activity limit 100;

select max(activity_index_total) from mapbox_activity;

