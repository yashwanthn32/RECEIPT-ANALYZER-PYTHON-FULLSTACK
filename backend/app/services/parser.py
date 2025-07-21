# parser.py

import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import re
from datetime import datetime
from typing import Dict, Any, List, Set

def extract_text_from_image(file_path: str) -> str:
    """Extracts text from an image file."""
    try:
        return pytesseract.image_to_string(Image.open(file_path))
    except Exception as e:
        print(f"Error processing image {file_path}: {e}")
        return ""

def extract_text_from_pdf(file_path: str) -> str:
    """Extracts text from a PDF file, attempting both text and OCR."""
    text = ""
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
        
        if len(text.strip()) < 100:
            for i, page in enumerate(doc):
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                text += pytesseract.image_to_string(img)
    except Exception as e:
        print(f"Error processing PDF {file_path}: {e}")
    return text

def extract_text_from_txt(file_path: str) -> str:
    """Extracts text from a plain text file."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Error processing text file {file_path}: {e}")
        return ""

def parse_receipt_text(text: str) -> Dict[str, Any]:
    """
    Parses raw text to extract structured data, now including category sub-totals.
    """
    extracted_data = {
        "vendor": "Unknown",
        "date": None,
        "amount": 0.0,
        "category": "Uncategorized",
        # This will now store a dictionary of {category: amount}
        "sub_categories": {}
    }

    # --- VENDOR DETECTION ---
    vendor_keywords = ["Target", "Walmart", "Costco", "Amazon", "BigBazaar", "Reliance Digital", "MegaMart"]
    for vendor in vendor_keywords:
        if re.search(vendor, text, re.IGNORECASE):
            extracted_data["vendor"] = vendor
            break

    # --- CATEGORY AND SUB-TOTAL DETECTION ---
    # This new logic finds category subtotals directly.
    category_keywords_map = {
        "Groceries": ["GROCERY SUBTOTAL"],
        "Electronics": ["ELECTRONICS SUBTOTAL"],
        "Apparel": ["APPAREL SUBTOTAL"],
    }
    
    found_categories: Dict[str, float] = {}
    for category, keywords in category_keywords_map.items():
        for keyword in keywords:
            # Regex to find the keyword and the number on the same line
            match = re.search(rf"{keyword}.*?([\d,]+\.\d{{2}})", text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                found_categories[category] = float(amount_str)
                break 

    # --- CATEGORY ASSIGNMENT ---
    if len(found_categories) > 1:
        extracted_data["category"] = "Mixed"
        extracted_data["sub_categories"] = found_categories
    elif len(found_categories) == 1:
        # Get the single category and its amount
        category, amount = list(found_categories.items())[0]
        extracted_data["category"] = category
        extracted_data["sub_categories"] = found_categories
            
    # --- DATE EXTRACTION ---
    date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})'
    date_match = re.search(date_pattern, text)
    if date_match:
        try:
            extracted_data["date"] = datetime.strptime(re.sub(r'/', '-', date_match.group(0)), '%d-%m-%Y').date()
        except ValueError:
            try:
                extracted_data["date"] = datetime.strptime(re.sub(r'/', '-', date_match.group(0)), '%Y-%m-%d').date()
            except ValueError:
                extracted_data["date"] = datetime.now().date()
    else:
        extracted_data["date"] = datetime.now().date()

    # --- FINAL AMOUNT EXTRACTION ---
    amount_pattern = r'(?:GRAND TOTAL)\s*[:\w\s]*[\$€£₹]?\s*([\d,]+\.\d{2})'
    amount_match = re.search(amount_pattern, text, re.IGNORECASE)
    if amount_match:
         extracted_data["amount"] = float(amount_match.group(1).replace(',', ''))
    else: # Fallback to the largest number if "GRAND TOTAL" isn't found
        all_floats = re.findall(r'[\d,]+\.\d{2}', text)
        if all_floats:
            cleaned_floats = [float(f.replace(',', '')) for f in all_floats]
            extracted_data["amount"] = max(cleaned_floats) if cleaned_floats else 0.0

    return extracted_data

def process_file(file_path: str, file_extension: str) -> Dict[str, Any]:
    """Main function to process an uploaded file."""
    text = ""
    if file_extension in ['.png', '.jpg', '.jpeg']:
        text = extract_text_from_image(file_path)
    elif file_extension == '.pdf':
        text = extract_text_from_pdf(file_path)
    elif file_extension == '.txt':
        text = extract_text_from_txt(file_path)
    
    if not text:
        raise ValueError("Could not extract text from the file.")

    return parse_receipt_text(text)