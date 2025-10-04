import pandas as pd
from datetime import datetime, date
from typing import List, Dict, Optional
import os

class ExpenseTracker:
    
    # Initialize ExpenseTracker with data file and load existing expenses
    def __init__(self, data_file: str = "expenses.csv"):
        self.data_file = data_file
        self.expenses = []
        self.load_expenses()
    

    # Add a new expense record with validation
    def add_expense(self, amount: float, date_str: str, vendor: str, category: str) -> bool:
        try:
            # Validate date format
            expense_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            expense = {
                "id": len(self.expenses) + 1,
                "amount": float(amount),
                "date": date_str,
                "vendor": vendor.strip(),
                "category": category.strip()
            }
            
            self.expenses.append(expense)
            return True
        except ValueError as e:
            print(f"Error adding expense: {e}")
            return False
    

    # Save all expenses to a CSV file
    def save_expenses_csv(self, filename: Optional[str] = None) -> bool:
        try:
            filename = filename or self.data_file
            df = pd.DataFrame(self.expenses)
            df.to_csv(filename, index=False)
            return True
        except Exception as e:
            print(f"Error saving to CSV: {e}")
            return False
    

    # Load expenses from CSV file
    def load_expenses(self, filename: Optional[str] = None) -> bool:
        try:
            filename = filename or self.data_file
            if os.path.exists(filename):
                df = pd.read_csv(filename)
                self.expenses = df.to_dict('records')
                return True
            else:
                # Create empty file if it doesn't exist
                self.expenses = []
                return True
        except Exception as e:
            print(f"Error loading expenses: {e}")
            self.expenses = []
            return False
    

    # Return all expenses as a pandas DataFrame
    def get_expenses_df(self) -> pd.DataFrame:
        if not self.expenses:
            return pd.DataFrame(columns=['id', 'amount', 'date', 'vendor', 'category'])
        
        df = pd.DataFrame(self.expenses)
        df['date'] = pd.to_datetime(df['date'])
        return df
    

    # Calculate total spending grouped by category
    def get_total_by_category(self) -> Dict[str, float]:
        if not self.expenses:
            return {}
        
        df = self.get_expenses_df()
        return df.groupby('category')['amount'].sum().to_dict()


    # Get the most recent expenses (sorted by date)
    def get_recent_expenses(self, limit: int = 10) -> List[Dict]:
        if not self.expenses:
            return []
        
        # Sort by date (most recent first)
        sorted_expenses = sorted(self.expenses, 
                               key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d"), 
                               reverse=True)
        return sorted_expenses[:limit]
    

    # Calculate the total amount of all expenses
    def get_total_spending(self) -> float:
        return sum(expense['amount'] for expense in self.expenses)
    

    # Get a list of all unique categories used in expenses
    def get_categories(self) -> List[str]:
        return list(set(expense['category'] for expense in self.expenses))
    

# Default categories for the application
DEFAULT_CATEGORIES = [
    "Food & Dining",
    "Transportation",
    "Shopping",
    "Entertainment",
    "Bills & Utilities",
    "Healthcare",
    "Education",
    "Travel",
    "Groceries",
    "Gas",
    "Other"
]
