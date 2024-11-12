import streamlit as st
from datetime import datetime
from utils.data_store import data_store
from models.data_models import Bid
import pandas as pd

# Company constants
COMPANY_NAME = "Green Motion"

st.title("Rental Company Portal")
st.subheader(f"Company: {COMPANY_NAME}")

# Filter options in sidebar
st.sidebar.header("Filters")

# Status filter
status_filter = st.sidebar.multiselect(
    "Status",
    ["pending", "completed"],
    default=["pending"]
)

# Get all requests
requests_df = data_store.get_all_rental_requests()

if not requests_df.empty:
    # Location filter
    locations = ["All Locations"] + sorted(requests_df['location'].unique().tolist())
    selected_location = st.sidebar.selectbox("Location", locations)
    
    # Apply filters
    filtered_requests = requests_df[requests_df['status'].isin(status_filter)]
    if selected_location != "All Locations":
        filtered_requests = filtered_requests[filtered_requests['location'] == selected_location]
    
    # Sort by most recent first
    filtered_requests['created_at'] = pd.to_datetime(filtered_requests['created_at'])
    filtered_requests = filtered_requests.sort_values('created_at', ascending=False)

    if not filtered_requests.empty:
        # Display count of filtered requests
        st.write(f"Showing {len(filtered_requests)} rental requests")
        
        for _, request in filtered_requests.iterrows():
            with st.expander(
                f"{request['location']} - {request['make']} {request['model']} "
                f"({request['pickup_datetime']} to {request['dropoff_datetime']})"
            ):
                # Request details
                st.write("### Request Details")
                col1, col2 = st.columns(2)
                with col1:
                    st.write("📍 Location:", request['location'])
                    st.write("🚗 Vehicle:", f"{request['make']} {request['model']}")
                    st.write("⚙️ Transmission:", request['transmission'])
                with col2:
                    st.write("⛽ Fuel Type:", request['fuel_type'])
                    st.write("📅 Pickup:", request['pickup_datetime'])
                    st.write("📅 Dropoff:", request['dropoff_datetime'])
                
                # Show existing bids for this request
                existing_bids = data_store.get_bids_for_request(request['id'])
                if not existing_bids.empty:
                    st.write("### Existing Bids")
                    for _, bid in existing_bids.iterrows():
                        st.write(f"• {bid['company_name']} - £{bid['price']:.2f}")
                
                # Bid form
                if request['status'] == 'pending':
                    st.write("### Submit New Bid")
                    with st.form(f"bid_form_{request['id']}"):
                        rep_name = st.text_input("Representative Name")
                        price = st.number_input("Bid Amount (£)", min_value=0.0, step=0.01)
                        notes = st.text_area("Notes (optional)")
                        
                        if st.form_submit_button("Submit Bid"):
                            bid = Bid(
                                id="",
                                request_id=request['id'],
                                company_name=COMPANY_NAME,
                                rep_name=rep_name,
                                price=price,
                                created_at=datetime.now(),
                                notes=notes
                            )
                            bid_id = data_store.create_bid(bid)
                            st.success("Bid submitted successfully!")
                            st.rerun()
                else:
                    st.write("🔒 This request has been completed")
                    if not existing_bids.empty:
                        winning_bid = existing_bids[existing_bids['id'] == request['selected_bid_id']]
                        if not winning_bid.empty:
                            st.success(f"Won by: {winning_bid.iloc[0]['company_name']} - £{winning_bid.iloc[0]['price']:.2f}")
    else:
        st.info("No rental requests found matching your filters.")
else:
    st.info("No rental requests available.")

# Add a refresh button at the bottom of the page
if st.button("Refresh Requests"):
    st.rerun() 