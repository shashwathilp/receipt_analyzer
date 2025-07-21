import pytesseract
from pdfminer.high_level import extract_text as extract_pdf_text
from PIL import Image
import io
import re
import dateparser
from datetime import datetime

class DataExtractor:
    """
    Extracts structured receipt data (vendor, date, amount, category) from
    images, PDFs, or plain text using OCR and regex patterns.
    """

    def extract_from_image(self, image_bytes: bytes) -> dict:
        try:
            image = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(image)
            return self._parse_text(text)
        except Exception as e:
            print("Image extraction error:", e)
            return {}

    def extract_from_pdf(self, pdf_bytes: bytes) -> dict:
        try:
            with io.BytesIO(pdf_bytes) as pdf_stream:
                text = extract_pdf_text(pdf_stream)
            return self._parse_text(text)
        except Exception as e:
            print("PDF extraction error:", e)
            return {}

    def extract_from_text(self, text: str) -> dict:
        return self._parse_text(text)

    def _parse_text(self, text: str) -> dict:
        lines = text.splitlines()
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        vendor = non_empty_lines[0] if non_empty_lines else "Unknown"

        # Extract amount
        amount = None
        for line in reversed(non_empty_lines):
            match = re.search(r'(₹|\$)?\s?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', line)
            if match:
                try:
                    amount = float(match.group(2).replace(',', ''))
                    break
                except:
                    continue

        # Extract date using dateparser
        date = None
        for line in non_empty_lines:
            match = re.search(r'(\b\d{1,4}[-/]\d{1,2}[-/]\d{1,4}\b)', line)
            if match:
                date_str = match.group(0)
                parsed = dateparser.parse(date_str, settings={'DATE_ORDER': 'DMY'})
                if parsed:
                    date = parsed.date()
                    break

        # Extract category
        category = "Uncategorized"
        category_keywords = {
            "Groceries": [
                "grocery", "supermart", "supermarket", "mart", "store", "bazaar",
                "provision", "kirana", "vegetable", "fruit", "ration"
            ],
            "Electronics": [
                "laptop", "electronics", "mobile", "tv", "charger", "usb", "mouse",
                "headphones", "earbuds", "tablet", "smartwatch", "battery", "device"
            ],
            "Food & Drink": [
                "cafe", "coffee", "restaurant", "burger", "food", "tea", "snacks", "meal",
                "pizza", "pasta", "sandwich", "noodles", "biryani", "chai", "lunch", "dinner", "zomato", "swiggy"
            ],
            "Clothing": [
                "shirt", "dress", "jeans", "apparel", "wear", "fashion", "boutique",
                "kurta", "saree", "salwar", "lehenga", "ethnic", "pants", "clothes", "garments"
            ],
            "Pharmacy": [
                "pharmacy", "medicine", "chemist", "drug", "tablet", "capsule",
                "clinic", "doctor", "prescription", "hospital", "meds"
            ],
            "Entertainment": [
                "movie", "book", "game", "cinema", "netflix", "ticket",
                "concert", "event", "theatre", "show", "pvr", "inox"
            ],
            "Utilities": [
                "electricity", "water", "gas", "internet", "bill", "postpaid",
                "recharge", "broadband", "wifi", "mobile bill", "data plan", "airtel", "jio", "bsnl"
            ],
            "Home & Kitchen": [
                "furniture", "kitchen", "bed", "sofa", "utensils", "cooker",
                "mixer", "home", "interior", "decor", "vase", "light", "bulb"
            ],
            "Transport": [
                "uber", "ola", "fuel", "petrol", "diesel", "bus", "cab", "auto", "ride", "metro", "train", "taxi"
            ],
            "Others": [
                "misc", "unknown", "general", "service", "repair", "custom", "charges"
            ]
        }

        text_lower = text.lower()
        for cat, keywords in category_keywords.items():
            if any(word in text_lower for word in keywords):
                category = cat
                break

        return {
            "vendor": vendor or "Unknown",
            "amount": amount if amount is not None else 0.0,
            "date": date,
            "category": category
        }

