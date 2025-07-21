# main.py

import os
import shutil
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from contextlib import asynccontextmanager
import pathlib

# --- Absolute Path Configuration ---
APP_DIR = pathlib.Path(__file__).parent.resolve()
BACKEND_ROOT_DIR = APP_DIR.parent
UPLOADS_DIR = BACKEND_ROOT_DIR / "uploads"
DB_FILE = BACKEND_ROOT_DIR / "receipts.db"

from . import crud, models, schemas
from .services import parser
from .database import engine, get_db

def run_startup_logic():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    if os.path.exists(UPLOADS_DIR):
        shutil.rmtree(UPLOADS_DIR)
    models.Base.metadata.create_all(bind=engine)
    os.makedirs(UPLOADS_DIR)

@asynccontextmanager
async def lifespan(app: FastAPI):
    run_startup_logic()
    yield

app = FastAPI(title="Receipt Processor API", lifespan=lifespan)

@app.post("/upload/", response_model=schemas.Receipt)
def upload_and_process_receipt(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # ... (code is unchanged)
    allowed_extensions = {'.png', '.jpg', '.jpeg', '.pdf', '.txt'}
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"File type '{file_extension}' not supported.")

    file_path = os.path.join(UPLOADS_DIR, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")

    try:
        extracted_data = parser.process_file(file_path, file_extension)
        receipt_data = schemas.ReceiptCreate(
            **extracted_data,
            file_path=str(file_path)
        )
        return crud.create_receipt(db=db, receipt=receipt_data)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Parsing error: {e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@app.get("/receipts/", response_model=List[schemas.Receipt])
def read_receipts(skip: int = 0, limit: int = 100, sort_by: Optional[str] = Query(None, enum=["date", "vendor", "amount"]), sort_order: Optional[str] = Query("asc", enum=["asc", "desc"]), db: Session = Depends(get_db)):
    return crud.get_receipts(db, skip=skip, limit=limit, sort_by=sort_by, sort_order=sort_order)

@app.get("/receipts/search/", response_model=List[schemas.Receipt])
def search_for_receipts(vendor: Optional[str] = None, start_date: Optional[date] = None, end_date: Optional[date] = None, db: Session = Depends(get_db)):
    return crud.search_receipts(db, vendor=vendor, start_date=start_date, end_date=end_date)
    
@app.get("/stats/summary/", response_model=schemas.SpendStats)
def get_stats_summary(db: Session = Depends(get_db)):
    return crud.get_spend_statistics(db)

# MODIFIED: Endpoint path, response_model, and function call are updated.
@app.get("/stats/vendor_spend/", response_model=List[schemas.VendorSpend])
def get_vendor_spend_stats(db: Session = Depends(get_db)):
    return crud.get_vendor_spend(db)

@app.get("/stats/monthly_spend/", response_model=List[schemas.MonthlySpend])
def get_monthly_spend_stats(db: Session = Depends(get_db)):
    return crud.get_monthly_spend(db)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True, reload_dirs=[str(APP_DIR)])




