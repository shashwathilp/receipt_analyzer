import sqlite3
import pandas as pd
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)

class Storage:
    """
    Handles SQLite database storage for receipts.
    """

    def __init__(self, db_path='receipts.db'):
        self.db_path = db_path
        self._initialize_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _initialize_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS receipts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vendor TEXT NOT NULL,
                    date TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT
                )
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_date ON receipts (date)
            ''')
            conn.commit()
            logging.info("Database initialized successfully.")

    def receipt_exists(self, vendor: str, date: str, amount: float) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM receipts WHERE vendor=? AND date=? AND amount=?
            ''', (vendor, date, amount))
            result = cursor.fetchone()
            return result[0] > 0

    def add_receipt(self, vendor: str, date: str, amount: float, category: str = 'Uncategorized'):
        if self.receipt_exists(vendor, date, amount):
            logging.warning(f"Duplicate skipped: {vendor}, {date}, ₹{amount}")
            return
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO receipts (vendor, date, amount, category)
                VALUES (?, ?, ?, ?)
            ''', (vendor, date, amount, category))
            conn.commit()
            logging.info(f"Receipt added to DB: {vendor}, ₹{amount}, {date}")

    def get_all_receipts_as_dataframe(self) -> pd.DataFrame:
        with self._get_connection() as conn:
            try:
                df = pd.read_sql_query(
                    "SELECT vendor, date, amount, category FROM receipts ORDER BY date DESC",
                    conn
                )
                df['date'] = pd.to_datetime(df['date'])
                df = df.rename(columns={
                    'vendor': 'Vendor',
                    'date': 'Date',
                    'amount': 'Amount',
                    'category': 'Category'
                })
                return df
            except Exception as e:
                logging.error(f"Error fetching data from DB: {e}")
                return pd.DataFrame(columns=['Vendor', 'Date', 'Amount', 'Category'])
