# ⚕️ Data Ingestion from clinicaltrials.gov REST API into Snowflake 

## ❄️ Overview

- The __`Ingest_JSON_from_REST_API.ipynb`__ notebook illustrates how to ingest semi-structured JSON data from [clinicaltrials.gov REST API](https://clinicaltrials.gov/api/v2/studies/NCT02953860) into a Snowflake table with two columns: 'study_id' to store the study identifier and 'study_data' to store raw clinical trial data as a VARIANT data type for further processing.

- The code includes:
  - Use of `Snowpark session` Python variables (e.g., role, database, schema) in SQL statements via Jinja syntax to set notebook's context,
  - DDL to create `NETWORK RULE` used to restrict access to the specific REST API endpoint (external network location), `EXTERNAL ACCESS INTEGRATION` that aggregates allowed network rules for use in UDFs and procedures, and Python-based `UDF` function to fetch data from the REST API endpoint.
  - DML to `insert` data `into` target table leveraging Snowflake built-in and UDF functions, and data type casting.
 






