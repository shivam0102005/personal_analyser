"""
report_generator.py
-------------------
Generates PDF and CSV summary reports.
"""

import io
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime

from src.analytics.expense_analysis import (
    generate_summary, category_spending, monthly_spending, top_merchants
)
from src.analytics.insight_generator import generate_insights
from src.visualization.charts import mpl_category_pie, mpl_monthly_bar


def generate_pdf_report(df: pd.DataFrame, budgets: dict = None) -> bytes:
    """
    Generate a multi-page PDF report and return as bytes.
    """
    buf = io.BytesIO()
    summary = generate_summary(df)
    insights = generate_insights(df, budgets)
    cats = category_spending(df)
    merchants = top_merchants(df, n=10)
    monthly = monthly_spending(df)

    with PdfPages(buf) as pdf:
        # ── Page 1: Title & Summary ──────────────────────────────────────────
        fig = plt.figure(figsize=(11.69, 8.27))  # A4 landscape
        fig.patch.set_facecolor("#1E1E2E")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#1E1E2E")
        ax.axis("off")

        # Title
        ax.text(0.5, 0.92, "AI Personal Finance Analyzer", transform=ax.transAxes,
                fontsize=28, fontweight="bold", color="white", ha="center", va="center")
        ax.text(0.5, 0.84, f"Report Generated: {datetime.now().strftime('%d %B %Y, %H:%M')}",
                transform=ax.transAxes, fontsize=12, color="#AAAAAA", ha="center")

        # KPIs
        kpis = [
            ("Total Spending", f"₹{summary['total_spending']:,.0f}"),
            ("Total Income", f"₹{summary['total_income']:,.0f}"),
            ("Avg Daily Spend", f"₹{summary['avg_daily_spending']:,.0f}"),
            ("Transactions", str(summary['transaction_count'])),
            ("Top Category", summary['highest_category']),
            ("Date Range", f"{summary['date_range']['start']} → {summary['date_range']['end']}"),
        ]
        cols = 3
        for i, (label, value) in enumerate(kpis):
            x = 0.1 + (i % cols) * 0.3
            y = 0.62 - (i // cols) * 0.18
            rect = plt.Rectangle((x - 0.04, y - 0.06), 0.28, 0.14,
                                  transform=ax.transAxes, color="#2D2D44", zorder=1)
            ax.add_patch(rect)
            ax.text(x + 0.10, y + 0.02, value, transform=ax.transAxes,
                    fontsize=14, fontweight="bold", color="#A8EDEA", ha="center", zorder=2)
            ax.text(x + 0.10, y - 0.03, label, transform=ax.transAxes,
                    fontsize=9, color="#AAAAAA", ha="center", zorder=2)

        # Insights preview
        ax.text(0.5, 0.22, "Key Insights", transform=ax.transAxes,
                fontsize=14, fontweight="bold", color="white", ha="center")
        preview = insights[:3]
        for j, insight in enumerate(preview):
            clean = insight.replace("**", "").replace("📅", "").replace("💸", "").replace("📊", "")
            ax.text(0.5, 0.15 - j * 0.06, f"• {clean[:90]}", transform=ax.transAxes,
                    fontsize=9, color="#CCCCCC", ha="center")

        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        # ── Page 2: Charts ────────────────────────────────────────────────────
        fig = plt.figure(figsize=(11.69, 8.27))
        fig.patch.set_facecolor("#1E1E2E")
        gs = gridspec.GridSpec(1, 2, figure=fig, wspace=0.3)

        ax1 = fig.add_subplot(gs[0])
        ax1.set_facecolor("#1E1E2E")
        mpl_category_pie(df, ax=ax1)

        ax2 = fig.add_subplot(gs[1])
        ax2.set_facecolor("#1E1E2E")
        mpl_monthly_bar(df, ax=ax2)

        plt.style.use("dark_background")
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        # ── Page 3: Category & Merchant Tables ────────────────────────────────
        fig = plt.figure(figsize=(11.69, 8.27))
        fig.patch.set_facecolor("#1E1E2E")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#1E1E2E")
        ax.axis("off")

        ax.text(0.5, 0.95, "Detailed Spending Breakdown", transform=ax.transAxes,
                fontsize=18, fontweight="bold", color="white", ha="center")

        # Category table
        cat_display = cats[["Category", "Total", "Transactions", "Percentage"]].head(10).copy()
        cat_display["Total"] = cat_display["Total"].apply(lambda x: f"₹{x:,.0f}")
        cat_display["Percentage"] = cat_display["Percentage"].apply(lambda x: f"{x:.1f}%")

        table1 = ax.table(
            cellText=cat_display.values,
            colLabels=cat_display.columns,
            cellLoc="center", loc="upper left",
            bbox=[0.0, 0.50, 0.48, 0.40],
        )
        _style_table(table1)

        # Merchant table
        merch_display = merchants[["Merchant", "Total_Spent", "Transactions"]].copy()
        merch_display["Total_Spent"] = merch_display["Total_Spent"].apply(lambda x: f"₹{x:,.0f}")

        table2 = ax.table(
            cellText=merch_display.values,
            colLabels=merch_display.columns,
            cellLoc="center", loc="upper right",
            bbox=[0.52, 0.50, 0.48, 0.40],
        )
        _style_table(table2)

        ax.text(0.24, 0.48, "Top Categories", transform=ax.transAxes,
                fontsize=11, fontweight="bold", color="white", ha="center")
        ax.text(0.76, 0.48, "Top Merchants", transform=ax.transAxes,
                fontsize=11, fontweight="bold", color="white", ha="center")

        # All insights
        ax.text(0.5, 0.42, "Automated Insights", transform=ax.transAxes,
                fontsize=14, fontweight="bold", color="white", ha="center")
        for k, insight in enumerate(insights[:6]):
            clean = insight.replace("**", "")
            for em in ["💸", "📅", "📆", "🏪", "📊", "🍔", "⚠️", "✅", "📺"]:
                clean = clean.replace(em, "")
            ax.text(0.05, 0.36 - k * 0.055, f"• {clean[:100]}", transform=ax.transAxes,
                    fontsize=8, color="#CCCCCC")

        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

    buf.seek(0)
    return buf.read()


def _style_table(table):
    """Apply dark theme styling to a matplotlib table."""
    for (row, col), cell in table.get_celld().items():
        cell.set_facecolor("#1E1E2E" if row > 0 else "#6C63FF")
        cell.set_text_props(color="white" if row > 0 else "white", fontsize=8)
        cell.set_edgecolor("#444444")


def generate_csv_report(df: pd.DataFrame, budgets: dict = None) -> bytes:
    """Generate a comprehensive CSV summary report."""
    buf = io.BytesIO()

    summary = generate_summary(df)
    cats = category_spending(df)
    monthly = monthly_spending(df)
    merchants = top_merchants(df, n=10)

    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        # Raw data
        df.drop(columns=["Year", "Month", "Day", "Day_of_Week", "Is_Weekend",
                          "Week_Number", "YearMonth", "Month_Name"],
                errors="ignore").to_excel(writer, sheet_name="Transactions", index=False)

        # Summary
        summary_df = pd.DataFrame([{
            "Metric": k.replace("_", " ").title(),
            "Value": str(v),
        } for k, v in summary.items() if not isinstance(v, dict)])
        summary_df.to_excel(writer, sheet_name="Summary", index=False)

        cats.to_excel(writer, sheet_name="Category_Breakdown", index=False)
        monthly.to_excel(writer, sheet_name="Monthly_Trends", index=False)
        merchants.to_excel(writer, sheet_name="Top_Merchants", index=False)

        if budgets:
            from src.analytics.expense_analysis import budget_vs_actual
            years = df["Year"].unique()
            months = df["Month"].unique()
            bdf = budget_vs_actual(df, budgets, int(years[-1]), int(months[-1]))
            bdf.to_excel(writer, sheet_name="Budget_Tracking", index=False)

    buf.seek(0)
    return buf.read()
