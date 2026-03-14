"""
data_cleaning.py
----------------
Data preprocessing pipeline for the AI Personal Finance Analyzer.
Handles cleaning, normalization, deduplication, and standardization.
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ─── Categorization Rules ────────────────────────────────────────────────────

CATEGORY_RULES = {
    "Food": [
        "swiggy", "zomato", "food", "restaurant", "cafe", "pizza", "burger",
        "kfc", "mcdonalds", "dominos", "biryani", "dining", "lunch", "dinner",
        "breakfast", "eat", "meal", "barbeque", "social", "taj restaurant",
        "mainland", "subway"
    ],
    "Transport": [
        "uber", "ola", "cab", "taxi", "petrol", "fuel", "rapido", "metro",
        "bus", "train", "railway", "irctc", "auto", "transport", "indian oil",
        "hp petrol", "bharat petroleum", "namma yatri"
    ],
    "Shopping": [
        "amazon", "flipkart", "myntra", "ajio", "shopping", "purchase",
        "meesho", "nykaa", "store", "mall", "fashion", "clothes", "garments",
        "decathlon", "ikea", "croma", "reliance digital"
    ],
    "Entertainment": [
        "netflix", "spotify", "prime", "hotstar", "disney", "youtube",
        "bookmyshow", "movie", "theatre", "concert", "gaming", "playstation",
        "steam", "pvr", "inox", "apple music", "gaana", "jiosaavn"
    ],
    "Utilities": [
        "electricity", "water", "gas", "internet", "broadband", "mobile",
        "recharge", "bill", "tata power", "bescom", "municipal", "airtel",
        "jio", "bsnl", "wifi", "byjus", "unacademy"
    ],
    "Groceries": [
        "dmart", "bigbasket", "grofers", "blinkit", "zepto", "grocery",
        "supermarket", "vegetables", "fruits", "milk", "dairy", "kirana",
        "reliance fresh", "more supermarket", "spencers"
    ],
    "Healthcare": [
        "pharmacy", "medical", "hospital", "doctor", "clinic", "apollo",
        "medplus", "netmeds", "1mg", "diagnostic", "lab test", "healthcare",
        "medicine", "dentist", "health"
    ],
    "Health & Fitness": [
        "gym", "cult.fit", "crossfit", "yoga", "fitness", "sport",
        "healthify", "cure.fit", "gold gym", "anytime fitness"
    ],
    "Education": [
        "school", "college", "university", "course", "udemy", "coursera",
        "education", "tuition", "book", "stationery", "amazon kindle"
    ],
    "Income": [
        "salary", "credit", "employer", "neft", "wages", "freelance",
        "dividend", "interest", "refund", "cashback", "bonus"
    ],
    "Miscellaneous": [
        "atm", "withdrawal", "transfer", "miscellaneous", "other"
    ],
}

PAYMENT_METHOD_RULES = {
    "UPI": ["upi", "gpay", "phonepe", "paytm", "bhim", "razorpay"],
    "Credit Card": ["credit card", "cc", "visa", "mastercard", "amex"],
    "Debit Card": ["debit card", "dc", "rupay"],
    "Net Banking": ["net banking", "netbanking", "neft", "rtgs", "imps"],
    "Cash": ["cash", "atm"],
    "Bank Transfer": ["bank transfer", "wire transfer"],
}

STANDARD_COLUMNS = ["Date", "Description", "Category", "Amount", "Transaction_Type", "Merchant", "Payment_Method"]


# ─── Categorization Functions ─────────────────────────────────────────────────

def categorize_transaction(description: str, existing_category: str = None) -> str:
    """Assign category based on description keywords."""
    if existing_category and str(existing_category).strip() not in ["", "nan", "Unknown"]:
        return existing_category.strip()

    desc_lower = str(description).lower()
    for category, keywords in CATEGORY_RULES.items():
        if any(kw in desc_lower for kw in keywords):
            return category
    return "Miscellaneous"


def extract_merchant(description: str) -> str:
    """Extract merchant name from transaction description."""
    desc = str(description).strip()
    # Remove common prefixes/suffixes
    prefixes = ["payment to ", "paid to ", "purchase at ", "transaction at ",
                "pos ", "upi-", "neft-", "imps-"]
    for p in prefixes:
        if desc.lower().startswith(p):
            desc = desc[len(p):]
    # Take first meaningful word(s) as merchant name
    parts = desc.split()
    merchant = " ".join(parts[:2]) if len(parts) >= 2 else desc
    return merchant.title()[:50]


def detect_payment_method(description: str, existing: str = None) -> str:
    """Infer payment method from description."""
    if existing and str(existing).strip() not in ["", "nan", "Unknown"]:
        return existing.strip()
    desc_lower = str(description).lower()
    for method, keywords in PAYMENT_METHOD_RULES.items():
        if any(kw in desc_lower for kw in keywords):
            return method
    return "UPI"  # Default for Indian transactions


def detect_transaction_type(amount, description: str = "", existing: str = None) -> str:
    """Detect whether transaction is Debit or Credit."""
    if existing and str(existing).strip() in ["Debit", "Credit"]:
        return existing.strip()

    desc_lower = str(description).lower()
    credit_keywords = ["salary", "credit", "refund", "cashback", "interest", "dividend", "bonus", "neft cr"]
    if any(kw in desc_lower for kw in credit_keywords):
        return "Credit"

    # Negative amounts are typically debits
    try:
        if float(amount) < 0:
            return "Debit"
    except (ValueError, TypeError):
        pass

    return "Debit"


# ─── Cleaning Pipeline ────────────────────────────────────────────────────────

class DataCleaner:
    def __init__(self):
        self.cleaning_report = {}

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Main cleaning pipeline."""
        logger.info(f"Starting data cleaning. Input shape: {df.shape}")
        original_count = len(df)

        df = self._standardize_columns(df)
        df = self._clean_dates(df)
        df = self._clean_amounts(df)
        df = self._handle_missing_values(df)
        df = self._remove_duplicates(df)
        df = self._apply_categorization(df)
        df = self._add_derived_features(df)

        self.cleaning_report = {
            "original_rows": original_count,
            "cleaned_rows": len(df),
            "removed_rows": original_count - len(df),
            "columns": list(df.columns),
        }

        logger.info(f"Cleaning complete. Output shape: {df.shape}")
        return df

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Rename and ensure all standard columns exist."""
        col_map = {}
        for col in df.columns:
            col_lower = col.lower().strip()
            if col_lower in ["date", "transaction date", "txn date", "value date"]:
                col_map[col] = "Date"
            elif col_lower in ["description", "narration", "particulars", "details", "remarks"]:
                col_map[col] = "Description"
            elif col_lower in ["amount", "debit", "credit", "transaction amount"]:
                col_map[col] = "Amount"
            elif col_lower in ["category", "type", "expense type"]:
                col_map[col] = "Category"
            elif col_lower in ["transaction_type", "dr/cr", "type"]:
                col_map[col] = "Transaction_Type"
            elif col_lower in ["merchant", "vendor", "payee"]:
                col_map[col] = "Merchant"
            elif col_lower in ["payment_method", "mode", "payment mode", "channel"]:
                col_map[col] = "Payment_Method"

        df = df.rename(columns=col_map)

        for col in STANDARD_COLUMNS:
            if col not in df.columns:
                df[col] = np.nan

        return df[STANDARD_COLUMNS]

    def _clean_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize date formats."""
        date_formats = [
            "%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y",
            "%d %b %Y", "%d %B %Y", "%Y/%m/%d", "%d-%b-%Y"
        ]
        def parse_date(val):
            if pd.isna(val):
                return pd.NaT
            for fmt in date_formats:
                try:
                    return datetime.strptime(str(val).strip(), fmt)
                except ValueError:
                    continue
            try:
                return pd.to_datetime(str(val), format="mixed")
            except Exception:
                return pd.NaT

        df["Date"] = df["Date"].apply(parse_date)
        df = df.dropna(subset=["Date"])
        df["Date"] = pd.to_datetime(df["Date"])
        return df

    def _clean_amounts(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert amount column to numeric."""
        def parse_amount(val):
            if pd.isna(val):
                return np.nan
            val_str = str(val).replace(",", "").replace("₹", "").replace("$", "").strip()
            # Handle parentheses for negative: (500) → -500
            val_str = re.sub(r'\((.+)\)', r'-\1', val_str)
            try:
                return abs(float(val_str))
            except ValueError:
                return np.nan

        df["Amount"] = df["Amount"].apply(parse_amount)
        df = df.dropna(subset=["Amount"])
        df = df[df["Amount"] > 0]
        return df

    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fill or handle missing values."""
        df["Description"] = df["Description"].fillna("Unknown Transaction")
        df["Category"] = df["Category"].fillna("Miscellaneous")
        df["Transaction_Type"] = df["Transaction_Type"].fillna("Debit")
        df["Merchant"] = df["Merchant"].fillna("Unknown")
        df["Payment_Method"] = df["Payment_Method"].fillna("Unknown")
        return df

    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove exact duplicate transactions."""
        before = len(df)
        df = df.drop_duplicates(subset=["Date", "Description", "Amount"])
        logger.info(f"Removed {before - len(df)} duplicate rows.")
        return df.reset_index(drop=True)

    def _apply_categorization(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply rule-based categorization and merchant extraction."""
        df["Category"] = df.apply(
            lambda row: categorize_transaction(row["Description"], row["Category"]), axis=1
        )
        df["Merchant"] = df.apply(
            lambda row: extract_merchant(row["Description"])
            if str(row["Merchant"]) in ["Unknown", "nan", ""] else row["Merchant"],
            axis=1
        )
        df["Payment_Method"] = df.apply(
            lambda row: detect_payment_method(row["Description"], row["Payment_Method"]), axis=1
        )
        df["Transaction_Type"] = df.apply(
            lambda row: detect_transaction_type(row["Amount"], row["Description"], row["Transaction_Type"]), axis=1
        )
        return df

    def _add_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add helper columns for analytics."""
        df["Year"] = df["Date"].dt.year
        df["Month"] = df["Date"].dt.month
        df["Month_Name"] = df["Date"].dt.strftime("%B")
        df["Day"] = df["Date"].dt.day
        df["Day_of_Week"] = df["Date"].dt.day_name()
        df["Is_Weekend"] = df["Date"].dt.dayofweek.isin([5, 6])
        df["Week_Number"] = df["Date"].dt.isocalendar().week.astype(int)
        df["YearMonth"] = df["Date"].dt.to_period("M").astype(str)
        return df
