🧾 Smart Receipt & Bill Analyzer

A Streamlit-powered web app that extracts and analyzes receipt data from images, PDFs, and text files.

🚀 Features

Upload receipts in JPG, PNG, PDF, or TXT formats

Automatically extract:

Vendor name

Date of purchase

Amount spent

Expense category (e.g., Food & Drink, Groceries, Clothing)

View your full receipt history in a dashboard

Visualize monthly spending trends and top categories/vendors

Delete all records with a single click (Admin action)

🖼️ Example Inputs

Grocery bills, shopping receipts, food invoices, etc.

📦 Tech Stack

Python 3

Streamlit

Tesseract OCR (pytesseract)

pdfminer.six (for PDF text extraction)

SQLite (local database)

Pydantic (data validation)

Pandas (dataframe visualization)

📁 Project Structure

.
├── app.py # Main Streamlit app

├── backend/

│ ├── extraction.py # Extracts text and metadata from uploaded files

│ ├── data_ingestion.py # Validates files, parses content, stores into DB

│ └── storage.py # SQLite DB handler

├── requirements.txt

├── .gitignore

└── README.md

⚙️ Installation

Clone this repo and install the dependencies:
git clone https://github.com/yourusername/receipt-analyzer.git
cd receipt-analyzer
pip install -r requirements.txt

Make sure Tesseract is installed and accessible from PATH.

Installation guide: https://github.com/tesseract-ocr/tesseract

🧪 Run the App:                                      
streamlit run app.py

📌 Notes

-Duplicate receipts (same vendor, amount, and date) are skipped

-Data is stored locally in receipts.db

📧 Contact

Developed by Shashwathi L P

Email: shashwathilp@gmail.com

LinkedIn: https://www.linkedin.com/in/shashwathi-l-p-488341333

GitHub: https://github.com/shashwathilp
