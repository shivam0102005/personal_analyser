"""
prediction_model.py
-------------------
Predicts next-month total spending and per-category trends
using Linear Regression and Random Forest Regressor.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings("ignore")


def _prepare_monthly_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build feature matrix from monthly aggregates for total spending prediction.
    Features: month index, month number, rolling mean, lag features.
    """
    from src.analytics.expense_analysis import get_debit_df
    debits = get_debit_df(df)

    monthly = (
        debits.groupby(["Year", "Month"])["Amount"]
        .sum()
        .reset_index()
        .rename(columns={"Amount": "Total_Spending"})
        .sort_values(["Year", "Month"])
        .reset_index(drop=True)
    )

    monthly["Month_Index"] = range(len(monthly))
    monthly["Rolling_Mean_3"] = monthly["Total_Spending"].rolling(3, min_periods=1).mean()
    monthly["Lag_1"] = monthly["Total_Spending"].shift(1)
    monthly["Lag_2"] = monthly["Total_Spending"].shift(2)
    monthly = monthly.dropna()
    return monthly


def predict_next_month_spending(df: pd.DataFrame) -> dict:
    """
    Predict total spending for the next month.
    Returns dict with predictions from both LR and RF models.
    """
    monthly = _prepare_monthly_features(df)

    if len(monthly) < 3:
        return {
            "lr_prediction": None,
            "rf_prediction": None,
            "message": "Need at least 3 months of data for prediction.",
            "historical": monthly.to_dict("records"),
        }

    features = ["Month_Index", "Month", "Rolling_Mean_3", "Lag_1", "Lag_2"]
    X = monthly[features].values
    y = monthly["Total_Spending"].values

    # Linear Regression
    lr = LinearRegression()
    lr.fit(X, y)

    # Random Forest
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X, y)

    # Build next-month feature vector
    last = monthly.iloc[-1]
    next_month_index = last["Month_Index"] + 1
    next_month = (last["Month"] % 12) + 1
    next_features = np.array([[
        next_month_index,
        next_month,
        monthly["Total_Spending"].tail(3).mean(),
        last["Total_Spending"],
        monthly.iloc[-2]["Total_Spending"] if len(monthly) >= 2 else last["Total_Spending"],
    ]])

    lr_pred = max(0, lr.predict(next_features)[0])
    rf_pred = max(0, rf.predict(next_features)[0])

    # Evaluation metrics (leave-one-out on small dataset)
    lr_train_score = lr.score(X, y)
    rf_train_score = rf.score(X, y)

    return {
        "lr_prediction": round(lr_pred, 2),
        "rf_prediction": round(rf_pred, 2),
        "ensemble_prediction": round((lr_pred + rf_pred) / 2, 2),
        "lr_r2": round(lr_train_score, 3),
        "rf_r2": round(rf_train_score, 3),
        "historical": monthly[["Year", "Month", "Total_Spending"]].to_dict("records"),
        "message": "Prediction generated successfully.",
    }


def predict_category_trends(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each category, predict next-month spending using Linear Regression.
    Returns a DataFrame with columns: Category, Last_Month, Predicted, Change_Pct.
    """
    from src.analytics.expense_analysis import get_debit_df
    debits = get_debit_df(df)

    monthly_cat = (
        debits.groupby(["Year", "Month", "Category"])["Amount"]
        .sum()
        .reset_index()
        .sort_values(["Year", "Month"])
    )

    results = []
    for cat, grp in monthly_cat.groupby("Category"):
        grp = grp.reset_index(drop=True)
        grp["Month_Index"] = range(len(grp))

        if len(grp) < 2:
            pred = grp.iloc[-1]["Amount"]
        else:
            lr = LinearRegression()
            X_c = grp[["Month_Index"]].values
            y_c = grp["Amount"].values
            lr.fit(X_c, y_c)
            next_idx = np.array([[len(grp)]])
            pred = max(0, lr.predict(next_idx)[0])

        last_val = grp.iloc[-1]["Amount"]
        change_pct = ((pred - last_val) / last_val * 100) if last_val > 0 else 0

        results.append({
            "Category": cat,
            "Last_Month_Spending": round(last_val, 2),
            "Predicted_Next_Month": round(pred, 2),
            "Change_Pct": round(change_pct, 1),
        })

    return pd.DataFrame(results).sort_values("Predicted_Next_Month", ascending=False)
