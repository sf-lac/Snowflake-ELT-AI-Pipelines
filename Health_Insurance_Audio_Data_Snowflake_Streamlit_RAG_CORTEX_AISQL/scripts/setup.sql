USE ROLE ACCOUNTADMIN;
CREATE OR REPLACE WAREHOUSE HC_AISQL_WH;
CREATE OR REPLACE DATABASE HC_AISQL_DB;
CREATE OR REPLACE SCHEMA HC_AISQL_DB.HC_AISQL_SCHEMA;

USE WAREHOUSE HC_AISQL_WH;
USE DATABASE HC_AISQL_DB;
USE SCHEMA HC_AISQL_SCHEMA;

CREATE STAGE HC_AISQL_STAGE 
	DIRECTORY = ( ENABLE = true ) 
	ENCRYPTION = ( TYPE = 'SNOWFLAKE_SSE' );

-- Load files into the stage via Snowsight UI

-- List files in the stage
SELECT * FROM DIRECTORY(@HC_AISQL_DB.HC_AISQL_SCHEMA.HC_AISQL_STAGE);

-- Load call recording(audio/mpeg files) directly from stage using FILE data type
CREATE OR REPLACE TABLE HC_AISQL_DB.HC_AISQL_SCHEMA.CALL_RECORDINGS AS
SELECT TO_FILE(FILE_URL) AUDIO_FILE, *
FROM DIRECTORY(@HC_AISQL_DB.HC_AISQL_SCHEMA.HC_AISQL_STAGE)
WHERE RELATIVE_PATH LIKE 'CALL_RECORDINGS/%';

SELECT * FROM HC_AISQL_DB.HC_AISQL_SCHEMA.CALL_RECORDINGS;

ALTER TABLE CALL_RECORDINGS ADD COLUMN CALL_TRANSCRIPT STRING;

UPDATE CALL_RECORDINGS 
SET CALL_TRANSCRIPT = AI_TRANSCRIBE(AUDIO_FILE):text::STRING;

ALTER TABLE CALL_RECORDINGS ADD COLUMN AI_CALL_REASON STRING;

UPDATE CALL_RECORDINGS 
SET AI_CALL_REASON = AI_CLASSIFY(CALL_TRANSCRIPT, ['claims related', 'coverage related', 
'billing related','other']):labels[0]::text;

DESCRIBE TABLE CALL_RECORDINGS;

SELECT * FROM CALL_RECORDINGS;

-- Create table to store extracted insights
CREATE OR REPLACE TABLE CALL_INSIGHTS (
  AUDIO_FILE_NAME TEXT,
  CUSTOMER_NAME arraY,
  MEMBER_ID ARRAY,
  INQUIRY_TYPE ARRAY,
  RESOLUTION ARRAY
);

-- Insert structured insights from all transcripts into reporting table
INSERT INTO CALL_INSIGHTS
SELECT
  REGEXP_SUBSTR(FL_GET_RELATIVE_PATH(AUDIO_FILE), '[^/]+$') AS AUDIO_FILE_NAME,
  SNOWFLAKE.CORTEX.EXTRACT_ANSWER(CALL_TRANSCRIPT, 'What is the customer''s name?') AS CUSTOMER_NAME,
  SNOWFLAKE.CORTEX.EXTRACT_ANSWER(CALL_TRANSCRIPT, 'What is the member ID?') AS MEMBER_ID,
  SNOWFLAKE.CORTEX.EXTRACT_ANSWER(CALL_TRANSCRIPT, 'What is the purpose of the call?') AS INQUIRY_TYPE,
  SNOWFLAKE.CORTEX.EXTRACT_ANSWER(CALL_TRANSCRIPT, 'What resolution was offered to the customer?') AS RESOLUTION,
FROM CALL_RECORDINGS;

SELECT * FROM CALL_INSIGHTS;

/* 
Create Cortex Search Service
- the semantic search engine in Snowflake that uses vector embeddings + indexed retrieval, used here to find relevant transcrips for a natural language query.
- provides automated embedding - text-to-vector conversion - using a powerful pre-trained LLM embedding model that captures the semantic meaning of a transcript chunk for matching the query,
- also provides indexing embeddings for fast semantic search and retrieval.
- given trascript chunks as input data, computes embeddings, and builds an internal vector index. 
- when a user submits a semantic query, its embedding is compared to the index - by Snowflake - to find the closest matches.
*/
CREATE OR REPLACE CORTEX SEARCH SERVICE CALL_RECORDINGS_SEARCH
ON CHUNK -- the column searched for matches when the service is queried
ATTRIBUTES RELATIVE_PATH -- available as filter column when chunk column is searched 
WAREHOUSE = HC_AISQL_WH -- warehouse to materialize results initially and when source table changes
TARGET_LAG = '1 hour' -- automatic re-indexing to reflect the latest data in the source table
AS (
  SELECT    
    REGEXP_SUBSTR(RELATIVE_PATH, '[^/]+$') AS RELATIVE_PATH,
    'Audio File Name: ' || RELATIVE_PATH || ': Transcript - ' || CALL_TRANSCRIPT AS CHUNK
  FROM CALL_RECORDINGS
);

/*
Semantic retrieval with Cortex Search Service
- The Cortex Search Service is used as a RAG engine for a chat app with the transcript data as a knowledge base. 
- Cortex Search retrieval engine is combined with Cortex AISQL functions to leverage semantic search and provide the context needed to return augmented, customized, contextualized answers grounded in the most-up-to-date data.
*/
WITH preview AS (
   SELECT PARSE_JSON(
    SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
      'CALL_RECORDINGS_SEARCH',
      '{
        "query": "Was Lipitor covered under the plan?",      
        "columns": ["CHUNK", "RELATIVE_PATH"],
        "limit": 3
      }'
    )
  )['results'] AS results
),
flattened AS (
  SELECT 
    value:CHUNK::STRING AS chunk,
    value:RELATIVE_PATH::STRING AS file_name,
  FROM preview,
  LATERAL FLATTEN(input => results)
),
extracted AS (
SELECT 
  file_name,  
  chunk,
  SNOWFLAKE.CORTEX.EXTRACT_ANSWER(chunk, 'Was Lipitor covered under the plan?') AS extracted_answer
FROM flattened
), 
answers AS (
SELECT
  file_name,
  chunk,
  value:answer::STRING AS answer,
  value:score::FLOAT AS confidence_score
FROM extracted,
LATERAL FLATTEN(input => extracted_answer)
)
SELECT *
FROM answers
ORDER BY confidence_score DESC;

/*
Note: Use Python API for Cortex Search Service in production applications
as SEARCH_PREVIEW is not intended for serving low-latency search queries in production
See https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search/cortex-search-overview
for an example of using Python API to query the service
*/

