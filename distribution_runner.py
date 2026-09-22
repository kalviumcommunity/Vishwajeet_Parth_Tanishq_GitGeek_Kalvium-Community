"""
Module 2.28: Distribution Analysis for Business Trends - Runner & Validator
Computes summary statistics, skewness, and kurtosis; visualizes histograms, KDE, and segment comparisons;
and validates business interpretations for revenue distributions.
"""
import os
import sys
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server / script execution
import matplotlib.pyplot as plt
import sqlalchemy
from init_db import DB_PATH, init_database

# Ensure UTF-8 output on Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure database exists
if not os.path.exists(DB_PATH):
    init_database(DB_PATH)

engine = sqlalchemy.create_engine(f'duckdb:///{DB_PATH}')


def load_revenue_data() -> pd.DataFrame:
    """Load customer revenue distribution dataset from DuckDB or CSV."""
    try:
        df = pd.read_sql("SELECT * FROM customer_revenue ORDER BY customer_id", engine)
    except Exception:
        csv_path = os.path.join(os.path.dirname(__file__), 'data', 'customer_revenue.csv')
        df = pd.read_csv(csv_path)
    return df


def run_distribution_analysis():
    print("==================================================================")
    print(">>> MODULE 2.28: DISTRIBUTION ANALYSIS FOR BUSINESS TRENDS <<<")
    print("==================================================================")

    df = load_revenue_data()
    rev = df['revenue']
    total_customers = len(df)

    # ------------------------------------------------------------------
    # Task 1: Summary Statistics & Central Tendency Comparison
    # ------------------------------------------------------------------
    print("\n------------------------------------------------------------------")
    print("Task 1: Summary Statistics & Central Tendency Comparison")
    print("------------------------------------------------------------------")
    mean_val = rev.mean()
    median_val = rev.median()
    std_val = rev.std()
    q25 = rev.quantile(0.25)
    q75 = rev.quantile(0.75)
    iqr_val = q75 - q25
    under_500_pct = (rev < 500.0).mean() * 100

    print(f"Total Customer Records: {total_customers}")
    print(f"Mean Revenue:           ${mean_val:,.2f}")
    print(f"Median Revenue:         ${median_val:,.2f}")
    print(f"Standard Deviation:     ${std_val:,.2f}")
    print(f"25th Percentile (Q1):   ${q25:,.2f}")
    print(f"75th Percentile (Q3):   ${q75:,.2f}")
    print(f"Interquartile Range:    ${iqr_val:,.2f}")
    print(f"Customers Under $500:   {under_500_pct:.1f}%")

    print("\n[Business Insight - Central Tendency Pitfall]:")
    print(f"  Reporting an 'average customer spend' of ${mean_val:,.2f} is dangerously misleading.")
    print(f"  In reality, {under_500_pct:.1f}% of customers spend under $500, with a median of ${median_val:,.2f}.")
    print("  The mean is inflated by a small cohort of high-value enterprise accounts.")

    # ------------------------------------------------------------------
    # Task 2: Skewness, Kurtosis & Statistical Interpretation
    # ------------------------------------------------------------------
    print("\n------------------------------------------------------------------")
    print("Task 2: Skewness, Kurtosis & Statistical Interpretation")
    print("------------------------------------------------------------------")
    skewness = stats.skew(rev)
    kurtosis = stats.kurtosis(rev)

    print(f"Skewness: {skewness:.2f}")
    print(f"Kurtosis: {kurtosis:.2f}")

    print("\nStatistical Rule-Based Interpretations:")
    if abs(skewness) > 1:
        print("  ✓ Highly skewed - use median")
    else:
        print("  ✓ Moderately symmetric - mean is acceptable")

    if kurtosis > 3:
        print("  ✓ Heavy tails - expect outliers")
    else:
        print("  ✓ Light tails - outliers infrequent")

    print("\n[Business Interpretation]:")
    print(f"  Positive Skewness ({skewness:.2f} > 1.0): Tail extends far to the right.")
    print("  Most customers generate modest revenue, while a handful of huge accounts generate massive spend.")
    print(f"  High Kurtosis ({kurtosis:.2f} > 3.0): Leptokurtic distribution with extreme tail risk/opportunity.")
    print("  Budgeting and forecasting must use median and segment-specific models, not global mean.")

    # ------------------------------------------------------------------
    # Task 3: Visualizing Distributions (Histogram & KDE)
    # ------------------------------------------------------------------
    print("\n------------------------------------------------------------------")
    print("Task 3: Visualizing Distributions (Histogram & KDE)")
    print("------------------------------------------------------------------")
    plots_dir = os.path.join(os.path.dirname(__file__), 'public')
    os.makedirs(plots_dir, exist_ok=True)
    plot_filepath = os.path.join(plots_dir, 'distribution_analysis.png')

    fig, axes = plt.subplots(2, 2, figsize=(15, 11))
    fig.suptitle('Module 2.28: Distribution Analysis for Business Trends', fontsize=16, fontweight='bold', y=0.98)

    # Plot 1: Histogram (Buckets)
    axes[0, 0].hist(rev, bins=50, edgecolor='black', color='#3b82f6', alpha=0.8)
    axes[0, 0].axvline(mean_val, color='#ef4444', linestyle='dashed', linewidth=2, label=f'Mean (${mean_val:,.0f})')
    axes[0, 0].axvline(median_val, color='#10b981', linestyle='solid', linewidth=2, label=f'Median (${median_val:,.0f})')
    axes[0, 0].set_title('1. Histogram: Revenue Distribution (50 Buckets)', fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel('Revenue ($)')
    axes[0, 0].set_ylabel('Customer Count')
    axes[0, 0].legend()
    axes[0, 0].grid(True, linestyle=':', alpha=0.6)

    # Plot 2: KDE (Smoothed Density)
    rev.plot(kind='density', ax=axes[0, 1], color='#6366f1', linewidth=2.5)
    axes[0, 1].axvline(mean_val, color='#ef4444', linestyle='dashed', linewidth=1.8, label=f'Mean (${mean_val:,.0f})')
    axes[0, 1].axvline(median_val, color='#10b981', linestyle='solid', linewidth=1.8, label=f'Median (${median_val:,.0f})')
    axes[0, 1].set_title('2. Kernel Density Estimate (Smoothed True Shape)', fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel('Revenue ($)')
    axes[0, 1].set_ylabel('Density')
    axes[0, 1].legend()
    axes[0, 1].grid(True, linestyle=':', alpha=0.6)

    # ------------------------------------------------------------------
    # Task 4: Segment Comparison
    # ------------------------------------------------------------------
    print("\n------------------------------------------------------------------")
    print("Task 4: Comparing Segments (High-Value vs Low-Value & SMB vs Enterprise)")
    print("------------------------------------------------------------------")
    # High-value vs low-value customers (Q3 vs Q1)
    high_value = df[rev > q75]
    low_value = df[rev < q25]

    print(f"High-Value Segment (Top 25% > ${q75:,.2f}): {len(high_value)} customers")
    print(f"  Mean: ${high_value['revenue'].mean():,.2f} | Median: ${high_value['revenue'].median():,.2f}")
    print(f"Low-Value Segment (Bottom 25% < ${q25:,.2f}): {len(low_value)} customers")
    print(f"  Mean: ${low_value['revenue'].mean():,.2f} | Median: ${low_value['revenue'].median():,.2f}")

    axes[1, 0].hist(high_value['revenue'], alpha=0.6, label=f'High-Value (>Q3, n={len(high_value)})', bins=30, color='#f59e0b', edgecolor='black')
    axes[1, 0].hist(low_value['revenue'], alpha=0.6, label=f'Low-Value (<Q1, n={len(low_value)})', bins=30, color='#06b6d4', edgecolor='black')
    axes[1, 0].set_title('3. Segment Comparison: High-Value vs. Low-Value', fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel('Revenue ($)')
    axes[1, 0].set_ylabel('Count')
    axes[1, 0].legend()
    axes[1, 0].grid(True, linestyle=':', alpha=0.6)

    # Plot 4: Customer Type (Bimodal Decomposition: Small Business vs Enterprise)
    smb_df = df[df['customer_type'] == 'Small Business']
    ent_df = df[df['customer_type'] == 'Enterprise']

    print(f"\nBimodal Segmentation Analysis:")
    print(f"  Small Business (n={len(smb_df)}): Mean=${smb_df['revenue'].mean():,.2f}, Median=${smb_df['revenue'].median():,.2f}")
    print(f"  Enterprise     (n={len(ent_df)}): Mean=${ent_df['revenue'].mean():,.2f}, Median=${ent_df['revenue'].median():,.2f}")

    axes[1, 1].hist(smb_df['revenue'], alpha=0.6, label=f'Small Business (n={len(smb_df)})', bins=30, color='#3b82f6', edgecolor='black')
    axes[1, 1].hist(ent_df['revenue'], alpha=0.6, label=f'Enterprise (n={len(ent_df)})', bins=30, color='#ec4899', edgecolor='black')
    axes[1, 1].set_title('4. Bimodal Decomposition: SMB vs. Enterprise', fontsize=12, fontweight='bold')
    axes[1, 1].set_xlabel('Revenue ($)')
    axes[1, 1].set_ylabel('Count')
    axes[1, 1].legend()
    axes[1, 1].grid(True, linestyle=':', alpha=0.6)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(plot_filepath, dpi=300)
    plt.close()
    print(f"\n✓ Distribution plots saved to: {plot_filepath}")

    # ------------------------------------------------------------------
    # Task 5: Automated Verification Assertions
    # ------------------------------------------------------------------
    print("\n------------------------------------------------------------------")
    print("Task 5: Running Automated Assertions")
    print("------------------------------------------------------------------")
    assert total_customers == 1000, f"Expected 1,000 customers, got {total_customers}"
    assert abs(mean_val - 5000.0) < 100.0, f"Expected mean near $5,000, got {mean_val}"
    assert abs(median_val - 450.0) < 50.0, f"Expected median near $450, got {median_val}"
    assert under_500_pct >= 75.0, f"Expected >= 75% customers under $500, got {under_500_pct}%"
    assert skewness > 1.0, f"Expected highly positive skewness (> 1.0), got {skewness}"
    assert kurtosis > 3.0, f"Expected heavy-tailed kurtosis (> 3.0), got {kurtosis}"
    assert os.path.exists(plot_filepath), f"Expected plot file at {plot_filepath}"
    assert os.path.getsize(plot_filepath) > 10000, "Plot file is too small or corrupt"
    print("✓ All distribution assertions verified successfully!")
    print("==================================================================\n")


if __name__ == '__main__':
    run_distribution_analysis()
