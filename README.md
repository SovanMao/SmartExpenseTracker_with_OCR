# Smart Expense Tracker with Receipt OCR

## Project Overview

This is a **Python-based Smart Expense Tracker** that allows users to log, manage, and visualize personal expenses with a modern web interface.
It integrates **Receipt OCR** functionality using `easyocr` and `transformers` to automatically extract expense details (amount, date, vendor, category) from receipt images and suggest categories using AI.


**Key Features:**
- Manual and receipt-based expense entry
- AI-powered auto-suggested categories
- Summary charts (pie, line, bar) for spending analysis
- Streamlit interactive UI for a smooth experience

---

## Dataset

You can use public datasets for testing OCR functionality:

1. [High-Quality Invoice Images for OCR](https://www.kaggle.com/datasets/osamahosamabdellatif/high-quality-invoice-images-for-ocr)  
2. [Invoice OCR Dataset](https://www.kaggle.com/datasets/senju14/invoice-ocr)


You may add your own sample receipts in a `dataset/` folder for demo purposes.

---


## Features
- Add expenses manually
- Upload receipt images and extract data automatically (OCR)
- AI-powered category suggestion (with fallback to keyword matching)
- View summaries with pie, line, and bar charts
- Save and load expense data (CSV/JSON)

---

## Installation

git clone https://github.com/SovanMao/SmartExpenseTracker_with_OCR.git
pip install -r requirements.txt
1. **Clone the repository:**
```bash
git clone https://github.com/SovanMao/SmartExpenseTracker_with_OCR.git
cd SmartExpenseTracker_with_OCR
```
2. **Install Python 3.x dependencies:**
```bash
pip install -r requirements.txt
```
3. **Run the Streamlit app:**
```bash
streamlit run app.py
```

## Project Structure
```
SmartExpenseTracker_with_OCR/
│
├─ src/                      # Python source code
│   ├─ expense_tracker.py    # Core tracker logic
│   ├─ reciept_ocr.py        # OCR + AI category suggestion
│   └─ app.py                # Streamlit UI
├─ documentation/            # Docs and documentation
│   ├─ Smart Expense Tracker with Receipt OCR and Auto-Categorization.docx
├─ requirements.txt          # Python dependencies
└─ README.md
```
---

## Team Members

- Person A – Expense Tracker core logic
- Person B – Receipt OCR & AI module
- Person C – Streamlit UI & documentation
---

## Usage

- Launch the app using Streamlit
- Add an expense manually or upload a receipt image (JPG, PNG, etc.)
- Review the extracted details and suggested category (AI-powered)
- Confirm or edit before saving
- View expense summaries and analytics via interactive charts
- Expenses are saved automatically for future sessions (CSV)
---

## License
This project is for educational purposes. Dataset licenses apply as per Kaggle datasets.
