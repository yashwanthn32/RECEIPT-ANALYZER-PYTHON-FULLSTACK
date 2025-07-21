# crud.py

from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from . import models, schemas
from datetime import date
from typing import List, Optional
import statistics

def get_receipts(db: Session, skip: int = 0, limit: int = 100, sort_by: Optional[str] = None, sort_order: str = "asc"):
    """Retrieve all receipts with pagination and sorting."""
    query = db.query(models.Receipt)
    
    if sort_by:
        column = getattr(models.Receipt, sort_by, None)
        if column:
            if sort_order == "desc":
                query = query.order_by(desc(column))
            else:
                query = query.order_by(column)

    return query.offset(skip).limit(limit).all()

def search_receipts(db: Session, vendor: Optional[str] = None, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[models.Receipt]:
    """Search receipts based on various criteria."""
    query = db.query(models.Receipt)
    if vendor:
        query = query.filter(models.Receipt.vendor.like(f"%{vendor}%"))
    if start_date:
        query = query.filter(models.Receipt.date >= start_date)
    if end_date:
        query = query.filter(models.Receipt.date <= end_date)
    return query.all()

def create_receipt(db: Session, receipt: schemas.ReceiptCreate) -> models.Receipt:
    """
    Creates a new receipt or updates an existing one based on the file_path.
    This provides a robust "upsert" functionality.
    """
    # Check if a receipt with the same file path exists
    existing_receipt = db.query(models.Receipt).filter(models.Receipt.file_path == receipt.file_path).first()
    
    if existing_receipt:
        # If it exists, update its fields with the new data
        update_data = receipt.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(existing_receipt, key, value)
        db_receipt = existing_receipt
    else:
        # If it doesn't exist, create a new instance
        db_receipt = models.Receipt(**receipt.model_dump())
        db.add(db_receipt)

    # Commit the transaction (updates or adds the record)
    db.commit()
    db.refresh(db_receipt)
    return db_receipt

def get_spend_statistics(db: Session) -> schemas.SpendStats:
    """Calculate and return aggregate spending statistics."""
    amounts = db.query(models.Receipt.amount).all()
    amount_list = [a[0] for a in amounts]

    if not amount_list:
        return schemas.SpendStats(total_spend=0, mean_spend=0, median_spend=0, mode_spend=0)

    total = sum(amount_list)
    mean = statistics.mean(amount_list)
    median = statistics.median(amount_list)
    try:
        mode = statistics.mode(amount_list)
    except statistics.StatisticsError:
        mode = 0 # No unique mode

    return schemas.SpendStats(total_spend=total, mean_spend=mean, median_spend=median, mode_spend=mode)

# MODIFIED: This function now calculates the sum of the amount, not the count.
def get_vendor_spend(db: Session) -> List:
    """Get the total amount spent per vendor."""
    return db.query(
        models.Receipt.vendor,
        func.sum(models.Receipt.amount).label('total_spend')
    ).group_by(models.Receipt.vendor).order_by(desc('total_spend')).all()

def get_monthly_spend(db: Session) -> List:
    """Get total spend aggregated by month."""
    return db.query(
        func.strftime('%Y-%m', models.Receipt.date).label('month'),
        func.sum(models.Receipt.amount).label('total_spend')
    ).group_by('month').order_by('month').all()