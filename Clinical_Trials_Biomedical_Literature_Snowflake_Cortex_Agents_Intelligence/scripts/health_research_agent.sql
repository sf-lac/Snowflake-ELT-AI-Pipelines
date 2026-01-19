USE ROLE accountadmin;

create database if not exists agentic_health_research_db;
create schema if not exists agents;
use database agentic_health_research_db;
use schema agents;

create or replace role agentic_health_research_role;

SET current_user_name = CURRENT_USER();    
    
GRANT ROLE agentic_health_research_role TO USER IDENTIFIER($current_user_name);
        
CREATE OR REPLACE WAREHOUSE agentic_health_research_wh 
    WITH WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE;

GRANT USAGE ON WAREHOUSE agentic_health_research_wh TO ROLE agentic_health_research_role;

ALTER USER IDENTIFIER($current_user_name) SET DEFAULT_ROLE = agentic_health_research_role;
ALTER USER IDENTIFIER($current_user_name) SET DEFAULT_WAREHOUSE = agentic_health_research_wh;
    
GRANT ALL PRIVILEGES ON DATABASE agentic_health_research_db TO ROLE agentic_health_research_role;
GRANT ALL PRIVILEGES ON SCHEMA agentic_health_research_db.agents TO ROLE agentic_health_research_role;

GRANT CREATE AGENT ON SCHEMA agentic_health_research_db.agents TO ROLE agentic_health_research_role;

GRANT USAGE ON CORTEX SEARCH SERVICE CLINICAL_TRIALS_RESEARCH_DATABASE.CT.CLINICAL_TRIALS_SEARCH_SERVICE
TO ROLE agentic_health_research_role;

GRANT USAGE ON CORTEX SEARCH SERVICE PUBMED_BIOMEDICAL_RESEARCH_CORPUS.OA_COMM.PUBMED_OA_CKE_SEARCH_SERVICE
TO ROLE agentic_health_research_role;

USE ROLE agentic_health_research_role;

CREATE OR REPLACE AGENT agentic_health_research_db.agents.health_research_agent
PROFILE = '{"display_name": "Health Research Agent"}'
COMMENT = 'This agent answers clinical development, biomedical research, regulatory,
commercialization, and patient-centric questions by synthesizing evidence from
clinical trial registries and peer-reviewed biomedical literature.'
FROM SPECIFICATION
$$
models:
  orchestration: claude-4-sonnet

instructions:
  response: |
    You are a healthcare and life sciences research assistant.
    Use clinical trial data for evidence on study design, endpoints,
    populations, and regulatory patterns.
    Use PubMed literature for mechanistic insights, biological validation,
    real-world outcomes, and emerging science.
    Always cite which source (clinical trials, PubMed, or both) informed the answer.
    Focus on strategic insights, not just summaries.

  orchestration: |
    When a question involves clinical outcomes, trial design,
    regulatory precedent, or competitive intelligence, prioritize the
    clinical_trials_search tool.
    When the question involves biological mechanisms, target validation,
    biomarkers, or translational evidence, prioritize the pubmed_search tool.
    Use both tools when strategic decisions require integrated clinical
    and scientific evidence.

  sample_questions:
    - question: "What are emerging drug prototypes for treating MYC-driven cancers?"
    - question: "What are the most common primary outcome measures used in trials for castration-resistant and neuroendocrine prostate cancers?"
    - question: "Is hnRNPA1 a validated drug target in cancer?"
    - question: "For MYC-driven solid tumors, which therapeutic mechanisms show the strongest translational support in PubMed, and how are those mechanisms reflected in current clinical trial endpoints and patient selection strategies?"
    - question: "What molecular targets are most frequently studied in neuroendocrine prostate cancer, and how do preclinical findings align with ongoing clinical trial designs?"
    - question: "Which therapeutic areas show high clinical trial activity but limited PubMed evidence, indicating potential commercialization risk or unmet validation gaps?"
    - question: "How do eligibility criteria and outcome measures in oncology trials align with real-world patient characteristics and biomarkers reported in PubMed literature?"
    - question: "What regulatory endpoint precedents exist for castration-resistant prostate cancer, and what supporting biological evidence is cited in the literature?"

tools:
  - tool_spec:
      type: cortex_search
      name: clinical_trials_search
      description: >
        Search clinical trial registry data to identify ongoing and completed trials,
        endpoints, patient populations, trial designs, regulatory patterns,
        and competitive intelligence across the drug development lifecycle.

  - tool_spec:
      type: cortex_search
      name: pubmed_search
      description: >
        Search PubMed biomedical literature for mechanistic insights,
        target validation, translational evidence, biomarkers,
        and emerging scientific trends.

tool_resources:
  clinical_trials_search:
    name: CLINICAL_TRIALS_RESEARCH_DATABASE.CT.CLINICAL_TRIALS_SEARCH_SERVICE
    max_results: 10

  pubmed_search:
    name: PUBMED_BIOMEDICAL_RESEARCH_CORPUS.OA_COMM.PUBMED_OA_CKE_SEARCH_SERVICE
    max_results: 10
$$;

GRANT MONITOR ON AGENT agentic_health_research_db.agents.health_research_agent TO ROLE agentic_health_research_role;




