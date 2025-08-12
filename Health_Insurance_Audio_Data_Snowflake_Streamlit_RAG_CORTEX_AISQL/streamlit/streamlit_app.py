# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
import json

session = get_active_session()

st.set_page_config(page_title="📞 Health Insurance Call Center AI Assistant", layout="wide")

st.title("📞 Health Insurance Call Center AI Assistant")
st.markdown("Search and extract answers from transcribed audio recordings \
using **Snowflake Cortex AISQL functions**.")

#st.info("This app uses a Retrieval-Augmented Generation (RAG) pipeline inside Snowflake: "
#        "`SEARCH_PREVIEW()` → `EXTRACT_ANSWER()` → Precise answer from transcript.")

# User input
st.subheader("🔍 Ask a question")
st.info("""
Example questions:

- Was Lipitor covered under the plan?
- What resolution was offered to the customer? 
- What was the purpose of the call?
- What was the claim status?
""")
user_question = st.text_input("")

# Sidebar explaining the RAG pipeline
with st.sidebar:
    st.markdown("## 🧠 Behind the Scenes")    
    st.info("""
This app runs a **Retrieval-Augmented Generation (RAG)** workflow entirely within **Snowflake**, using native **AISQL functions** and **Streamlit**.

1. 🔍 **Retrieve**: `SNOWFLAKE.CORTEX.SEARCH_PREVIEW()` identifies the most relevant transcript chunks from indexed call recordings.  
2. 🧠 **Augment**: The retrieved chunks are embedded as context into a prompt alongside the user’s question.  
3. ✨ **Generate**: `SNOWFLAKE.CORTEX.EXTRACT_ANSWER()` produces a precise answer using the combined context and question.

All processing happens **natively inside Snowflake**, ensuring simplicity, scalability, and data security.
""")

# Run only if question provided
if user_question:  
    # JSON input for SEARCH_PREVIEW
    search_body = json.dumps({
        "query": user_question,
        "columns": ["CHUNK", "RELATIVE_PATH"],
        "limit": 2
    })

    # SQL query with parameterized question
    sql = f"""
    WITH preview AS (
      SELECT PARSE_JSON(
        SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
          'CALL_RECORDINGS_SEARCH',          
          '{search_body}'
        )
      )['results'] AS results
    ),
    flattened AS (
      SELECT 
        value:CHUNK::STRING AS chunk,
        value:RELATIVE_PATH::STRING AS file_name
      FROM preview,
      LATERAL FLATTEN(input => results)
    ),
    extracted AS (
      SELECT 
        file_name,
        chunk,
        SNOWFLAKE.CORTEX.EXTRACT_ANSWER(chunk, '{user_question}') AS extracted_answer
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
    SELECT * FROM answers
    ORDER BY confidence_score DESC;
    """

    # Run the query using Snowpark session
    
    df = session.sql(sql).to_pandas()        

    # RAG pipeline steps
    st.subheader("🧩 RAG Pipeline Execution")

    # Step 1: Semantic Search Input
    st.markdown("#### 1️⃣ Semantic Search Input")
    st.code(user_question, language='markdown')

    # Step 2: Search payload sent to SEARCH_PREVIEW and
    # the full SQL query executed to perform the RAG Pipeline
    st.markdown("#### 2️⃣ Search Payload and SQL Used")
    with st.expander("🔧 Cortex SEARCH_PREVIEW Payload"):
        st.json(json.loads(search_body))

    with st.expander("🧾 Full SQL Executed (RAG Pipeline)"):
        st.code(sql, language='sql')

    # Step 3: Results
    if df.empty:
        st.warning("❌ No relevant answers found.")
    else:
        st.markdown("#### 3️⃣ Top Matched Transcript Chunks + Generated Answers")
        for index, row in df.iterrows():
            st.markdown(f"**Match:** `{index + 1}`")
            st.markdown(f"**📁 File:** `{row['FILE_NAME']}`")
            st.markdown(f"**🧠 Extracted Answer:** {row['ANSWER']}")
            st.markdown(f"🔢 Confidence Score: `{round(row['CONFIDENCE_SCORE'], 3)}`")
            with st.expander("🗒️ Matched Transcript Chunk"):
                st.write(row['CHUNK'])
            st.divider()
    
  

    
    

