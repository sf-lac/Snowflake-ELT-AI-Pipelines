# ⚕️ ELT Data Pipeline for processing HL7 FHIR R4 JSON messages with Snowflake SQL and functions, Snowflake Dynamic Data Masking and Streamlit in Snowflake

This project illustrates how to process semi-structured FHIR component resouces that make up an exchangable patient record into a structured representation to facilitate role-based data protection of sensitive information, data analysis and visualization with Snowflake.

---

## ❄️ Overview

- **Setup**: The __`FHIR_Setup.sql`__ Snowflake SQL Worksheet creates database, schema, warehouse, and notebook __`FHIR_NB.ipynb`__ to run the pipeline.
- **Ingest**: Stage FHIR JSON data files from local file system by executing 'PUT' command using SnowSQL client.
- **Load**: Create target patient table with a single VARIANT column, a file format and copy into the table the raw JSON messages.
- **Transform**: Create views for querying data flattened to a tabular format. Leverage dynamic data masking to protect PII or HIPAA individual or health-related data based on functional roles. Create and apply column-level masking policies in the views to selectively mask plain-text data at query time.
- **Visualize**: Create analytical queries on the joined views and plot their results using Pandas and Streamlit within the Snowflake notebook.

---




