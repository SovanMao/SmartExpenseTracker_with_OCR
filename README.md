# Smart Expense Tracker with Receipt OCR

## Project Overview
This is a **Python-based Expense Tracker** that allows users to log, manage, and visualize personal expenses.  
It also integrates **Receipt OCR** functionality using `pytesseract` to automatically extract expense details (amount, date, vendor) from receipt images and suggest categories for user confirmation.

The app provides:
- Manual and receipt-based expense entry
- Auto-suggested categories
- Summary charts (pie chart by category, line chart by month)
- Streamlit interactive UI for a smooth demo

---

## Dataset
We use two datasets for testing OCR functionality:

1. [High-Quality Invoice Images for OCR](https://www.kaggle.com/datasets/osamahosamabdellatif/high-quality-invoice-images-for-ocr)  
2. [Invoice OCR Dataset](https://www.kaggle.com/datasets/senju14/invoice-ocr)

Sample receipts are included in the `dataset/` folder for demo purposes.

---

## Features
- Add expenses manually
- Upload receipt images and extract data automatically
- Auto-suggest categories with user confirmation
- View summaries with pie and line charts
- Save and load expense data (CSV/JSON)

---

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/SmartExpenseTracker.git
```
2. Install Python 3.x dependencies:
```
pip install -r requirements.txt
```
3. Run the Streamlit app:
```
streamlit run src/app.py
```
Project Structure
```
SmartExpenseTracker/
│
├─ dataset/                # Sample receipt images
├─ src/                    # Python source code
│   ├─ expense_tracker.py  # Core tracker logic
│   ├─ receipt_ocr.py      # OCR + parsing
│   └─ app.py              # Streamlit UI
├─ documentation/          # Docs and screenshots
├─ WBS.xlsx                # Work Breakdown Structure & progress tracker
├─ requirements.txt        # Python dependencies
└─ README.md
```
---

## Team Members

1. Person A – Expense Tracker core logic
2. Person B – Receipt OCR module
3. Person C – Streamlit UI + documentation
---

## Usage

- Launch the app using Streamlit
- Add an expense manually or upload a receipt image
- Review the suggested category and confirm or edit
- View expense summaries via charts
- Expenses are saved automatically for future sessions
---

## License
This project is for educational purposes. Dataset licenses apply as per Kaggle datasets.
