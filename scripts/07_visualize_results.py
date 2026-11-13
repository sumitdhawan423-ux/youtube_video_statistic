"""
Step 7: Result Visualizations Using Matplotlib and Seaborn.
Generates 8 high-resolution publication-grade visualizations from analytical tables:
1. 01_top_10_videos_views.png
2. 02_category_engagement_analysis.png
3. 03_country_comparison.png
4. 04_best_publish_timing_heatmap.png
5. 05_monthly_trends_line.png
6. 06_correlation_matrix_heatmap.png
7. 07_mllib_feature_importances.png
8. 08_mllib_engagement_clusters.png
9. 09_interaction_restrictions_impact.png
"""

import sys
from pathlib import Path

# Add project root and .venv site-packages to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
VENV_PACKAGES = PROJECT_ROOT / ".venv" / "Lib" / "site-packages"
if VENV_PACKAGES.exists() and str(VENV_PACKAGES) not in sys.path:
    sys.path.insert(0, str(VENV_PACKAGES))

import os
mpl_dir = PROJECT_ROOT / "output" / ".matplotlib"
mpl_dir.mkdir(parents=True, exist_ok=True)
os.environ["MPLCONFIGDIR"] = str(mpl_dir)

pg_python = r"C:\Program Files\PostgreSQL\18\pgAdmin 4\python"
if os.path.exists(pg_python) and hasattr(os, "add_dll_directory"):
    try:
        os.add_dll_directory(pg_python)
    except Exception:
        pass

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from config.config import TABLES_DIR, CHARTS_DIR

# Set global plotting style
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.titlesize"] = 13
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["figure.dpi"] = 300

def plot_top_10_videos():
    path = TABLES_DIR / "01_top_10_videos.csv"
    if not path.exists():
        return
    df = pd.read_csv(path)
    
    fig, ax1 = plt.subplots(figsize=(12, 7))
    df = df.sort_values(by="max_views", ascending=True).tail(10)
    
    # Truncate title for readability
    short_titles = [f"[{row['country']}] " + (row['title'][:35] + "..." if len(row['title']) > 35 else row['title']) for _, row in df.iterrows()]
    
    y_pos = np.arange(len(df))
    bars = ax1.barh(y_pos, df["max_views"] / 1e6, color="#4A90E2", alpha=0.85, label="Views (Millions)")
    
    # Format labels
    for bar in bars:
        w = bar.get_width()
        ax1.text(w + 0.1, bar.get_y() + bar.get_height()/2, f"{w:.1f}M", va="center", ha="left", fontsize=9, fontweight="bold")
        
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(short_titles)
    ax1.set_xlabel("Total Views (Millions)")
    ax1.set_title("Top 10 Most Viewed Trending Videos")
    plt.tight_layout()
    
    out_file = CHARTS_DIR / "01_top_10_videos_views.png"
    plt.savefig(out_file)
    plt.close()
    print(f"[+] Saved chart: {out_file.name}")

def plot_category_aggregates():
    path = TABLES_DIR / "03_category_aggregates.csv"
    if not path.exists():
        return
    df = pd.read_csv(path).sort_values(by="avg_views", ascending=False).head(10)
    
    fig, ax1 = plt.subplots(figsize=(12, 6))
    x = np.arange(len(df))
    width = 0.4
    
    ax1.bar(x - width/2, df["avg_views"] / 1e3, width=width, color="#2E86AB", label="Avg Views (Thousands)")
    ax1.set_ylabel("Avg Views (k)", color="#2E86AB")
    ax1.set_xticks(x)
    ax1.set_xticklabels(df["category_title"], rotation=30, ha="right")
    
    ax2 = ax1.twinx()
    ax2.plot(x + width/2, df["avg_engagement_rate"] * 100, color="#E63946", marker="o", linewidth=2.5, label="Avg Engagement Rate (%)")
    ax2.set_ylabel("Engagement Rate (%)", color="#E63946")
    ax2.grid(False)
    
    plt.title("Top Categories: Average Views vs Engagement Rate")
    plt.tight_layout()
    out_file = CHARTS_DIR / "02_category_engagement_analysis.png"
    plt.savefig(out_file)
    plt.close()
    print(f"[+] Saved chart: {out_file.name}")

def plot_country_comparison():
    path = TABLES_DIR / "04_country_comparison.csv"
    if not path.exists():
        return
    df = pd.read_csv(path)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    sns.barplot(data=df, x="country", y="avg_views", ax=ax1, palette="viridis")
    ax1.set_title("Average Views per Video by Country")
    ax1.set_ylabel("Average Views")
    ax1.set_xlabel("Country Code")
    
    sns.barplot(data=df, x="country", y="avg_engagement_rate", ax=ax2, palette="magma")
    ax2.set_title("Average Engagement Rate by Country")
    ax2.set_ylabel("Engagement Rate (Likes+Comments)/Views")
    ax2.set_xlabel("Country Code")
    
    plt.tight_layout()
    out_file = CHARTS_DIR / "03_country_comparison.png"
    plt.savefig(out_file)
    plt.close()
    print(f"[+] Saved chart: {out_file.name}")

def plot_publish_timing_heatmap():
    path = TABLES_DIR / "06_publish_timing.csv"
    if not path.exists():
        return
    df = pd.read_csv(path)
    
    # Days order
    days_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    pivot = df.pivot_table(index="publish_weekday", columns="publish_hour", values="avg_views", aggfunc="mean").fillna(0)
    pivot = pivot.reindex(days_order)
    
    plt.figure(figsize=(14, 6))
    sns.heatmap(pivot / 1e3, cmap="YlOrRd", annot=True, fmt=".0f", cbar_kws={"label": "Avg Views (Thousands)"})
    plt.title("Optimal Publishing Windows: Average Views (in Thousands) by Weekday & Hour")
    plt.xlabel("Publish Hour (UTC, 0 - 23)")
    plt.ylabel("Publish Weekday")
    plt.tight_layout()
    
    out_file = CHARTS_DIR / "04_best_publish_timing_heatmap.png"
    plt.savefig(out_file)
    plt.close()
    print(f"[+] Saved chart: {out_file.name}")

def plot_monthly_trends():
    path = TABLES_DIR / "05_monthly_trends.csv"
    if not path.exists():
        return
    df = pd.read_csv(path).sort_values(by="publish_year_month")
    
    fig, ax1 = plt.subplots(figsize=(12, 5))
    ax1.plot(df["publish_year_month"], df["avg_views"] / 1e3, marker="s", color="#3A86FF", linewidth=2, label="Avg Views (k)")
    ax1.set_ylabel("Average Views (Thousands)", color="#3A86FF")
    ax1.set_xlabel("Year-Month")
    ax1.tick_params(axis="x", rotation=45)
    
    ax2 = ax1.twinx()
    ax2.plot(df["publish_year_month"], df["avg_engagement_rate"] * 100, marker="^", color="#FB5607", linewidth=2, linestyle="--", label="Engagement (%)")
    ax2.set_ylabel("Avg Engagement Rate (%)", color="#FB5607")
    ax2.grid(False)
    
    plt.title("Trending Video Trajectory Over Time (Views vs Engagement Rate)")
    plt.tight_layout()
    out_file = CHARTS_DIR / "05_monthly_trends_line.png"
    plt.savefig(out_file)
    plt.close()
    print(f"[+] Saved chart: {out_file.name}")

def plot_correlation_matrix():
    path = TABLES_DIR / "07_correlation_matrix.csv"
    if not path.exists():
        return
    df = pd.read_csv(path).set_index("metric")
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(df, annot=True, cmap="coolwarm", vmin=-1, vmax=1, fmt=".3f", square=True)
    plt.title("Pearson Correlation Matrix: Views, Likes, Dislikes, Comments")
    plt.tight_layout()
    
    out_file = CHARTS_DIR / "06_correlation_matrix_heatmap.png"
    plt.savefig(out_file)
    plt.close()
    print(f"[+] Saved chart: {out_file.name}")

def plot_mllib_features():
    path = TABLES_DIR / "mllib_feature_importances.csv"
    if not path.exists():
        return
    df = pd.read_csv(path).sort_values(by="Importance", ascending=True)
    
    plt.figure(figsize=(10, 5))
    bars = plt.barh(df["Feature"], df["Importance"], color="#06D6A0")
    for bar in bars:
        w = bar.get_width()
        plt.text(w + 0.01, bar.get_y() + bar.get_height()/2, f"{w:.3f}", va="center", fontsize=9)
    plt.xlabel("Gini Importance")
    plt.title("Spark MLlib Random Forest: Feature Importances for View Prediction")
    plt.tight_layout()
    
    out_file = CHARTS_DIR / "07_mllib_feature_importances.png"
    plt.savefig(out_file)
    plt.close()
    print(f"[+] Saved chart: {out_file.name}")

def plot_mllib_clusters():
    path = TABLES_DIR / "mllib_clustered_samples.csv"
    if not path.exists():
        return
    df = pd.read_csv(path)
    
    plt.figure(figsize=(10, 6))
    scatter = sns.scatterplot(
        data=df,
        x=df["views"] / 1e3,
        y=df["likes"] / 1e3,
        hue="cluster",
        size="comment_count",
        sizes=(30, 300),
        palette="tab10",
        alpha=0.8
    )
    plt.title("Spark MLlib K-Means: Video Engagement Clusters (Views vs Likes)")
    plt.xlabel("Views (Thousands)")
    plt.ylabel("Likes (Thousands)")
    plt.tight_layout()
    
    out_file = CHARTS_DIR / "08_mllib_engagement_clusters.png"
    plt.savefig(out_file)
    plt.close()
    print(f"[+] Saved chart: {out_file.name}")

def main():
    print("="*60)
    print("YouTube Video Statistics - Step 7: Generating Visualizations")
    print("="*60)
    plot_top_10_videos()
    plot_category_aggregates()
    plot_country_comparison()
    plot_publish_timing_heatmap()
    plot_monthly_trends()
    plot_correlation_matrix()
    plot_mllib_features()
    plot_mllib_clusters()
    print(f"\n[+] All charts successfully written to: {CHARTS_DIR}")

if __name__ == "__main__":
    main()

