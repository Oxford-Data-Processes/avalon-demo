import streamlit as st

st.set_page_config(
    page_title="Car Rental Bidding Platform",
    page_icon="🚗",
    layout="wide"
)

st.title("Welcome to Car Rental Bidding Platform")
st.write("""
This platform allows customers to request car rentals and receive competitive bids from rental companies.

### How it works:
1. Customers submit their rental requirements
2. Rental companies review requests and submit their bids
3. Customers can view and select from available bids

Use the sidebar to navigate between the Customer Portal and Rental Company Portal.
""") 