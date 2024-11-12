import streamlit as st
import os
from utils.data_store import data_store

st.title("Admin Portal")

st.warning("⚠️ Warning: These actions cannot be undone!")

col1, col2 = st.columns(2)

with col1:
    st.header("Clear All Data")
    if st.button("Clear All Data"):
        # Clear rental requests
        if os.path.exists(data_store.requests_file):
            os.remove(data_store.requests_file)
        
        # Clear bids
        if os.path.exists(data_store.bids_file):
            os.remove(data_store.bids_file)
            
        # Reinitialize empty files
        data_store._initialize_files()
        
        st.success("All data has been cleared!")

with col2:
    st.header("View Current Data")
    
    if st.button("Show Rental Requests"):
        requests_df = data_store.get_all_rental_requests()
        if not requests_df.empty:
            st.dataframe(requests_df)
        else:
            st.info("No rental requests found")
    
    if st.button("Show Bids"):
        bids_df = data_store.get_all_bids()  # We need to add this method 