# ⚕️💡✨🧠 End-to-End Data & AI Pipelines for Healthcare Data Processing and Analytics using Snowflake 

---

## ⚙️🛠️ Pipelines

- __`1.`__ **Health Research Agent** - an agentic AI application built on **Snowflake Cortex Agents** that synthesizes evidence from **clinical trial registries** and **peer-reviewed biomedical literature** to answer high-impact questions across the drug development lifecycle. Exposed through **Snowflake Intelligence UI**, the Cortex Agent leverages **Snowflake Cortex Knowledge Extensions** - shared **Marketplace Cortex Search Services** for __RAG__ reasoning.

- __`2.`__ End-to-End ELT data pipeline and analytics dashboard for ingestion, normalization, and exploration of semi-structured JSON data from clinicaltrials.gov via REST API making use of __Snowflake external access integration, Python-based UDF, Snowpark and Streamlit in Snowflake__.

- __`3.`__ End-to-End __ELT & AI pipeline for processing and analysis of semi-structured HL7 FHIR R4 JSON messages__ with __Snowflake Snowpark, Cortex Analyst and Streamlit in Snowflake__. A conversational Streamlit Chat App that calls Cortex Analyst REST API with a configured semantic model allows users to interact with HL7 FHIR R4 extracted resources that include patient information, medical encounters, conditions/diagnoses, medications and insurance claims using natural language question-asking. Cortex Analyst assists with both financial analysis of healthcare costs as well as clinical analysis of diagnoses, treatment and patient care patterns. Cortex Analyst generated queries are optimized and refactored into materialized views giving persistent, pre-aggregated data for fast downstream queries and read-heavy workloads.
 
- __`4.`__ End-to-End __ELT data pipeline__ for processing semi-structured HL7 __FHIR R4 JSON messages__ into a structured representation to facilitate __role-based data protection of sensitive information__, analysis and visualization with __SnowSQL CLI client, Snowflake SQL, functions, dynamic data masking and Streamlit in Snowflake notebook__.

- __`5.`__ End-to-end __Retrieval-Augmented Generation (RAG) pipeline in Snowflake using native Cortex AISQL functions__ to enable business users semantically search and extract health insurance-related answers from transcribed call center audio recordings via a Streamlit interface.

- __`6.`__ End-to-end __Medical Image Diagnosis pipeline using Cortex AISQL, Snowpark, and Streamlit__, leveraging LLMs for classification, explanation, and diagnosis.

---




