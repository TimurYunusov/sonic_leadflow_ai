import requests
import streamlit as st
import pandas as pd
import asyncio

# Import your actual pipeline entrypoint and AppState
from leadflow_ai.schemas.lead import AppState
from leadflow_ai.api.main import run_leadflow_pipeline  # You may need to adapt this import

st.set_page_config(page_title="LeadFlow AI - Business Scraper", layout="wide")
st.title("🚀 LeadFlow AI: Local Business Scraper & Analyzer")

st.sidebar.header("🔍 Search Configuration")
query = st.sidebar.text_input("Google Maps Search Query", value="technology companies in South Loop Chicago")
max_links = st.sidebar.number_input("Max Businesses", min_value=1, max_value=25, value=10)
run_pipeline = st.sidebar.button("Run LeadFlow Pipeline")

def call_api(query, max_links):
    url = "http://localhost:8000/run-leadflow-pipeline"
    payload = {
        "search_query": query,
        "max_links": int(max_links)
    }
    with st.spinner("⏳ Running pipeline…"):
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()["businesses"]

if run_pipeline:
    try:
        businesses = call_api(query, max_links)
        if not businesses:
            st.warning("No businesses found. Try another query!")
        else:
            df = pd.DataFrame([
                {
                    "Name": b["name"],
                    "Website": b["website"],
                    "Email": b["email"],
                    "Summary": b.get("summary", ""),
                    "Pain Points": b.get("pain_points", ""),
                    "Outreach Email": b.get("outreach_email", ""),
                    "Google Maps": b["url"]
                }
                for b in businesses
            ])
            st.success(f"Found {len(businesses)} businesses.")
            st.dataframe(df, use_container_width=True)
            st.download_button(
                label="Export to CSV",
                data=df.to_csv(index=False),
                file_name="leadflow_results.csv",
                mime="text/csv"
            )
            st.markdown("---")
            st.header("📄 Details for Each Business")
            for b in businesses:
                with st.expander(b["name"]):
                    st.markdown(f"**Website:** {b['website']}")
                    st.markdown(f"**Email:** {b['email']}")
                    st.markdown(f"**Summary:** {b.get('summary', '')}")
                    st.markdown(f"**Pain Points:** {b.get('pain_points', '')}")
                    st.markdown(f"**Outreach Email:**\n\n{b.get('outreach_email', '')}")
                    st.markdown(f"[View on Google Maps]({b['url']})")
    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Enter your search query and click 'Run LeadFlow Pipeline' to start.")