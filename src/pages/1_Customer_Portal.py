import streamlit as st
from datetime import datetime, timedelta, time
from utils.data_store import data_store
from models.data_models import RentalRequest
import pandas as pd

# Constants
UK_AIRPORTS = [
    "London Heathrow (LHR)",
    "London Gatwick (LGW)",
    "Manchester (MAN)",
    "London Stansted (STN)",
    "London Luton (LTN)",
    "Edinburgh (EDI)",
    "Birmingham (BHX)",
    "Glasgow (GLA)",
    "Bristol (BRS)",
    "Newcastle (NCL)"
]

VEHICLE_OPTIONS = {
    "Audi": ["A1", "A3", "A4", "A6", "Q3", "Q5"],
    "BMW": ["1 Series", "3 Series", "5 Series", "X1", "X3", "X5"],
    "Ford": ["Fiesta", "Focus", "Kuga", "Puma"],
    "Mercedes": ["A-Class", "C-Class", "E-Class", "GLA", "GLC"],
    "Toyota": ["Yaris", "Corolla", "RAV4", "Prius"],
    "Volkswagen": ["Polo", "Golf", "Passat", "Tiguan", "T-Roc"]
}

def generate_time_slots():
    """Generate time slots in 30-minute increments"""
    slots = []
    for hour in range(0, 24):
        for minute in [0, 30]:
            slots.append(time(hour, minute))
    return slots

def get_default_time_index(time_slots):
    """Get the index of 10:00 in the time slots list"""
    return next(i for i, t in enumerate(time_slots) if t.hour == 10 and t.minute == 0)

def validate_dates(pickup, dropoff):
    now = datetime.now()
    min_duration = timedelta(hours=5)
    
    if pickup < now:
        return False, "Pickup time must be in the future"
    if dropoff <= pickup:
        return False, "Dropoff time must be after pickup time"
    if dropoff - pickup < min_duration:
        return False, "Minimum rental duration is 5 hours"
    return True, ""

def update_models():
    st.session_state.models = VEHICLE_OPTIONS[st.session_state.make]

st.title("Customer Portal")

tab1, tab2 = st.tabs(["Submit Request", "View Bids"])

with tab1:
    st.header("Submit Rental Request")
    
    # Initialize session state for make/model
    if 'make' not in st.session_state:
        st.session_state.make = list(VEHICLE_OPTIONS.keys())[0]
        st.session_state.models = VEHICLE_OPTIONS[st.session_state.make]
    
    # Vehicle selection outside the form
    col1, col2 = st.columns(2)
    with col1:
        make = st.selectbox(
            "Vehicle Make",
            list(VEHICLE_OPTIONS.keys())
        )
    with col2:
        model = st.selectbox(
            "Vehicle Model",
            options=VEHICLE_OPTIONS[make]
        )
    
    with st.form("rental_request_form"):
        # Location selection
        location = st.selectbox("Pickup Location", UK_AIRPORTS)
        
        # Transmission and fuel type
        transmission = st.selectbox("Transmission", ["Automatic", "Manual"])
        fuel_type = st.selectbox("Fuel Type", ["Petrol", "Diesel", "Electric", "Hybrid"])
        
        # Date and time selection
        tomorrow = datetime.now().date() + timedelta(days=1)
        
        col1, col2 = st.columns(2)
        with col1:
            pickup_date = st.date_input(
                "Pickup Date",
                min_value=tomorrow,
                value=tomorrow,
                max_value=tomorrow + timedelta(days=365)
            )
            
            time_slots = generate_time_slots()
            default_time_index = get_default_time_index(time_slots)
            
            pickup_time = st.selectbox(
                "Pickup Time",
                time_slots,
                index=default_time_index,
                format_func=lambda x: x.strftime("%H:%M")
            )
        
        with col2:
            default_dropoff = pickup_date + timedelta(days=3)
            dropoff_date = st.date_input(
                "Dropoff Date",
                min_value=pickup_date,
                value=default_dropoff,
                max_value=pickup_date + timedelta(days=365)
            )
            
            dropoff_time = st.selectbox(
                "Dropoff Time",
                time_slots,
                index=default_time_index,
                format_func=lambda x: x.strftime("%H:%M")
            )
        
        submit_button = st.form_submit_button("Submit Request")
        
        if submit_button:
            pickup_dt = datetime.combine(pickup_date, pickup_time)
            dropoff_dt = datetime.combine(dropoff_date, dropoff_time)
            
            is_valid, error_msg = validate_dates(pickup_dt, dropoff_dt)
            
            if is_valid:
                request = RentalRequest(
                    id="",
                    location=location,
                    make=make,
                    model=model,
                    transmission=transmission,
                    fuel_type=fuel_type,
                    pickup_datetime=pickup_dt,
                    dropoff_datetime=dropoff_dt
                )
                request_id = data_store.create_rental_request(request)
                st.success(f"Request submitted successfully! Your request ID is: {request_id}")
            else:
                st.error(error_msg)

with tab2:
    st.header("Your Recent Rental Requests")
    
    # Sidebar filters
    st.sidebar.header("Filter Requests")
    
    requests_df = data_store.get_all_rental_requests()
    
    if not requests_df.empty:
        # Get unique locations for filter
        locations = ["All Locations"] + sorted(requests_df['location'].unique().tolist())
        selected_location = st.sidebar.selectbox("Filter by Location", locations)
        
        # Sort requests by creation date, most recent first
        requests_df['created_at'] = pd.to_datetime(requests_df['created_at'])
        requests_df = requests_df.sort_values('created_at', ascending=False)
        
        # Apply location filter
        if selected_location != "All Locations":
            requests_df = requests_df[requests_df['location'] == selected_location]
        
        if not requests_df.empty:
            for _, request in requests_df.iterrows():
                with st.expander(
                    f"{request['make']} {request['model']} - {request['location']} "
                    f"({request['pickup_datetime']} to {request['dropoff_datetime']})"
                ):
                    st.write("Request Details:")
                    st.write(f"• Transmission: {request['transmission']}")
                    st.write(f"• Fuel Type: {request['fuel_type']}")
                    st.write(f"• Status: {request['status'].title()}")
                    
                    bids_df = data_store.get_bids_for_request(request['id'])
                    
                    if not bids_df.empty:
                        st.subheader("Bids Received")
                        
                        # Sorting options for bids
                        sort_by = st.selectbox(
                            "Sort bids by",
                            ["Price (Low to High)", "Price (High to Low)", "Most Recent"],
                            key=f"sort_{request['id']}"
                        )
                        
                        # Sort bids based on selection
                        if sort_by == "Price (Low to High)":
                            bids_df = bids_df.sort_values("price")
                        elif sort_by == "Price (High to Low)":
                            bids_df = bids_df.sort_values("price", ascending=False)
                        else:
                            bids_df = bids_df.sort_values("created_at", ascending=False)
                        
                        # Display bids in a clean table format
                        st.write("Available bids:")
                        
                        for _, bid in bids_df.iterrows():
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(
                                    f"**{bid['company_name']}** - £{bid['price']:.2f}\n\n"
                                    f"Representative: {bid['rep_name']}\n\n"
                                    f"Notes: {bid['notes'] if bid['notes'] else 'No additional notes'}"
                                )
                            with col2:
                                if request['status'] == 'pending':
                                    if st.button("Select Bid", key=f"select_{bid['id']}"):
                                        data_store.update_request_status(request['id'], "completed", bid['id'])
                                        st.success("Bid selected! Please contact the rental company to complete your booking.")
                                        st.rerun()
                                elif request['selected_bid_id'] == bid['id']:
                                    st.success("Selected Bid")
                        
                    else:
                        st.info("No bids received yet for this request.")
        else:
            st.info(f"No rental requests found for {selected_location}")
    else:
        st.info("You haven't made any rental requests yet.")