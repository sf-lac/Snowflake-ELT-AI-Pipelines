# ⚕️💡✨🧠 End-to-End Data & AI Pipeline for Processing and Analyzing HL7 FHIR R4 JSON Messages with Snowpark, Cortex Analyst and Streamlit in Snowflake

---

## ❄️ Overview

This project illustrates how to:
- Process semi-structured FHIR component resouces that make up an exchangable patient record into a structured representation using Snowpark APIs. 
- Construct and refine a semantic model that captures relationships between harmonized resources to help Cortex Analyst understand the specifics of FHIR data (e.g. PATIENTS, ENCOUNTERS, CLAIMS, CONDITIONS, MEDICATIONS).
- Create a Streamlit Chat App to call Cortex Analyst REST API with the configured semantic model to allow users to interact with HL7 FHIR data using natural language question-asking.
- Optimize slow performant Cortex Analyst generated queries to increase efficiency (e.g. 120X performace gain).
- Refactor queries into Snowflake materialized views to optimize compute resource usage and significantly boost query performance giving persistent, pre-aggregated data for fast downstream queries and read-heavy workloads.
- Add index clustering to speed up point lookups or filters.

---

## 💡✨🧠 Analytics

- 📊 Clinical Utilization & Care Pathways
- 💰 Claims and Financial Insights
- 📈 Quality & Outcomes
- 🧩 Patient Journey Mapping

---

## 📂 Project structure
<pre>
├── notebooks/
│ ├── FHIR_NB.ipynb # Data & AI Pipeline Snowflake notebook
├── scripts/
│ ├── FHIR_Setup.sql # Snowflake SQL Worksheet to create database, schema, warehouse, and notebook
├── semantic_model/
│ ├── hl7_fhir_r4_semantic_model.yaml # Staged .yaml file for the Semantic Model over healthcare data constructed using Cortex Analyst guided setup, then manually refined
├── streamlit/
│ ├── streamlit_app.py # Streamlit Cortex Analyst Conversational App text-to-SQL Q&A
│ ├── environment.yml 
├── README.md
</pre>

---




