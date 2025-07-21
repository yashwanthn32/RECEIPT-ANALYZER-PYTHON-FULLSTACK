# models.py

from sqlalchemy import Column, Integer, String, Float, Date, JSON
from .database import Base

class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    vendor = Column(String, index=True)
    date = Column(Date, index=True)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=True)
    # ADDED: A JSON field to store the list of all found categories.
    sub_categories = Column(JSON, nullable=True)
    file_path = Column(String, unique=True)