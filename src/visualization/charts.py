"""
charts.py
---------
All chart-generation functions for the Personal Finance Analyzer.
Returns Plotly figures (for Streamlit) or Matplotlib figures (for PDF reports).
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns

# ─── Color Palette ────────────────────────────────────────────────────────────
PALETTE = px.colors.qualitative.Pastel
PRIMARY = "#6C63FF"
BACKGROUND = "#0E1117"
CARD_BG = "#1E1E2E"

sns.set_theme(style="darkgrid", palette="pastel")


# ─── Plotly Charts ────────────────────────────────────────────────────────────

def pie_chart_categories(df: pd.DataFrame) -> go.Figure:
    """Pie chart of category-wise spending distribution."""
    from src.analytics.expense_analysis import category_spending
    cats = category_spending(df)
    fig = px.pie(
        cats, names="Category", values="Total",
        title="💰 Spending by Category",
        color_discrete_sequence=PALETTE,
        hole=0.4,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(paper_bgcolor=CARD_BG, font_color="white", title_x=0.5)
    return fig


def bar_chart_top_categories(df: pd.DataFrame, top_n: int = 8) -> go.Figure:
    """Horizontal bar chart of top spending categories."""
    from src.analytics.expense_analysis import category_spending
    cats = category_spending(df).head(top_n)
    fig = px.bar(
        cats, x="Total", y="Category", orientation="h",
        title=f"📊 Top {top_n} Spending Categories",
        color="Total", color_continuous_scale="Viridis",
        text="Total",
    )
    fig.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
    fig.update_layout(
        paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
        font_color="white", title_x=0.5, showlegend=False,
        yaxis={"categoryorder": "total ascending"},
        coloraxis_showscale=False,
    )
    return fig


def line_chart_daily_spending(df: pd.DataFrame) -> go.Figure:
    """Line chart of daily spending with 7-day rolling average."""
    from src.analytics.expense_analysis import daily_spending
    daily = daily_spending(df)
    daily["Rolling_7"] = daily["Daily_Total"].rolling(7, min_periods=1).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily["Date"], y=daily["Daily_Total"],
        mode="lines", name="Daily Spend",
        line=dict(color="#A8EDEA", width=1.5),
        opacity=0.6,
    ))
    fig.add_trace(go.Scatter(
        x=daily["Date"], y=daily["Rolling_7"],
        mode="lines", name="7-Day Avg",
        line=dict(color="#FED6E3", width=2.5),
    ))
    fig.update_layout(
        title="📈 Daily Spending Trend", title_x=0.5,
        paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
        font_color="white",
        xaxis_title="Date", yaxis_title="Amount (₹)",
        hovermode="x unified",
    )
    return fig


def stacked_bar_monthly_categories(df: pd.DataFrame) -> go.Figure:
    """Stacked bar chart showing monthly spending by category."""
    from src.analytics.expense_analysis import monthly_category_spending
    pivot = monthly_category_spending(df)
    cat_cols = [c for c in pivot.columns if c != "YearMonth"]

    fig = go.Figure()
    for i, cat in enumerate(cat_cols):
        fig.add_trace(go.Bar(
            name=cat,
            x=pivot["YearMonth"],
            y=pivot[cat],
            marker_color=PALETTE[i % len(PALETTE)],
        ))
    fig.update_layout(
        barmode="stack",
        title="📅 Monthly Category Breakdown",
        title_x=0.5,
        paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
        font_color="white",
        xaxis_title="Month", yaxis_title="Amount (₹)",
        legend=dict(orientation="h", yanchor="bottom", y=-0.5),
    )
    return fig


def heatmap_spending_intensity(df: pd.DataFrame) -> go.Figure:
    """Heatmap of spending intensity (Day of Week × Week Number)."""
    from src.analytics.expense_analysis import spending_heatmap_data
    pivot = spending_heatmap_data(df)
    if pivot.empty:
        return go.Figure()

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=[f"W{c}" for c in pivot.columns],
        y=pivot.index.tolist(),
        colorscale="YlOrRd",
        colorbar=dict(title="₹ Spent"),
    ))
    fig.update_layout(
        title="🌡️ Spending Intensity Heatmap",
        title_x=0.5,
        paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
        font_color="white",
        xaxis_title="Week Number", yaxis_title="Day of Week",
    )
    return fig


def bar_chart_monthly_spending(df: pd.DataFrame) -> go.Figure:
    """Monthly total spending bar chart with MoM change annotation."""
    from src.analytics.expense_analysis import monthly_spending
    monthly = monthly_spending(df)

    colors = [PRIMARY if c >= 0 else "#FF6B6B"
              for c in monthly["MoM_Change_Pct"].fillna(0)]

    fig = go.Figure(go.Bar(
        x=monthly["YearMonth"],
        y=monthly["Total_Spending"],
        marker_color=colors,
        text=monthly["Total_Spending"].apply(lambda x: f"₹{x:,.0f}"),
        textposition="outside",
    ))
    fig.update_layout(
        title="🗓️ Monthly Total Spending",
        title_x=0.5,
        paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
        font_color="white",
        xaxis_title="Month", yaxis_title="Total Spending (₹)",
    )
    return fig


def bar_chart_top_merchants(df: pd.DataFrame, n: int = 10) -> go.Figure:
    """Bar chart of top N merchants by spend."""
    from src.analytics.expense_analysis import top_merchants
    merchants = top_merchants(df, n=n)
    fig = px.bar(
        merchants, x="Merchant", y="Total_Spent",
        title=f"🏪 Top {n} Merchants by Spend",
        color="Total_Spent", color_continuous_scale="Teal",
        text="Total_Spent",
    )
    fig.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
    fig.update_layout(
        paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
        font_color="white", title_x=0.5,
        coloraxis_showscale=False,
    )
    return fig


def scatter_cluster_plot(pca_df: pd.DataFrame) -> go.Figure:
    """2-D scatter plot of spending clusters (PCA-reduced)."""
    if pca_df.empty or "PC1" not in pca_df.columns:
        return go.Figure()

    fig = px.scatter(
        pca_df, x="PC1", y="PC2",
        color="Cluster_Label",
        hover_data=["YearMonth"] if "YearMonth" in pca_df.columns else None,
        title="🔍 Spending Pattern Clusters",
        color_discrete_sequence=PALETTE,
    )
    fig.update_traces(marker_size=12)
    fig.update_layout(
        paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
        font_color="white", title_x=0.5,
    )
    return fig


def budget_gauge_chart(category: str, actual: float, budget: float) -> go.Figure:
    """Gauge chart showing budget utilisation for a single category."""
    pct = min((actual / budget * 100), 150) if budget > 0 else 0
    color = "#2ECC71" if pct <= 80 else "#F39C12" if pct <= 100 else "#E74C3C"

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=actual,
        number={"prefix": "₹", "valueformat": ",.0f"},
        delta={"reference": budget, "increasing": {"color": "#E74C3C"}, "prefix": "₹"},
        title={"text": f"{category} Budget", "font": {"color": "white"}},
        gauge={
            "axis": {"range": [0, budget * 1.5], "tickcolor": "white"},
            "bar": {"color": color},
            "bgcolor": CARD_BG,
            "steps": [
                {"range": [0, budget * 0.8], "color": "#1A1A2E"},
                {"range": [budget * 0.8, budget], "color": "#16213E"},
                {"range": [budget, budget * 1.5], "color": "#0F3460"},
            ],
            "threshold": {"line": {"color": "red", "width": 4}, "value": budget},
        },
    ))
    fig.update_layout(paper_bgcolor=CARD_BG, font_color="white", height=300)
    return fig


def bar_chart_day_of_week(df: pd.DataFrame) -> go.Figure:
    """Bar chart: average spending per day of week."""
    from src.analytics.expense_analysis import day_of_week_spending
    dow = day_of_week_spending(df)
    fig = px.bar(
        dow, x="Day_of_Week", y="Average",
        title="📅 Average Spending by Day of Week",
        color="Average", color_continuous_scale="Sunset",
        text="Average",
    )
    fig.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
    fig.update_layout(
        paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
        font_color="white", title_x=0.5, coloraxis_showscale=False,
    )
    return fig


def line_chart_prediction(historical: list, lr_pred: float, rf_pred: float) -> go.Figure:
    """Line chart showing historical spending + next-month predictions."""
    hist_df = pd.DataFrame(historical)
    if hist_df.empty:
        return go.Figure()

    hist_df["Label"] = hist_df["Year"].astype(str) + "-" + hist_df["Month"].astype(str).str.zfill(2)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist_df["Label"], y=hist_df["Total_Spending"],
        mode="lines+markers", name="Historical",
        line=dict(color="#A8EDEA", width=2),
    ))

    next_label = "Next Month"
    last_val = hist_df["Total_Spending"].iloc[-1]

    if lr_pred:
        fig.add_trace(go.Scatter(
            x=[hist_df["Label"].iloc[-1], next_label],
            y=[last_val, lr_pred],
            mode="lines+markers", name=f"LR Prediction: ₹{lr_pred:,.0f}",
            line=dict(color="#FED6E3", width=2, dash="dash"),
        ))
    if rf_pred:
        fig.add_trace(go.Scatter(
            x=[hist_df["Label"].iloc[-1], next_label],
            y=[last_val, rf_pred],
            mode="lines+markers", name=f"RF Prediction: ₹{rf_pred:,.0f}",
            line=dict(color="#D4FC79", width=2, dash="dot"),
        ))

    fig.update_layout(
        title="🔮 Next Month Spending Prediction",
        title_x=0.5,
        paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
        font_color="white", hovermode="x unified",
    )
    return fig


# ─── Matplotlib/Seaborn (for PDF reports) ────────────────────────────────────

def mpl_category_pie(df: pd.DataFrame, ax: plt.Axes = None):
    """Matplotlib pie chart for PDF report embedding."""
    from src.analytics.expense_analysis import category_spending
    cats = category_spending(df).head(8)
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
        standalone = True
    else:
        standalone = False
        fig = ax.figure

    wedges, texts, autotexts = ax.pie(
        cats["Total"], labels=cats["Category"],
        autopct="%1.1f%%", startangle=140,
        colors=sns.color_palette("pastel", len(cats)),
    )
    ax.set_title("Category-wise Spending Distribution", fontsize=14, fontweight="bold")

    if standalone:
        return fig


def mpl_monthly_bar(df: pd.DataFrame, ax: plt.Axes = None):
    """Matplotlib bar chart for monthly spending."""
    from src.analytics.expense_analysis import monthly_spending
    monthly = monthly_spending(df)
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 5))
        standalone = True
    else:
        standalone = False
        fig = ax.figure

    ax.bar(monthly["YearMonth"], monthly["Total_Spending"],
           color=sns.color_palette("viridis", len(monthly)))
    ax.set_title("Monthly Total Spending", fontsize=14, fontweight="bold")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount (₹)")
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

    if standalone:
        return fig
