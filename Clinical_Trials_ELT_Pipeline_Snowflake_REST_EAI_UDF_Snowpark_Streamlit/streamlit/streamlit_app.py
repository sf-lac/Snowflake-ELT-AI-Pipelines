# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session

import streamlit as st
import plotly.express as px

# ❄️ Snowflake Streamlit session
session = get_active_session()

st.set_page_config(page_title="Blueprint of a Clinical Trial", layout="wide")
st.title("🧬 Blueprint of a Clinical Trial")

# ---------------------------
# 📥 Utility to load tables
# ---------------------------
@st.cache_data(show_spinner=False)
def load_table(name):
    return session.sql(f"SELECT * FROM {name}").to_pandas()

# ---------------------------
# 📦 Load Data
# ---------------------------
core = load_table("clinical_trial_core_normalized")
locations= load_table("clinical_trials_locations_normalized")
design = load_table("clinical_trial_design_normalized")
design_outcomes = load_table("clinical_trials_design_outcomes_normalized")
baseline = load_table("clinical_trials_baseline_measures_normalized")
outcomes = load_table("clinical_trials_outcome_measures_normalized")
adverse = load_table("clinical_trials_adverse_events_normalized")
limitations = load_table("clinical_trials_limitations_normalized")
documents = load_table("clinical_trials_documents_normalized")

# ---------------------------
# 🗂️ Tabs
# ---------------------------
tabs = st.tabs([
    "Overview", "Locations", "Design",
    "Outcomes", "Baseline", "Adverse Events",
    "Documents", "Limitations"
])

# ---------------------------
# 🧾 OVERVIEW
# ---------------------------
with tabs[0]:
    st.header("📄 Study Overview")
    if not core.empty:
        with st.expander("Study Metadata", expanded=True):
            st.markdown(f"**Study Identifier:** {core['NCT_ID'][0]}")
            st.markdown(f"**Brief Title:** {core['BRIEF_TITLE'][0]}")
            st.markdown(f"**Official Title:** {core['OFFICIAL_TITLE'][0]}")
            st.markdown("**Brief Summary:**")
            st.text_area("", core['BRIEF_SUMMARY'][0], height=200)
            st.markdown("**Detailed Description:**")
            st.text_area("", core['DETAILED_DESCRIPTION'][0], height=200)
        with st.expander("Conditions", expanded=True):
            st.markdown(f"**Conditions:** {core['CONDITIONS_SPECIFICS'][0]}")
        with st.expander("Status", expanded=True):
            st.markdown(f"**Overall Status:** {core['OVERALL_STATUS'][0]}")
            st.markdown(f"**Start Date:** {core['START_DATE'][0]}")
            st.markdown(f"**Completion Date:** {core['COMPLETION_DATE'][0]}")
        with st.expander("Sponsors & Collaborators", expanded=True):    
            st.markdown(f"**Principal Investigator:** {core['PRINCIPAL_INVESTIGATOR'][0]}")
            st.markdown(f"**Lead Sponsor:** {core['LEAD_SPONSOR'][0]}")
            st.markdown(f"**Collaborators:** {core['COLLABORATORS'][0]}")
        with st.expander("Full Study Table", expanded=True):
            st.dataframe(core)

# ---------------------------
# 📍 LOCATIONS
# ---------------------------
with tabs[1]:
    st.header("📍 Trial Locations")
    if {"LATITUDE", "LONGITUDE"}.issubset(locations.columns):
        st.map(locations[['LATITUDE', 'LONGITUDE']].dropna())

    with st.expander("Full Location Table", expanded=True):
        st.dataframe(locations)

# ---------------------------
# 🧬 DESIGN
# ---------------------------
with tabs[2]:
    st.header("🧬 Study Design")
    if not design.empty:
        with st.expander("Design Metadata", expanded=True):
            st.markdown(f"**Study Type:** {design['STUDY_TYPE'][0]}")
            st.markdown(f"**Phases:** {design['PHASES'][0]}")
            st.markdown(f"**Enrollment:** {design['ENROLLMENT_INFO'][0]}")
            st.markdown(f"**Primary Purpose:** {design['PRIMARY_PURPOSE'][0]}")
            st.markdown(f"**Masking:** {design['MASKING_INFO'][0]}")
            st.markdown(f"**Intervention Model:** {design['INTERVENTION_MODEL'][0]}")
        with st.expander("Interventions Details", expanded=True):
            st.markdown(f"**Intervention Type:** {design['INTERVENTION_TYPE'][0]}")
            st.markdown(f"**Intervention Name:** {design['INTERVENTION_NAME'][0]}")
            st.markdown(f"**Intervention Other Names:** {design['INTERVENTION_OTHER_NAMES'][0]}")
            st.markdown("**Intervention Description:**")
            st.text_area("", design['INTERVENTION_DESCRIPTION'][0], height=200)
        with st.expander("Eligibility Details", expanded=True):
            st.markdown(f"**Sex:** {design['SEX'][0]}")
            st.markdown(f"**Min Age:** {design['MIN_AGE'][0]}")
            st.markdown(f"**Max Age:** {design['MAX_AGE'][0]}")
            st.markdown(f"**Healthy Volunteers:** {design['HEALTHY_VOLUNTEERS'][0]}")
            st.markdown("**Eligibility Criteria:**")
            st.text_area("", design['ELIGIBILITY_CRITERIA'][0], height=200)
        with st.expander("Full Design Table", expanded=True):
            st.dataframe(design)
 

# ---------------------------
# 🎯 OUTCOMES
# ---------------------------
with tabs[3]:
    st.header("🎯 Outcome Measures")

    # Filter
    primary_df = outcomes[outcomes["OUTCOME_TYPE"] == "PRIMARY"]
    secondary_df = outcomes[outcomes["OUTCOME_TYPE"] == "SECONDARY"]

    # Drop duplicates
    secondary_df = secondary_df.drop_duplicates(
        subset=["OUTCOME_TITLE"])

    with st.expander("Primary Outcome Measures", expanded=True):
        primary_text = "—"
        if not primary_df.empty:
            primary_text = "\n\n".join([
                f"**{r['OUTCOME_TITLE']}** — {r['OUTCOME_DESCRIPTION']} ({r['TIME_FRAME']})"
                for _, r in primary_df.iterrows()
            ])
            st.markdown(primary_text)

    with st.expander("Secondary Outcome Measures", expanded=True):
        secondary_text = "—"
        if not secondary_df.empty:
            secondary_text = "\n\n".join([
                f"**{r['OUTCOME_TITLE']}** — {r['OUTCOME_DESCRIPTION']} ({r['TIME_FRAME']})"
                for _, r in secondary_df.iterrows()
            ])
            st.markdown(secondary_text)

    with st.expander("Statistics", expanded=True):
        if "OUTCOME_TYPE" in outcomes.columns:
            om_plot = outcomes.groupby("OUTCOME_TYPE").size().reset_index(name="count")
            fig_om = px.pie(om_plot, names="OUTCOME_TYPE", 
                            values="count", 
                            title="Outcome Measures Breakdown by Type")
            st.plotly_chart(fig_om)

        if "OUTCOME_TITLE" in outcomes.columns:
            om_plot = outcomes.groupby("OUTCOME_TITLE").size().reset_index(name="count")
            fig_om = px.pie(om_plot, names="OUTCOME_TITLE", 
                            values="count", 
                            title="Outcome Measures Breakdown by Title")
            st.plotly_chart(fig_om)

        if "CLASS_TITLE" in outcomes.columns and "MEASUREMENT_VALUE" in outcomes.columns and "OUTCOME_TITLE" in outcomes.columns:
            # Group by TYPE and CLASS, and sum participants
            chart_data = (
                outcomes.groupby(["OUTCOME_TITLE", "CLASS_TITLE"])["MEASUREMENT_VALUE"]
                .sum()
                .reset_index()
            )

            fig = px.bar(
                chart_data,
                x="CLASS_TITLE",
                y="MEASUREMENT_VALUE",
                color="OUTCOME_TITLE",
                title= "Outcomes by Type and Class",
                labels={"CLASS_TITLE":"CLASS", "OUTCOME_TITLE":"OUTCOME", "MEASUREMENT_VALUE": "PARTICIPANTS"},
            )

            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)        

    with st.expander("Search Outcomes", expanded=True):
        search = st.text_input("")
        filtered_outcomes = outcomes[outcomes.apply(lambda row: search.lower() in row.astype(str).str.lower().to_string(), axis=1)] if search else outcomes

    with st.expander("Outcome Measures Table", expanded=True):
        st.dataframe(filtered_outcomes)

# ---------------------------
# 👤 BASELINE CHARACTERISTICS
# ---------------------------
with tabs[4]:
    st.header("👤 Baseline Characteristics")

    with st.expander("Statistics", expanded=True):
        if "PARAM_TITLE" in baseline.columns:
            chart_data = baseline.groupby("PARAM_TITLE").size().reset_index(name="count")
            fig = px.bar(chart_data, x="PARAM_TITLE", y="count",
                         title="Baseline Measures per Type",
                         labels={"PARAM_TITLE":"MEASURE"},

                        )
            st.plotly_chart(fig, use_container_width=True) 

        if "CATEGORY_TITLE" in baseline.columns and "VALUE" in baseline.columns and "PARAM_TITLE" in baseline.columns:
            
            # Filter only Race data first
            race_df = baseline[baseline["PARAM_TITLE"] == "Race (NIH/OMB)"]
    
            # Group by TYPE and CATEGORY, and sum participants
            chart_data = (
                race_df.groupby(["PARAM_TITLE", "CATEGORY_TITLE"])["VALUE"]
                .sum()
                .reset_index()
            )

            fig = px.bar(
                chart_data,
                x="CATEGORY_TITLE",
                y="VALUE",
                title= "Baseline Measurements by Race",
                labels={"CATEGORY_TITLE":"RACE", "VALUE": "PARTICIPANTS"},
            )

            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("Baseline Measures Table", expanded=True):
        st.dataframe(baseline)
    

# ---------------------------
# ⚠️ ADVERSE EVENTS
# ---------------------------
with tabs[5]:
    st.header("⚠️ Adverse Events")

    with st.expander("Metadata", expanded=True):
            st.markdown("**Description:**")
            st.text_area("", adverse['ADVERSE_EVENT_DESCRIPTION'][0])
            st.markdown(f"**Time Frame:** {adverse['TIME_FRAME'][0]}")
            st.markdown(f"**Frequency:** {adverse['FREQUENCY_THRESHOLD'][0]}")
   
    with st.expander("Statistics", expanded=True):
        if "ADVERSE_EVENT_TYPE" in adverse.columns:
            ae_plot = adverse.groupby("ADVERSE_EVENT_TYPE").size().reset_index(name="count")
            fig_ae = px.pie(ae_plot, names="ADVERSE_EVENT_TYPE", values="count", title="Adverse Events Breakdown by Type")
            st.plotly_chart(fig_ae)

        if "ORGAN_SYSTEM" in adverse.columns:
            ae_plot = adverse.groupby("ORGAN_SYSTEM").size().reset_index(name="count")
            fig_ae = px.pie(ae_plot, names="ORGAN_SYSTEM", values="count", title="Adverse Events Breakdown by Organ System")
            st.plotly_chart(fig_ae)


        if "TERM" in adverse.columns and "AFFECTED_PARTICIPANTS" in adverse.columns and "ADVERSE_EVENT_TYPE" in adverse.columns:
            # Group by TYPE and TERM, and sum affected participants
            chart_data = (
                adverse.groupby(["ADVERSE_EVENT_TYPE", "TERM"])["AFFECTED_PARTICIPANTS"]
                .sum()
                .reset_index()
            )

            fig = px.bar(
                chart_data,
                x="TERM",
                y="AFFECTED_PARTICIPANTS",
                color="ADVERSE_EVENT_TYPE",
                title= "Affected Participants by Type and Term",
                labels={"AFFECTED_PARTICIPANTS": "PARTICIPANTS AFFECTED"},
            )

            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("Filter by Event Type", expanded=True):
        filter_type = st.selectbox("", options=["All"] + sorted(adverse["ADVERSE_EVENT_TYPE"].dropna().unique().tolist()))
        ae_filtered = adverse if filter_type == "All" else adverse[adverse["ADVERSE_EVENT_TYPE"] == filter_type]

    with st.expander("Adverse Event Table", expanded=True):
        st.dataframe(ae_filtered)

# ---------------------------
# 📄 DOCUMENTS
# ---------------------------
with tabs[6]:
    st.header("📄 Trial Documents")
    with st.expander("Documents Table", expanded=True):
        st.dataframe(documents)

# ---------------------------
# 🔍 Limitations
# ---------------------------
with tabs[7]:  
    st.header("📝 Limitations & Caveats")

    with st.expander("Limitations of study", expanded=True):
        st.markdown("**Description:**")
        st.text_area("", limitations['DESCRIPTION'][0], height=200)


