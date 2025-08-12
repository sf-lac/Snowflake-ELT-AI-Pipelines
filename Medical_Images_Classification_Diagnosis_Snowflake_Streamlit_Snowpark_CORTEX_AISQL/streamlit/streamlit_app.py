# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col, prompt, call_function

session = get_active_session()

st.set_page_config(page_title="🧠 Medical Image Classifier", layout="wide")

# Title and description
st.title("🧠 Medical Image Diagnosis AI Assistant")
st.markdown("Classify medical images and provide a concise medical diagnosis using **Snowflake Cortex `AI_CLASSIFY` and `AI_COMPLETE` AISQL functions**.")

# Step 1 - Upload or Select Image
st.markdown("### 1️⃣ Upload or Select Medical Image")

tab1, tab2 = st.tabs(["📁 Upload Image", "📦 Select from Stage"])

with tab1:
    uploaded_file = st.file_uploader("Upload JPEG image", type=["jpg", "jpeg"])
    if uploaded_file:
        st.image(uploaded_file)
        # Define the target stage and file path
        stage_name = "HC_AISQL_DB.HC_AISQL_SCHEMA.HC_AISQL_STAGE"  
        stage_folder = "MEDICAL_IMAGES"
        file_path_on_stage = f"@{stage_name}/{stage_folder}/{uploaded_file.name}"
        # Upload local file to stage 
        try:
            session.file.put_stream(uploaded_file, file_path_on_stage,
                             auto_compress=True, overwrite=True)
            st.success(f"File '{uploaded_file.name}' uploaded successfully to stage '{stage_name}' in the '{stage_folder}' folder.")
            st.info("Go to 'Select from Stage' tab. Select the uploaded image for AI classification and medical diagnosis")
        except Exception as e:
            st.error(f"Error uploading file: {e}")
       

with tab2:
    df = session.sql("""
        SELECT TO_FILE(FILE_URL) AS IMAGE_FILE,
        RELATIVE_PATH
        FROM DIRECTORY(@HC_AISQL_DB.HC_AISQL_SCHEMA.HC_AISQL_STAGE)
        WHERE RELATIVE_PATH LIKE 'MEDICAL_IMAGES/%'
        """)

    selected_path = st.selectbox("", df.select(col("RELATIVE_PATH")))
    
    image = session.file.get_stream("@HC_AISQL_DB.HC_AISQL_SCHEMA.HC_AISQL_STAGE/" + selected_path, decompress=False).read()
    st.image(image)

    # Step 2 - Classification Results
    st.markdown("### 2️⃣ AI Classification & Explanation using Cortex AISQL functions")

    # Run AI_CLASSIFY
    category_list = ['X-ray', 'CT', 'MRI', 'Ultrasound', 'PET', 'Other']
    classify_expr = call_function(
        "AI_CLASSIFY",
        prompt("Please classify this medical image {0}", col("IMAGE_FILE")),
        category_list
    )["labels"][0].cast("string").alias("classification")

    # Run AI_COMPLETE for explanation
    explanation_expr = call_function(
        "AI_COMPLETE",
        "claude-3-5-sonnet",
        prompt("Explain in one sentence why this is a valid classification for image {0}", col("IMAGE_FILE"))
    ).alias("explanation")

    result_df = (
        session.table("MEDICAL_IMAGES")
        .filter(col("RELATIVE_PATH") == selected_path)
        .select("RELATIVE_PATH", "IMAGE_FILE", classify_expr, explanation_expr)
        .to_pandas()
    )

    # Display results
    if not result_df.empty:
        st.markdown(f"🧪 **Prediction**: {result_df['CLASSIFICATION'].iloc[0]}")
        st.markdown(f"💬 **Explanation**: {result_df['EXPLANATION'].iloc[0]}")

        with st.expander("🔍 Full Output"):
            st.dataframe(result_df)
    else:
        st.warning("No prediction available.")

    # Step 3 - Diagnosis Results
    st.markdown("### 3️⃣ AI Diagnosis")

    # Run AI_COMPLETE to generate a diagnosis
    diagnosis_expr = call_function(
    "AI_COMPLETE",
    "claude-3-5-sonnet",
    prompt("Provide a concise medical diagnosis based on this image {0}.", col("IMAGE_FILE"))
    ).alias("final_diagnosis")

    # Run classification + explanation + diagnosis
    result_df = (
    session.table("MEDICAL_IMAGES")
    .filter(col("RELATIVE_PATH") == selected_path)
    .select("RELATIVE_PATH", "IMAGE_FILE", classify_expr, explanation_expr, diagnosis_expr)
    .to_pandas()
    )

    # Display results
    st.success(result_df['FINAL_DIAGNOSIS'][0])

    # Code
    st.markdown("### 🧾 AI Logic")
    
    with st.expander("🔍 View code"):
        st.code(
        '''
# Define category list for classification
category_list = ['X-ray', 'CT', 'MRI', 'Ultrasound', 'PET', 'Other']

# Run AI_CLASSIFY to predict category
classify_expr = call_function(
    "AI_CLASSIFY",
    prompt("Please classify this medical image {0}", col("IMAGE_FILE")),
    category_list
)["labels"][0].cast("string").alias("classification")

# Run AI_COMPLETE to generate an explanation
explanation_expr = call_function(
    "AI_COMPLETE",
    "claude-3-5-sonnet",
    prompt("Explain in one sentence why this is a valid classification for image {0}", col("IMAGE_FILE"))
).alias("explanation")

# Filter and execute query
result_df = (
    session.table("MEDICAL_IMAGES")
    .filter(col("RELATIVE_PATH") == selected_path)
    .select("RELATIVE_PATH", "IMAGE_FILE", classify_expr, explanation_expr)
    .to_pandas()
    )

# Run AI_COMPLETE to generate a diagnosis
diagnosis_expr = call_function(
    "AI_COMPLETE",
    "claude-3-5-sonnet",
    prompt("Provide a concise medical diagnosis based on this image {0}.", col("IMAGE_FILE"))
    ).alias("final_diagnosis")

    # Run classification + explanation + diagnosis
result_df = (
    session.table("MEDICAL_IMAGES")
    .filter(col("RELATIVE_PATH") == selected_path)
    .select("RELATIVE_PATH", "IMAGE_FILE", classify_expr, explanation_expr, diagnosis_expr)
    .to_pandas()
    )

        ''',
        language="python"
    )



