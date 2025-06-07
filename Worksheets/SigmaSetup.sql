-- https://quickstarts.sigmacomputing.com/guide/partner_snowflake_summit_hackathon_2024/index.html?index=..%2F..index#2

-- Use the appropriate warehouse
USE WAREHOUSE PC_SIGMA_WH;

-- Switch to using the Sigma database
USE DATABASE PC_SIGMA_DB;

-- Create the WRITE schema within the Sigma database
CREATE SCHEMA WRITE;

-- Grant usage on the database to the ACCOUNTADMIN role
GRANT USAGE ON DATABASE PC_SIGMA_DB TO ROLE ACCOUNTADMIN;

-- Grant various permissions on the WRITE schema to the ACCOUNTADMIN role
GRANT USAGE, 
      CREATE TABLE, 
      CREATE VIEW, 
      CREATE STAGE 
ON SCHEMA WRITE 
TO ROLE ACCOUNTADMIN;