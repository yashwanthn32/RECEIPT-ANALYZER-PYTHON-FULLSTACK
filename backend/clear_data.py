# backend/clear_data.py

import os
import shutil

# --- Configuration ---
DB_FILE = "receipts.db"
UPLOADS_DIR = "uploads"

def clear_data():
    """
    A simple script to manually clear the database and uploaded files
    for a fresh start.
    """
    print("--- Starting Cleanup ---")

    # Delete the database file if it exists
    if os.path.exists(DB_FILE):
        try:
            os.remove(DB_FILE)
            print(f"Successfully deleted database: {DB_FILE}")
        except Exception as e:
            print(f"Error deleting database file: {e}")
    else:
        print("Database file not found, skipping.")

    # Delete the uploads directory if it exists
    if os.path.exists(UPLOADS_DIR):
        try:
            shutil.rmtree(UPLOADS_DIR)
            print(f"Successfully deleted uploads directory: {UPLOADS_DIR}")
        except Exception as e:
            print(f"Error deleting uploads directory: {e}")
    else:
        print("Uploads directory not found, skipping.")
    
    print("--- Cleanup Finished ---")

if __name__ == "__main__":
    clear_data()