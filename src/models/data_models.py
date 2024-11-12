from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class RentalRequest:
    id: str
    location: str
    make: str
    model: str
    transmission: str
    fuel_type: str
    pickup_datetime: datetime
    dropoff_datetime: datetime
    status: str = "pending"
    selected_bid_id: Optional[str] = None
    created_at: datetime = datetime.now()

@dataclass
class Bid:
    id: str
    request_id: str
    company_name: str
    rep_name: str
    price: float
    created_at: datetime
    notes: Optional[str] = None
