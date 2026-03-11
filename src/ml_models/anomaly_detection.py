"""
anomaly_detection.py
--------------------
Detects unusual / suspicious transactions using:
  - Z-score method
  - Isolation Forest (sklearn)
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings("ignore")


def zscore_anomalies(df: pd.DataFrame, threshold: float = 2.5) -> pd.DataFrame:
    """
    Flag transactions whose amount is more than `threshold` standard deviations
    from the per-category mean.
    """
    from src.analytics.expense_analysis import get_debit_df
    debits = get_debit_df(df).copy()

    debits["Cat_Mean"] = debits.groupby("Category")["Amount"].transform("mean")
    debits["Cat_Std"] = debits.groupby("Category")["Amount"].transform("std").fillna(1)
    debits["Z_Score"] = (debits["Amount"] - debits["Cat_Mean"]) / debits["Cat_Std"]
    debits["Is_Anomaly_Z"] = debits["Z_Score"].abs() > threshold

    anomalies = debits[debits["Is_Anomaly_Z"]].copy()
    anomalies["Anomaly_Method"] = "Z-Score"
    anomalies["Anomaly_Reason"] = anomalies.apply(
        lambda r: (
            f"₹{r['Amount']:,.0f} in {r['Category']} is "
            f"{r['Z_Score']:.1f}σ above the category mean of ₹{r['Cat_Mean']:,.0f}"
        ),
        axis=1
    )
    return anomalies[["Date", "Description", "Category", "Amount", "Merchant",
                       "Anomaly_Method", "Anomaly_Reason"]].reset_index(drop=True)


def isolation_forest_anomalies(df: pd.DataFrame, contamination: float = 0.05) -> pd.DataFrame:
    """
    Use Isolation Forest to detect anomalous transactions.
    Features: Amount, Category (encoded), Day_of_Week (encoded).
    """
    from src.analytics.expense_analysis import get_debit_df
    debits = get_debit_df(df).copy()

    if len(debits) < 10:
        return pd.DataFrame()

    le_cat = LabelEncoder()
    le_dow = LabelEncoder()
    debits["Cat_Enc"] = le_cat.fit_transform(debits["Category"].astype(str))
    debits["DoW_Enc"] = le_dow.fit_transform(debits["Day_of_Week"].astype(str))

    X = debits[["Amount", "Cat_Enc", "DoW_Enc"]].values

    iso = IsolationForest(contamination=contamination, random_state=42, n_estimators=100)
    debits["IF_Score"] = iso.fit_predict(X)  # -1 = anomaly, 1 = normal
    debits["IF_Decision"] = iso.decision_function(X)

    anomalies = debits[debits["IF_Score"] == -1].copy()
    anomalies["Anomaly_Method"] = "Isolation Forest"
    anomalies["Anomaly_Reason"] = anomalies.apply(
        lambda r: (
            f"Unusual ₹{r['Amount']:,.0f} transaction at {r['Merchant']} "
            f"flagged by anomaly detection model."
        ),
        axis=1
    )
    return anomalies[["Date", "Description", "Category", "Amount", "Merchant",
                       "Anomaly_Method", "Anomaly_Reason"]].reset_index(drop=True)


def detect_all_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """Combine both detection methods and deduplicate."""
    z_anomalies = zscore_anomalies(df)
    if_anomalies = isolation_forest_anomalies(df)

    combined = pd.concat([z_anomalies, if_anomalies], ignore_index=True)
    # Deduplicate by date + description + amount
    combined = combined.drop_duplicates(subset=["Date", "Description", "Amount"])
    return combined.sort_values("Amount", ascending=False).reset_index(drop=True)


def format_anomaly_alerts(anomalies: pd.DataFrame) -> list:
    """Convert anomaly rows into human-readable alert strings."""
    alerts = []
    for _, row in anomalies.iterrows():
        alerts.append(
            f"🚨 **Suspicious Transaction Detected** ({row['Anomaly_Method']})\n"
            f"   {row['Date'].strftime('%d %b %Y') if hasattr(row['Date'], 'strftime') else row['Date']} | "
            f"{row['Description']} | ₹{row['Amount']:,.0f}\n"
            f"   Reason: {row['Anomaly_Reason']}"
        )
    return alerts
