import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

API_USERNAME = os.getenv("DASHBOARD_USERNAME", "admin")
API_PASSWORD = os.getenv("DASHBOARD_PASSWORD", "secret")
API_URL = "http://localhost:8000/api/purchases"

# Page Configuration
st.set_page_config(page_title="Personal OS", page_icon="⚡", layout="wide")
st.title("⚡ Personal OS Dashboard")
st.markdown("---")

@st.cache_data(ttl=60)  # Caches data for 60 seconds so you don't spam Google APIs
def fetch_tracker_data():
    """Securely fetches data from the FastAPI backend."""
    try:
        response = requests.get(API_URL, auth=(API_USERNAME, API_PASSWORD))
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch data: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Connection error. Is the FastAPI backend running? Details: {e}")
        return None

# Fetch the data payload
data_payload = fetch_tracker_data()

if data_payload and data_payload.get("status") == "success":
    raw_data = data_payload.get("data", [])
    
    if len(raw_data) > 1:
        # Separate headers (row 1) from the actual entries (row 2 onward)
        headers = raw_data[1]
        rows = raw_data[2:]
        
        # Convert to a Pandas DataFrame for easy manipulation
        df = pd.DataFrame(rows, columns=headers)
        
        # UI: Top-level metrics
        st.subheader("Logistics & Purchases")
        col1, col2, col3 = st.columns(3)
        
        # Calculate some quick stats safely
        total_items = len(df)
        delayed = len(df[df['Status'].str.contains('Processing', case=False, na=False)])
        refunded = len(df[df['Status'].str.contains('Closed', case=False, na=False)])
        
        col1.metric("Total Tracked Items", total_items)
        col2.metric("Processing / Delayed", delayed)
        col3.metric("Closed / Refunded", refunded)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # UI: Interactive Data Table
        st.dataframe(
            df, 
            use_container_width=True, 
            hide_index=True
        )
    else:
        st.info("Connected to Google Sheets, but no data was found.")
else:
    st.warning("Awaiting connection to backend server...")
