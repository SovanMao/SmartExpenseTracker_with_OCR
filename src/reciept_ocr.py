# ---------------- IMPORTS AND DEPENDENCIES ----------------
import easyocr
import re
import pandas as pd
import dateparser
from transformers import pipeline

class ReceiptOCR:

    # ---------------- CLASS INITIALIZATION ----------------
    def __init__(self):
        # Initialize EasyOCR reader for English
        self.reader = easyocr.Reader(['en'], gpu=False)
        
        # Initialize category classifier
        try:
            self.classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        except:
            self.classifier = None
            print("Warning: Could not load classification model. Category prediction will use keyword matching.")
        
        # Categories for classification
        self.categories = [
            "Food & Dining", "Transportation", "Shopping", "Entertainment", 
            "Bills & Utilities", "Healthcare", "Education", "Travel", 
            "Groceries", "Gas", "Other"
        ]  
    
    
    # ---------------- MAIN PROCESSING ----------------
    def process_receipt(self, receipt_path: str) -> pd.DataFrame:
        try:
            # OCR: Extract text from image
            results = self.reader.readtext(receipt_path)
            extracted_text = " ".join([res[1] for res in results])
            print("Extracted Text:\n", extracted_text)

            # ----- Extract date ----- 
            date_patterns = [
                r"\b\d{4}[-/]\d{2}[-/]\d{2}\b",     # 2020-12-31
                r"\b\d{2}[-/]\d{2}[-/]\d{4}\b",     # 31/12/2020
                r"\b\d{2}[-/]\d{2}[-/]\d{2}\b",     # 31-12-20
                r"\b\d{1,2}[-/]\d{1,2}\s\d{4}\b",   # 11-31 2020 (with space)
                r"\b\w+\s\d{1,2},\s\d{4}\b"         # Dec 31, 2020
            ]

            date_found = None
            for pattern in date_patterns:
                match = re.search(pattern, extracted_text)
                if match:
                    date_found = match.group()
                    break

            # Parse into standard format YYYY-MM-DD
            if date_found:
                if dateparser:
                    parsed_date = dateparser.parse(date_found)
                    if parsed_date:
                        date = parsed_date.strftime("%Y-%m-%d")
                    else:
                        date = date_found   # fallback keep raw string
                else:
                    date = date_found
            else:
                date = "Unknown"


            # ----- Extract total/amount -----
            total_match = re.findall(r"\d{1,3}(?:[ ,]?\d{3})*(?:[.,]\d{2})", extracted_text)   
            total_normalized = [val.replace(" ", "").replace(",", ".") for val in total_match]          # Normalize numbers for EU money(remove spaces, replace ',' with '.')
            total = total_normalized[-1] if total_normalized else "Unknown"                             # Get last number as total

            print("\nTotal match:", total_match)
            print("Normalized totals:", total_normalized)
            print("Total extracted:", total)
    

            # ----- Extract place (take first line as guess) -----
            place = results[0][1] if results else "Unknown"


            # ----- Predict category -----
            if self.classifier:
                try:
                    category_result = self.classifier(extracted_text, candidate_labels=self.categories)
                    category = category_result["labels"][0]
                except:
                    category = "Other"
            else:
                category = "Other"


            # Print results
            print("\n--- Extracted Information ---")
            print("Date:", date)
            print("Place:", place)
            print("Total:", total)
            print("Category:", category)

            # Create DataFrame for return (don't auto-save to CSV)
            data = {"Date": [date], "Place": [place], "Total": [total], "Category": [category]}
            df = pd.DataFrame(data)
            
            return df
            
        except Exception as e:
            print(f"Error processing receipt: {str(e)}")
            # Return empty DataFrame on error
            return pd.DataFrame(columns=["Date", "Place", "Total", "Category"])
    

