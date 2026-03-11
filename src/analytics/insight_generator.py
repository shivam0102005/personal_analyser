"""
insight_generator.py
--------------------
Generates human-readable automated insights from financial data.
"""

import pandas as pd
import numpy as np
from src.analytics.expense_analysis import (
    get_debit_df, category_spending, monthly_spending,
    weekday_vs_weekend, top_merchants, average_daily_spending
)


def generate_insights(df: pd.DataFrame, budgets: dict = None) -> list:
    """Return a list of insight strings."""
    insights = []

    if df.empty:
        return ["No data available to generate insights."]

    debits = get_debit_df(df)
    if debits.empty:
        return ["No debit transactions found."]

    # 1. Top category insight
    cats = category_spending(df)
    if not cats.empty:
        top = cats.iloc[0]
        insights.append(
            f"💸 You spent the most on **{top['Category']}** — "
            f"₹{top['Total']:,.0f} ({top['Percentage']:.1f}% of total spending)."
        )

    # 2. Monthly change insight
    monthly = monthly_spending(df)
    if len(monthly) >= 2:
        last = monthly.iloc[-1]
        prev = monthly.iloc[-2]
        change = last["MoM_Change_Pct"]
        if not np.isnan(change):
            direction = "increased 📈" if change > 0 else "decreased 📉"
            insights.append(
                f"📅 Your spending in **{last['Month_Name']} {int(last['Year'])}** "
                f"{direction} by **{abs(change):.1f}%** compared to the previous month."
            )

    # 3. Weekend vs Weekday
    ww = weekday_vs_weekend(df)
    if ww["Weekend_Higher"]:
        insights.append(
            f"📆 You spend more on **weekends** (avg ₹{ww['Weekend_Avg']:,.0f}) "
            f"vs weekdays (avg ₹{ww['Weekday_Avg']:,.0f}). Consider weekend budgeting!"
        )
    else:
        insights.append(
            f"📆 Your weekday spending (avg ₹{ww['Weekday_Avg']:,.0f}) "
            f"exceeds weekend spending (avg ₹{ww['Weekend_Avg']:,.0f})."
        )

    # 4. Top merchant
    merchants = top_merchants(df, n=1)
    if not merchants.empty:
        m = merchants.iloc[0]
        insights.append(
            f"🏪 Your most-visited merchant is **{m['Merchant']}** "
            f"with ₹{m['Total_Spent']:,.0f} spent across {int(m['Transactions'])} transactions."
        )

    # 5. Average daily spending
    avg_daily = average_daily_spending(df)
    insights.append(f"📊 Your average daily spending is **₹{avg_daily:,.0f}**.")

    # 6. Food spending check
    food_row = cats[cats["Category"] == "Food"]
    if not food_row.empty:
        food_pct = food_row.iloc[0]["Percentage"]
        if food_pct > 30:
            insights.append(
                f"🍔 Food expenses account for **{food_pct:.1f}%** of your spending — "
                f"consider home cooking to reduce costs."
            )

    # 7. Budget alerts
    if budgets:
        for cat, budget in budgets.items():
            actual = debits[debits["Category"] == cat]["Amount"].sum()
            if actual > budget:
                overspend = actual - budget
                insights.append(
                    f"⚠️ **Budget Alert**: You've overspent on **{cat}** by "
                    f"₹{overspend:,.0f} (Budget: ₹{budget:,.0f}, Actual: ₹{actual:,.0f})."
                )

    # 8. Savings rate
    income = df[df["Transaction_Type"] == "Credit"]["Amount"].sum()
    expenses = debits["Amount"].sum()
    if income > 0:
        savings_rate = ((income - expenses) / income) * 100
        emoji = "✅" if savings_rate > 20 else "⚠️"
        insights.append(
            f"{emoji} Your estimated savings rate is **{savings_rate:.1f}%** "
            f"(Income: ₹{income:,.0f}, Expenses: ₹{expenses:,.0f})."
        )

    # 9. Subscription costs
    ent_row = cats[cats["Category"] == "Entertainment"]
    if not ent_row.empty:
        insights.append(
            f"📺 You spent ₹{ent_row.iloc[0]['Total']:,.0f} on entertainment/subscriptions. "
            f"Review unused subscriptions to save money."
        )

    return insights
