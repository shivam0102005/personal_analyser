"""
expense_analysis.py
-------------------
Core analytics engine for the AI Personal Finance Analyzer.
All analytics use pandas groupby / resample operations.
"""

import pandas as pd
import numpy as np
from typing import Optional


def get_debit_df(df: pd.DataFrame) -> pd.DataFrame:
    """Return only debit (expense) transactions."""
    return df[df["Transaction_Type"] == "Debit"].copy()


# ─── Summary Statistics ───────────────────────────────────────────────────────

def total_spending(df: pd.DataFrame) -> float:
    return get_debit_df(df)["Amount"].sum()


def total_income(df: pd.DataFrame) -> float:
    return df[df["Transaction_Type"] == "Credit"]["Amount"].sum()


def average_daily_spending(df: pd.DataFrame) -> float:
    debits = get_debit_df(df)
    if debits.empty:
        return 0.0
    days = (debits["Date"].max() - debits["Date"].min()).days or 1
    return debits["Amount"].sum() / days


def average_transaction_value(df: pd.DataFrame) -> float:
    debits = get_debit_df(df)
    return debits["Amount"].mean() if not debits.empty else 0.0


def transaction_count(df: pd.DataFrame) -> int:
    return len(get_debit_df(df))


# ─── Category Analytics ───────────────────────────────────────────────────────

def category_spending(df: pd.DataFrame) -> pd.DataFrame:
    """Total spending grouped by category (debits only)."""
    debits = get_debit_df(df)
    result = (
        debits.groupby("Category")["Amount"]
        .agg(["sum", "count", "mean"])
        .rename(columns={"sum": "Total", "count": "Transactions", "mean": "Avg_Transaction"})
        .sort_values("Total", ascending=False)
        .reset_index()
    )
    result["Percentage"] = (result["Total"] / result["Total"].sum() * 100).round(2)
    return result


def highest_spending_category(df: pd.DataFrame) -> str:
    cats = category_spending(df)
    return cats.iloc[0]["Category"] if not cats.empty else "N/A"


def lowest_spending_category(df: pd.DataFrame) -> str:
    cats = category_spending(df)
    return cats.iloc[-1]["Category"] if not cats.empty else "N/A"


# ─── Monthly Analytics ────────────────────────────────────────────────────────

def monthly_spending(df: pd.DataFrame) -> pd.DataFrame:
    """Total debit spending per calendar month."""
    debits = get_debit_df(df)
    result = (
        debits.groupby(["Year", "Month", "Month_Name", "YearMonth"])["Amount"]
        .sum()
        .reset_index()
        .rename(columns={"Amount": "Total_Spending"})
        .sort_values(["Year", "Month"])
    )
    result["MoM_Change_Pct"] = result["Total_Spending"].pct_change() * 100
    return result


def monthly_category_spending(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly spending broken down by category (pivot table)."""
    debits = get_debit_df(df)
    pivot = debits.pivot_table(
        index="YearMonth", columns="Category", values="Amount", aggfunc="sum", fill_value=0
    )
    return pivot.reset_index()


# ─── Daily & Weekly Analytics ────────────────────────────────────────────────

def daily_spending(df: pd.DataFrame) -> pd.DataFrame:
    """Total spending per day."""
    debits = get_debit_df(df)
    return (
        debits.groupby("Date")["Amount"]
        .sum()
        .reset_index()
        .rename(columns={"Amount": "Daily_Total"})
        .sort_values("Date")
    )


def weekday_vs_weekend(df: pd.DataFrame) -> dict:
    """Compare average spending on weekdays vs weekends."""
    debits = get_debit_df(df)
    weekday_avg = debits[~debits["Is_Weekend"]]["Amount"].mean()
    weekend_avg = debits[debits["Is_Weekend"]]["Amount"].mean()
    return {
        "Weekday_Avg": round(weekday_avg, 2) if not np.isnan(weekday_avg) else 0,
        "Weekend_Avg": round(weekend_avg, 2) if not np.isnan(weekend_avg) else 0,
        "Weekend_Higher": weekend_avg > weekday_avg,
    }


def day_of_week_spending(df: pd.DataFrame) -> pd.DataFrame:
    """Average spending for each day of week."""
    debits = get_debit_df(df)
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    result = (
        debits.groupby("Day_of_Week")["Amount"]
        .agg(["sum", "mean", "count"])
        .rename(columns={"sum": "Total", "mean": "Average", "count": "Transactions"})
        .reindex(order)
        .reset_index()
    )
    return result


# ─── Merchant Analytics ───────────────────────────────────────────────────────

def top_merchants(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Top N merchants by total spend."""
    debits = get_debit_df(df)
    return (
        debits.groupby("Merchant")["Amount"]
        .agg(["sum", "count"])
        .rename(columns={"sum": "Total_Spent", "count": "Transactions"})
        .sort_values("Total_Spent", ascending=False)
        .head(n)
        .reset_index()
    )


def payment_method_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """How payments are split across payment methods."""
    debits = get_debit_df(df)
    return (
        debits.groupby("Payment_Method")["Amount"]
        .sum()
        .reset_index()
        .rename(columns={"Amount": "Total"})
        .sort_values("Total", ascending=False)
    )


# ─── Spending Heatmap Data ────────────────────────────────────────────────────

def spending_heatmap_data(df: pd.DataFrame) -> pd.DataFrame:
    """Returns a pivot table of Day_of_Week × Week_Number for heatmap."""
    debits = get_debit_df(df)
    pivot = debits.pivot_table(
        index="Day_of_Week", columns="Week_Number", values="Amount",
        aggfunc="sum", fill_value=0
    )
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivot = pivot.reindex([d for d in day_order if d in pivot.index])
    return pivot


# ─── Budget Tracking ──────────────────────────────────────────────────────────

def budget_vs_actual(df: pd.DataFrame, budgets: dict, year: int, month: int) -> pd.DataFrame:
    """Compare actual spending to budgets for a given month."""
    mask = (df["Year"] == year) & (df["Month"] == month) & (df["Transaction_Type"] == "Debit")
    period_df = df[mask]
    cat_spend = period_df.groupby("Category")["Amount"].sum().to_dict()

    rows = []
    for cat, budget in budgets.items():
        actual = cat_spend.get(cat, 0)
        rows.append({
            "Category": cat,
            "Budget": budget,
            "Actual": actual,
            "Remaining": budget - actual,
            "Used_Pct": round((actual / budget * 100), 1) if budget > 0 else 0,
            "Overspent": actual > budget,
        })
    return pd.DataFrame(rows)


# ─── Full Summary ─────────────────────────────────────────────────────────────

def generate_summary(df: pd.DataFrame) -> dict:
    """Return a high-level analytics summary dict."""
    debits = get_debit_df(df)
    monthly = monthly_spending(df)

    return {
        "total_spending": round(total_spending(df), 2),
        "total_income": round(total_income(df), 2),
        "avg_daily_spending": round(average_daily_spending(df), 2),
        "avg_transaction": round(average_transaction_value(df), 2),
        "transaction_count": transaction_count(df),
        "highest_category": highest_spending_category(df),
        "lowest_category": lowest_spending_category(df),
        "date_range": {
            "start": str(df["Date"].min().date()),
            "end": str(df["Date"].max().date()),
        },
        "months_covered": len(monthly),
        "weekday_vs_weekend": weekday_vs_weekend(df),
    }
