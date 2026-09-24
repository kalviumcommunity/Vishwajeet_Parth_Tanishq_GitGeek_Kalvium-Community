"""
Module 2.30: GroupBy Aggregation & Segment Insights - Runner & Validator
Implements Split-Apply-Combine patterns, .agg(), .transform(), .apply(), multi-dimensional grouping,
pivot tables, segment ranking, actionable business insights, and visualization.
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
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


def load_segment_data() -> pd.DataFrame:
    """Load customer churn and segment dataset from DuckDB or CSV fallback."""
    try:
        df = pd.read_sql("SELECT * FROM customer_churn_segments ORDER BY customer_id", engine)
    except Exception:
        csv_path = os.path.join(os.path.dirname(__file__), 'data', 'customer_churn_segments.csv')
        df = pd.read_csv(csv_path)
    return df


def run_segment_aggregation():
    print("==================================================================")
    print(">>> MODULE 2.30: GROUPBY AGGREGATION & SEGMENT INSIGHTS <<<")
    print("==================================================================")

    df = load_segment_data()
    total_customers = len(df)
    total_revenue = df['revenue'].sum()
    blended_churn_rate = df['churn'].mean()

    # ------------------------------------------------------------------
    # Task 1: Dataset-Wide Averages vs. Segment-Specific Realities
    # ------------------------------------------------------------------
    print("\n------------------------------------------------------------------")
    print("Task 1: The Dataset-Wide Averages Fallacy vs. Segment Realities")
    print("------------------------------------------------------------------")
    print(f"Total Customer Records:     {total_customers:,}")
    print(f"Total Company Revenue:      ${total_revenue:,.2f}")
    print(f"Blended Average Churn Rate: {blended_churn_rate * 100:.2f}%")

    print("\n[Business Pitfall - The 'Average' Trap]:")
    print(f"  Reporting a blended churn rate of {blended_churn_rate * 100:.2f}% hides critical business risks.")
    print("  Leadership might assume churn is uniformly distributed across the customer base.")
    print("  In reality, high-value accounts might be flourishing while self-serve segments are collapsing.")

    # ------------------------------------------------------------------
    # Task 2: Split-Apply-Combine & Three GroupBy Methods (agg, transform, apply)
    # ------------------------------------------------------------------
    print("\n------------------------------------------------------------------")
    print("Task 2: Split-Apply-Combine Pattern (.agg, .transform, .apply)")
    print("------------------------------------------------------------------")

    # 1. .agg() - Combine results into single value per group
    agg_summary = df.groupby('customer_type')['churn'].agg(['sum', 'count', 'mean'])
    agg_summary.columns = ['churned_count', 'total_count', 'churn_rate']
    print("\n1. GroupBy .agg() Summary (Churn by Customer Type):")
    print(agg_summary.apply(lambda col: col.map(lambda v: f"{v*100:.1f}%" if col.name == 'churn_rate' else f"{v:,.0f}")))

    # 2. .transform() - Broadcast group statistic per row without reducing DataFrame dimensionality
    df['churn_rate_by_type'] = df.groupby('customer_type')['churn'].transform('mean')
    df['avg_revenue_by_type'] = df.groupby('customer_type')['revenue'].transform('mean')
    print("\n2. GroupBy .transform() Verification (Broadcast Group Mean to Rows):")
    sample_transform = df[['customer_id', 'customer_type', 'revenue', 'avg_revenue_by_type', 'churn', 'churn_rate_by_type']].iloc[[0, 150, 950]]
    print(sample_transform.to_string(index=False))

    # 3. .apply() - Custom function per group (e.g., Top-3 customer revenue contribution per segment)
    top3_revenue = df.groupby('customer_type')['revenue'].apply(lambda x: x.nlargest(3).sum())
    print("\n3. GroupBy .apply() Custom Function (Sum of Top 3 Customers per Segment):")
    for seg, val in top3_revenue.items():
        print(f"  {seg:<15}: ${val:,.2f}")

    # ------------------------------------------------------------------
    # Task 3: Multi-Dimensional Aggregation & Unstack
    # ------------------------------------------------------------------
    print("\n------------------------------------------------------------------")
    print("Task 3: Multi-Dimensional GroupBy & .unstack()")
    print("------------------------------------------------------------------")
    multi_group = df.groupby(['customer_type', 'product'])['revenue'].sum()
    unstacked_matrix = multi_group.unstack()
    print("Multi-Level GroupBy Revenue by Segment & Product (Unstacked 2D Matrix):")
    print(unstacked_matrix.map(lambda v: f"${v:,.0f}"))

    # ------------------------------------------------------------------
    # Task 4: Two-Dimensional Pivot Table
    # ------------------------------------------------------------------
    print("\n------------------------------------------------------------------")
    print("Task 4: Pivot Table for Two-Dimensional View")
    print("------------------------------------------------------------------")
    revenue_pivot = pd.pivot_table(
        df,
        values='revenue',
        index='customer_type',
        columns='product',
        aggfunc='sum'
    )
    churn_pivot = pd.pivot_table(
        df,
        values='churn',
        index='customer_type',
        columns='product',
        aggfunc='mean'
    ) * 100.0

    print("Revenue Pivot Table ($ Sum):")
    print(revenue_pivot.map(lambda v: f"${v:,.0f}"))
    print("\nChurn Rate Pivot Table (% Mean):")
    print(churn_pivot.map(lambda v: f"{v:.1f}%"))

    # ------------------------------------------------------------------
    # Task 5: Ranking Segments & Surfacing Actionable Insights
    # ------------------------------------------------------------------
    print("\n------------------------------------------------------------------")
    print("Task 5: Segment Ranking & Actionable Business Insights")
    print("------------------------------------------------------------------")
    segment_metrics = df.groupby('customer_type').agg({
        'churn': 'mean',
        'revenue': 'sum',
        'customer_id': 'count'
    })
    segment_metrics.columns = ['churn_rate', 'total_revenue', 'customer_count']

    # Compute key business shares
    segment_metrics['revenue_share_pct'] = (segment_metrics['total_revenue'] / total_revenue) * 100.0
    segment_metrics['customer_share_pct'] = (segment_metrics['customer_count'] / total_customers) * 100.0
    segment_metrics['churn_rank'] = segment_metrics['churn_rate'].rank(ascending=False)

    ranked_segments = segment_metrics.sort_values('churn_rate', ascending=False)
    print("Segment Performance Scorecard (Sorted by Churn Risk):")
    print(ranked_segments.apply(lambda col: col.map(
        lambda v: f"{v*100:.1f}%" if col.name == 'churn_rate'
        else (f"${v:,.2f}" if col.name == 'total_revenue'
        else (f"{v:.1f}%" if 'share' in col.name
        else (f"#{int(v)}" if col.name == 'churn_rank' else f"{int(v):,}")))
    )))

    print("\n[Actionable Business Insights & Strategic Interventions]:")
    interventions = {
        'Enterprise': {
            'status': 'HEALTHY & PROFITABLE',
            'action': 'Maintain high-touch white-glove support, conduct quarterly executive business reviews (QBRs), and expand multi-product adoption.'
        },
        'SMB': {
            'status': 'HIGH CHURN RISK - INTERVENTION REQUIRED',
            'action': 'Deploy automated onboarding health scores, streamline self-serve configuration, and establish trigger-based intervention workflows.'
        },
        'Startup': {
            'status': 'MODERATE CHURN - ACTIVATION FOCUS',
            'action': 'Provide self-guided developer docs, community office hours, usage-tier incentives, and in-app milestone nudges.'
        }
    }

    for seg_name, row in ranked_segments.iterrows():
        churn_pct = row['churn_rate'] * 100.0
        rev_share = row['revenue_share_pct']
        cust_share = row['customer_share_pct']
        info = interventions.get(seg_name, {'status': 'REVIEW', 'action': 'Monitor performance.'})
        print(f"\n  • Segment: {seg_name.upper()} ({info['status']})")
        print(f"    - Metrics: {churn_pct:.1f}% churn, {rev_share:.1f}% of revenue, {cust_share:.1f}% of customer base.")
        print(f"    - Action Required: {info['action']}")

    # ------------------------------------------------------------------
    # Visualizations: 4-Panel Segment Insights Dashboard
    # ------------------------------------------------------------------
    print("\n------------------------------------------------------------------")
    print("Generating Professional Visualization Dashboard...")
    print("------------------------------------------------------------------")
    plots_dir = os.path.join(os.path.dirname(__file__), 'public')
    os.makedirs(plots_dir, exist_ok=True)
    plot_filepath = os.path.join(plots_dir, 'segment_insights.png')

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Module 2.30: GroupBy Aggregation & Segment Insights', fontsize=17, fontweight='bold', y=0.98)

    # 1. Churn Rate by Segment vs Blended Average
    seg_names = list(ranked_segments.index)
    churn_vals = [ranked_segments.loc[s, 'churn_rate'] * 100 for s in seg_names]
    bar_colors = ['#ef4444' if v > 10 else ('#f59e0b' if v > 5 else '#10b981') for v in churn_vals]

    bars = axes[0, 0].bar(seg_names, churn_vals, color=bar_colors, edgecolor='black', alpha=0.85)
    axes[0, 0].axhline(blended_churn_rate * 100, color='#64748b', linestyle='--', linewidth=2, label=f'Blended Avg ({blended_churn_rate*100:.1f}%)')
    axes[0, 0].set_title('1. Churn Rate by Segment vs. Blended Benchmark', fontsize=12, fontweight='bold')
    axes[0, 0].set_ylabel('Churn Rate (%)')
    axes[0, 0].set_ylim(0, max(churn_vals) * 1.25)
    axes[0, 0].legend()
    axes[0, 0].grid(True, linestyle=':', alpha=0.6)
    for bar in bars:
        h = bar.get_height()
        axes[0, 0].text(bar.get_x() + bar.get_width() / 2., h + 0.3, f'{h:.1f}%', ha='center', va='bottom', fontweight='bold')

    # 2. Revenue Share vs. Customer Base Share (Pareto Disparity)
    x = np.arange(len(seg_names))
    width = 0.35
    rev_shares = [ranked_segments.loc[s, 'revenue_share_pct'] for s in seg_names]
    cust_shares = [ranked_segments.loc[s, 'customer_share_pct'] for s in seg_names]

    axes[0, 1].bar(x - width/2, rev_shares, width, label='Revenue Share (%)', color='#3b82f6', edgecolor='black')
    axes[0, 1].bar(x + width/2, cust_shares, width, label='Customer Share (%)', color='#93c5fd', edgecolor='black')
    axes[0, 1].set_title('2. Revenue Share vs. Customer Base Share', fontsize=12, fontweight='bold')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(seg_names)
    axes[0, 1].set_ylabel('Percentage (%)')
    axes[0, 1].legend()
    axes[0, 1].grid(True, linestyle=':', alpha=0.6)

    # 3. Two-Dimensional Revenue Heatmap by Segment & Product
    cax = axes[1, 0].matshow(revenue_pivot / 1000.0, cmap='YlGnBu')
    fig.colorbar(cax, ax=axes[1, 0], fraction=0.046, pad=0.04, label='Revenue ($ in Thousands)')
    axes[1, 0].set_xticks(range(len(revenue_pivot.columns)))
    axes[1, 0].set_xticklabels(revenue_pivot.columns, rotation=25, ha='left', fontsize=10)
    axes[1, 0].set_yticks(range(len(revenue_pivot.index)))
    axes[1, 0].set_yticklabels(revenue_pivot.index, fontsize=10)
    axes[1, 0].set_title('3. Two-Dimensional Revenue Distribution ($k)', fontsize=12, fontweight='bold', pad=15)
    for r in range(len(revenue_pivot.index)):
        for c in range(len(revenue_pivot.columns)):
            val = revenue_pivot.iloc[r, c] / 1000.0
            text_color = 'white' if val > (revenue_pivot.values.max() / 2000.0) else 'black'
            axes[1, 0].text(c, r, f"${val:,.0f}k", ha="center", va="center", color=text_color, fontweight='bold')

    # 4. Churn Rate by Segment & Product (Vulnerability Matrix)
    cax2 = axes[1, 1].matshow(churn_pivot, cmap='Reds')
    fig.colorbar(cax2, ax=axes[1, 1], fraction=0.046, pad=0.04, label='Churn Rate (%)')
    axes[1, 1].set_xticks(range(len(churn_pivot.columns)))
    axes[1, 1].set_xticklabels(churn_pivot.columns, rotation=25, ha='left', fontsize=10)
    axes[1, 1].set_yticks(range(len(churn_pivot.index)))
    axes[1, 1].set_yticklabels(churn_pivot.index, fontsize=10)
    axes[1, 1].set_title('4. Product Vulnerability Matrix (Churn %)', fontsize=12, fontweight='bold', pad=15)
    for r in range(len(churn_pivot.index)):
        for c in range(len(churn_pivot.columns)):
            val = churn_pivot.iloc[r, c]
            text_color = 'white' if val > (churn_pivot.values.max() * 0.7) else 'black'
            axes[1, 1].text(c, r, f"{val:.1f}%", ha="center", va="center", color=text_color, fontweight='bold')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(plot_filepath, dpi=300)
    plt.close()
    print(f"✓ Visual segment dashboard saved to: {plot_filepath}")

    # ------------------------------------------------------------------
    # Task 6: Automated Verification Assertions
    # ------------------------------------------------------------------
    print("\n------------------------------------------------------------------")
    print("Task 6: Running Automated Assertions")
    print("------------------------------------------------------------------")
    assert total_customers == 2000, f"Expected 2,000 customers, got {total_customers}"
    assert len(ranked_segments) == 3, f"Expected 3 customer types, got {len(ranked_segments)}"

    # Churn rates
    ent_churn = ranked_segments.loc['Enterprise', 'churn_rate']
    smb_churn = ranked_segments.loc['SMB', 'churn_rate']
    stu_churn = ranked_segments.loc['Startup', 'churn_rate']

    assert abs(ent_churn - 0.01) < 0.005, f"Enterprise churn expected ~1%, got {ent_churn}"
    assert abs(smb_churn - 0.12) < 0.005, f"SMB churn expected ~12%, got {smb_churn}"
    assert abs(stu_churn - 0.08) < 0.005, f"Startup churn expected ~8%, got {stu_churn}"

    # Revenue share
    ent_rev_share = ranked_segments.loc['Enterprise', 'revenue_share_pct']
    assert abs(ent_rev_share - 70.0) < 1.0, f"Enterprise revenue share expected ~70%, got {ent_rev_share}%"

    # Transform broadcast shape validation
    assert df['churn_rate_by_type'].shape == (total_customers,), "Transform shape mismatch"
    assert (df['churn_rate_by_type'] >= 0.0).all() and (df['churn_rate_by_type'] <= 1.0).all()

    # Unstack & Pivot table identity
    assert np.allclose(unstacked_matrix.values, revenue_pivot.values), "Pivot table does not match unstack"

    # Chart output validation
    assert os.path.exists(plot_filepath), f"Chart missing at {plot_filepath}"
    assert os.path.getsize(plot_filepath) > 10000, "Chart file corrupt or incomplete"

    print("✓ All GroupBy Aggregation & Segment Insights Assertions Passed Successfully!")
    print("==================================================================\n")


if __name__ == '__main__':
    run_segment_aggregation()
