import logging
import datetime
import streamlit as st
from pydantic import BaseModel, ValidationError, validator
from dateutil import parser
from .extraction import DataExtractor
from .storage import Storage

logging.basicConfig(level=logging.INFO)

class UploadedFile(BaseModel):
    filename: str
    content: bytes
    content_type: str

    @validator('content_type')
    def validate_content_type(cls, v):
        if not any(t in v for t in ['image', 'pdf', 'text']):
            raise ValueError(f"Unsupported file type: {v}")
        return v

class DataIngestor:
    def __init__(self, db_path='receipts.db'):
        self.extractor = DataExtractor()
        self.storage = Storage(db_path=db_path)

    def ingest_file(self, filename: str, content: bytes, content_type: str) -> tuple[bool, str]:
        try:
            validated_file = UploadedFile(
                filename=filename,
                content=content,
                content_type=content_type
            )

            if 'image' in validated_file.content_type:
                extracted_data = self.extractor.extract_from_image(validated_file.content)
            elif 'pdf' in validated_file.content_type:
                extracted_data = self.extractor.extract_from_pdf(validated_file.content)
            elif 'text' in validated_file.content_type:
                text = validated_file.content.decode('utf-8')
                extracted_data = self.extractor.extract_from_text(text)
            else:
                return False, f"Unsupported file type: {validated_file.content_type}"

            if not extracted_data:
                logging.warning(f"No data extracted from file: {filename}")
                return False, f"Could not extract any data from '{filename}'."

            vendor = extracted_data.get('vendor', 'Unknown')
            amount = extracted_data.get('amount', 0.0)

            # Handle date parsing
            extracted_date = extracted_data.get('date')
            if extracted_date:
                try:
                    parsed_date = extracted_date if isinstance(extracted_date, datetime.date) else parser.parse(str(extracted_date)).date()
                except Exception:
                    st.warning("⚠️ Invalid date format. Using today's date.")
                    parsed_date = datetime.date.today()
            else:
                st.warning("⚠️ Could not extract date. Using today's date.")
                parsed_date = datetime.date.today()

            category = extracted_data.get('category', 'Uncategorized')

            self.storage.add_receipt(
                vendor=vendor,
                date=str(parsed_date),
                amount=amount,
                category=category
            )

            logging.info(f"Receipt processed successfully: {filename}")
            return True, f"Successfully processed and stored receipt from '{filename}'."

        except ValidationError as e:
            logging.error(f"Validation error: {e}")
            return False, f"Validation Error: {e}"
        except Exception as e:
            logging.exception("Unexpected error during ingestion")
            return False, f"Unexpected error processing '{filename}': {e}"
