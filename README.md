# RECEIPT-ANALYZER-PYTHON-FULLSTACK
This is a complete full-stack application designed to upload, parse, and analyze receipts and bills. It extracts key information like the vendor, date, and total amount, and is particularly powerful in identifying and breaking down spending across multiple categories within a single receipt. The extracted data is then presented on an interactive dashboard with clear, insightful visualizations.

## How It Works

The application is built on a robust client-server architecture:

1.  **Frontend (Streamlit):** A user-friendly web interface where you can drag and drop receipt files (`.txt`, `.pdf`, `.png`, `.jpg`).
2.  **Backend (FastAPI):** A high-performance API that receives the uploaded files.
3.  **Parsing Engine:** The backend uses a sophisticated rule-based parser with regular expressions to scan the receipt's text. It intelligently identifies:
    * The primary vendor.
    * The transaction date.
    * The final grand total.
    * **Sub-totals for specific spending categories** (like Groceries, Electronics, Apparel).
4.  **Database (SQLite):** The extracted information, including the detailed category breakdown, is stored in a lightweight and reliable SQLite database.
5.  **Data Visualization:** The Streamlit frontend fetches the processed data from the backend and displays it in a clean table and a series of interactive charts, providing a clear overview of your spending habits.

---

## Project Structure

The project is organized into a clean, modular structure that separates the backend logic from the frontend interface.

<img width="636" height="605" alt="image" src="https://github.com/user-attachments/assets/b3985b08-b3a8-4118-ab0d-f6e7cf0cff1c" />

## How to Execute the Project

Follow these steps to get the application running on your local machine.

### Step 1: Prerequisites

Before you begin, ensure you have the following installed:

* **Python 3.8+**
* **Tesseract OCR Engine:** This is essential for processing image-based receipts.
    * **Windows:** Download and run the installer from [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki). During installation, make sure to add it to your system's PATH.
    * **macOS:** `brew install tesseract`
    * **Ubuntu/Debian:** `sudo apt update && sudo apt install tesseract-ocr`

### Step 2: Setup

1.  **Clone the Repository:**
    ```bash
    git clone <your-repo-url>
    cd receipt-processor
    ```

2.  **Install Dependencies:**
    Install all the required Python packages using the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```

### Step 3: Run the Application

The application consists of two parts that need to be run in separate terminals.

1.  **Start the Backend Server:**
    * Open a terminal and navigate to the `backend` directory.
    * Run the following command. This will start the server, and the `lifespan` event will automatically clear any old data, ensuring you get a fresh start every time.
    ```bash
    python -m app.main
    ```
    * Keep this terminal open. The API will be running at `http://127.0.0.1:8000`.

2.  **Start the Frontend Interface:**
    * Open a **new** terminal and navigate to the `frontend` directory.
    * Run the Streamlit application with this command:
    ```bash
    python -m streamlit run app.py
    ```
    * Your web browser should automatically open to the application's interface at `http://localhost:8501`.

You can now upload receipts and see the results instantly. After uploading a file, simply click the **"Refresh Charts"** button to update the visualizations with the new data.

---

## Key Features & Limitations

### Features

* **Multi-Format Support:** Handles `.txt`, `.pdf`, `.png`, and `.jpg` files.
* **Intelligent Parsing:** Accurately extracts vendor, date, and total amount.
* **Detailed Category Breakdown:** Identifies sub-totals for different spending categories within a single receipt and displays them in a pie chart.
* **Robust Error Handling:** The backend and frontend are designed to handle errors gracefully without crashing.
* **Fresh Start on Demand:** The backend automatically clears all previous data every time it is launched, providing a clean slate for each session.

### Limitations

* **Parser Rules:** The parser is rule-based and relies on specific keywords (e.g., "GRAND TOTAL", "ELECTRONICS SUBTOTAL"). It may not work correctly on receipts with very different layouts.
* **Single Currency:** The application assumes all amounts are in a single currency and does not perform currency conversion.
* **English Language:** The parsing keywords are in English, and it has not been tested on receipts in other languages.
