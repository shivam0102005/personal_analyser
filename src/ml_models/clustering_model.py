"""
clustering_model.py
-------------------
K-Means clustering to identify spending pattern groups.
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings("ignore")


CLUSTER_LABELS = {
    0: "🍔 Food-Heavy Spender",
    1: "🛍️ Shopping Enthusiast",
    2: "⚖️ Balanced Spender",
    3: "🚗 Transport-Heavy",
    4: "🎮 Entertainment Lover",
}


def build_user_spending_profile(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a spending-profile vector per month.
    Each row = one (Year, Month) observation.
    Each column = spending in a category.
    """
    from src.analytics.expense_analysis import get_debit_df
    debits = get_debit_df(df)

    pivot = debits.pivot_table(
        index=["Year", "Month"],
        columns="Category",
        values="Amount",
        aggfunc="sum",
        fill_value=0,
    ).reset_index()

    return pivot


def cluster_spending_patterns(df: pd.DataFrame, n_clusters: int = 3) -> dict:
    """
    Run K-Means clustering on monthly spending profiles.

    Returns
    -------
    dict with keys:
        'cluster_df'   – DataFrame with cluster assignments
        'pca_df'       – 2-D PCA projection for scatter plot
        'cluster_stats'– per-cluster summary stats
        'n_clusters'   – actual number of clusters used
    """
    profile = build_user_spending_profile(df)

    feature_cols = [c for c in profile.columns if c not in ["Year", "Month"]]
    if not feature_cols or len(profile) < n_clusters:
        return {
            "cluster_df": profile,
            "pca_df": pd.DataFrame(),
            "cluster_stats": pd.DataFrame(),
            "n_clusters": 0,
            "message": "Insufficient data for clustering (need ≥ n_clusters months).",
        }

    X = profile[feature_cols].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Automatically adjust n_clusters if too few samples
    n_clusters = min(n_clusters, len(profile))

    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)

    profile["Cluster"] = labels
    profile["Cluster_Label"] = [CLUSTER_LABELS.get(l, f"Cluster {l}") for l in labels]

    # PCA for 2-D visualisation
    n_components = min(2, X_scaled.shape[1])
    pca = PCA(n_components=n_components)
    pca_coords = pca.fit_transform(X_scaled)
    pca_df = pd.DataFrame(pca_coords, columns=["PC1", "PC2"][:n_components])
    pca_df["Cluster"] = labels
    pca_df["Cluster_Label"] = profile["Cluster_Label"].values
    pca_df["YearMonth"] = profile["Year"].astype(str) + "-" + profile["Month"].astype(str).str.zfill(2)

    # Cluster summary
    cluster_stats = (
        profile.groupby("Cluster_Label")[feature_cols]
        .mean()
        .round(2)
        .reset_index()
    )

    return {
        "cluster_df": profile,
        "pca_df": pca_df,
        "cluster_stats": cluster_stats,
        "n_clusters": n_clusters,
        "message": f"Successfully identified {n_clusters} spending clusters.",
    }


def get_current_cluster(cluster_result: dict) -> str:
    """Return the cluster label for the most recent month."""
    cdf = cluster_result.get("cluster_df", pd.DataFrame())
    if cdf.empty:
        return "Unknown"
    latest = cdf.sort_values(["Year", "Month"]).iloc[-1]
    return latest.get("Cluster_Label", "Unknown")
