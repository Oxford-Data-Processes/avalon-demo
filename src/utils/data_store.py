import pandas as pd
from datetime import datetime
import uuid
import os
from models.data_models import RentalRequest, Bid

class CSVDataStore:
    def __init__(self):
        self.base_path = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.requests_file = os.path.join(self.base_path, 'rental_requests.csv')
        self.bids_file = os.path.join(self.base_path, 'bids.csv')
        self._initialize_files()

    def _initialize_files(self):
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
        
        # Initialize rental requests CSV
        if not os.path.exists(self.requests_file):
            pd.DataFrame(columns=[
                'id', 'location', 'make', 'model', 'transmission', 'fuel_type',
                'pickup_datetime', 'dropoff_datetime', 'status', 'selected_bid_id', 'created_at'
            ]).to_csv(self.requests_file, index=False)
        
        # Initialize bids CSV
        if not os.path.exists(self.bids_file):
            pd.DataFrame(columns=[
                'id', 'request_id', 'company_name', 'rep_name', 'price', 'created_at', 'notes'
            ]).to_csv(self.bids_file, index=False)

    def create_rental_request(self, request: RentalRequest) -> str:
        request.id = str(uuid.uuid4())
        request.created_at = datetime.now()
        
        df = pd.read_csv(self.requests_file)
        new_row = request.__dict__
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(self.requests_file, index=False)
        return request.id

    def get_rental_request(self, request_id: str) -> RentalRequest:
        df = pd.read_csv(self.requests_file)
        request_data = df[df['id'] == request_id].to_dict('records')
        return RentalRequest(**request_data[0]) if request_data else None

    def get_all_rental_requests(self) -> pd.DataFrame:
        return pd.read_csv(self.requests_file)

    def create_bid(self, bid: Bid) -> str:
        bid.id = str(uuid.uuid4())
        bid.created_at = datetime.now()
        
        df = pd.read_csv(self.bids_file)
        new_row = bid.__dict__
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(self.bids_file, index=False)
        return bid.id

    def get_bids_for_request(self, request_id: str) -> pd.DataFrame:
        df = pd.read_csv(self.bids_file)
        return df[df['request_id'] == request_id]

    def update_request_status(self, request_id: str, status: str, selected_bid_id: str = None):
        df = pd.read_csv(self.requests_file)
        df.loc[df['id'] == request_id, 'status'] = status
        if selected_bid_id:
            df.loc[df['id'] == request_id, 'selected_bid_id'] = selected_bid_id
        df.to_csv(self.requests_file, index=False)

    def get_all_bids(self) -> pd.DataFrame:
        return pd.read_csv(self.bids_file)

# Global instance
data_store = CSVDataStore() 