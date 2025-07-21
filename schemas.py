# schemas.py

from pydantic import BaseModel
from datetime import date
from typing import Optional, Dict, List

# Pydantic model for creating a receipt (input)
class ReceiptBase(BaseModel):
    vendor: str
    amount: float
    date: date
    category: Optional[str] = None
    sub_categories: Dict[str, float] = {}

class ReceiptCreate(ReceiptBase):
    file_path: str

# Pydantic model for reading a receipt from the DB (output)
class Receipt(ReceiptBase):
    id: int
    file_path: str

    class Config:
        from_attributes = True

# Pydantic model for summary statistics
class SpendStats(BaseModel):
    total_spend: float
    mean_spend: float
    median_spend: float
    mode_spend: float
    
# MODIFIED: Renamed to VendorSpend and changed 'count' to 'total_spend'.
class VendorSpend(BaseModel):
    vendor: str
    total_spend: float

class MonthlySpend(BaseModel):
    month: str
    total_spend: float