"""
Module 2.33: Funnel Analysis & Drop-Off Detection - Runner & Validator
Defines sequential funnel stages, computes drop-off and conversion rates,
identifies bottlenecks/leaks, quantifies business revenue impact, and generates visual dashboards.
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
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


def load_funnel_data() -> pd.DataFrame:
    """Load user onboarding funnel dataset from DuckDB or CSV."""
    try:
        df = pd.read_sql("SELECT * FROM user_funnel ORDER BY user_id", engine)
    except Exception:
        csv_path = os.path.join(os.path.dirname(__file__), 'data', 'funnel_events.csv')
        df = pd.read_csv(csv_path)
    return df


def calculate_funnel_metrics(stages_dict: dict) -> pd.DataFrame:
    """Compute step-by-step drop-off and progression metrics between consecutive stages."""
    stage_names = list(stages_dict.keys())
    stage_counts = list(stages_dict.values())
    top_stage_count = stage_counts[0]

    records = []
    for i in range(len(stage_counts) - 1):
        users_start = stage_counts[i]
        users_next = stage_counts[i + 1]
        lost = users_start - users_next
        drop_rate = (lost / users_start) * 100.0 if users_start > 0 else 0.0
        completion_rate = (users_next / users_start) * 100.0 if users_start > 0 else 0.0
        cumulative_conv = (users_next / top_stage_count) * 100.0 if top_stage_count > 0 else 0.0

        records.append({
            'step_index': i + 1,
            'from_stage': stage_names[i],
            'to_stage': stage_names[i + 1],
            'users_entered': users_start,
            'users_continued': users_next,
            'lost_users': lost,
            'drop_rate_pct': drop_rate,
            'completion_rate_pct': completion_rate,
            'cumulative_conversion_pct': cumulative_conv
        })

    return pd.DataFrame(records)


def run_funnel_analysis():
    print("==================================================================")
    print(">>> MODULE 2.33: FUNNEL ANALYSIS & DROP-OFF DETECTION <<<")
    print("==================================================================")

    df = load_funnel_data()
    total_users = len(df)

    # ------------------------------------------------------------------
    # Task 1: Define Sequential Funnel Stages
    # ------------------------------------------------------------------
    print("\n------------------------------------------------------------------")
    print("Task 1: Defining Sequential Funnel Stages")
    print("------------------------------------------------------------------")
    # Granular 6-stage user onboarding journey
    granular_stages = {
        'Sign Up Clicked': int(df['signup_clicked'].sum()),
        'Email Entered': int(df['email_entered'].sum()),
        'Password Created': int(df['password_created'].sum()),
        'Email Verified': int(df['email_verified'].sum()),
        'Payment Added': int(df['payment_added'].sum()),
        'First Purchase': int(df['first_purchase'].sum())
    }

    # 4-stage executive summary funnel (from assignment prompt)
    exec_stages = {
        'Sign Up': granular_stages['Sign Up Clicked'],
        'Email Verified': granular_stages['Email Verified'],
        'Payment Added': granular_stages['Payment Added'],
        'First Purchase': granular_stages['First Purchase']
    }

    print("Sequential Onboarding Funnel Counts (Granular):")
    for stage, count in granular_stages.items():
        pct_of_total = (count / total_users) * 100.0
        print(f"  • {stage:<25}: {count:,} users ({pct_of_total:.1f}% of top-of-funnel)")

    overall_conversion = (granular_stages['First Purchase'] / granular_stages['Sign Up Clicked']) * 100.0
    print(f"\nOverall Top-to-Bottom Conversion Rate: {overall_conversion:.1f}%")
    print("[Business Context]: The company knows 'conversion is 20%'.")
    print("However, without computing granular step-by-step drop-off, the primary leak remains invisible.")

    # ------------------------------------------------------------------
    # Task 2: Step-by-Step Drop-Off & Progression Measurement
    # ------------------------------------------------------------------
    print("\n------------------------------------------------------------------")
    print("Task 2: Measuring Consecutive Drop-Off & Completion Rates")
    print("------------------------------------------------------------------")
    funnel_metrics_df = calculate_funnel_metrics(granular_stages)
    display_df = funnel_metrics_df[[
        'from_stage', 'to_stage', 'users_entered', 'lost_users',
        'drop_rate_pct', 'completion_rate_pct', 'cumulative_conversion_pct'
    ]].copy()
    display_df['users_entered'] = display_df['users_entered'].map(lambda v: f"{v:,}")
    display_df['lost_users'] = display_df['lost_users'].map(lambda v: f"{v:,}")
    display_df['drop_rate_pct'] = display_df['drop_rate_pct'].map(lambda v: f"{v:.1f}%")
    display_df['completion_rate_pct'] = display_df['completion_rate_pct'].map(lambda v: f"{v:.1f}%")
    display_df['cumulative_conversion_pct'] = display_df['cumulative_conversion_pct'].map(lambda v: f"{v:.1f}%")

    print(display_df.to_string(index=False))

    # ------------------------------------------------------------------
    # Task 3: Identify the Biggest Leak Programmatically
    # ------------------------------------------------------------------
    print("\n------------------------------------------------------------------")
    print("Task 3: Identifying the Primary Funnel Leak (Bottleneck)")
    print("------------------------------------------------------------------")
    worst_step_idx = funnel_metrics_df['drop_rate_pct'].idxmax()
    biggest_leak = funnel_metrics_df.iloc[worst_step_idx]

    print(f"🚨 BIGGEST FUNNEL LEAK DETECTED:")
    print(f"   Stage Transition: '{biggest_leak['from_stage']}' ➔ '{biggest_leak['to_stage']}'")
    print(f"   Drop-Off Rate:    {biggest_leak['drop_rate_pct']:.1f}% loss")
    print(f"   Users Abandoned:  {biggest_leak['lost_users']:,} users dropped")

    print("\n[Engineering & Product Root Cause Diagnosis]:")
    print("  • Users have already invested high effort adding payment details (4,000 users).")
    print(f"  • Yet HALF of them ({biggest_leak['lost_users']:,} users) abandon before confirming the transaction.")
    print("  • Common friction points: hidden surcharges/fees shown at final checkout, slow 3DS gateway authentication,")
    print("    ambiguous CTA buttons, or confusing pricing plan confirmations.")

    # ------------------------------------------------------------------
    # Task 4: Quantifying Business & Financial Impact of Optimization
    # ------------------------------------------------------------------
    print("\n------------------------------------------------------------------")
    print("Task 4: Business Impact & Revenue Growth Modeling")
    print("------------------------------------------------------------------")
    # Average Order Value (AOV) from actual purchasers
    actual_purchasers = df[df['first_purchase'] == 1]
    avg_order_value = actual_purchasers['purchase_amount'].mean() if len(actual_purchasers) > 0 else 150.0
    current_revenue = actual_purchasers['purchase_amount'].sum() if len(actual_purchasers) > 0 else 300000.0

    print(f"Current First Purchases:    {granular_stages['First Purchase']:,}")
    print(f"Average Order Value (AOV):  ${avg_order_value:,.2f}")
    print(f"Current First-Purchase ARR: ${current_revenue:,.2f}")

    # Optimization Scenarios for the biggest leak ('Payment Added' -> 'First Purchase'):
    # Base: 4,000 users with payment added, 2,000 drop off (50% drop rate)
    scenarios = [
        {'name': 'Status Quo (50% Drop)', 'drop_rate': 0.50},
        {'name': 'Moderate Fix (30% Drop)', 'drop_rate': 0.30},
        {'name': 'Strong Fix (20% Drop)', 'drop_rate': 0.20},
        {'name': 'Full Friction Fix (10% Drop)', 'drop_rate': 0.10},
        {'name': 'Zero Friction (0% Drop)', 'drop_rate': 0.00},
    ]

    impact_rows = []
    base_purchasers = granular_stages['Payment Added']
    for sc in scenarios:
        drop_r = sc['drop_rate']
        purchasers = int(base_purchasers * (1.0 - drop_r))
        gain_users = purchasers - granular_stages['First Purchase']
        sim_rev = purchasers * avg_order_value
        gain_rev = sim_rev - current_revenue
        pct_growth = (gain_rev / current_revenue) * 100.0

        impact_rows.append({
            'Scenario': sc['name'],
            'Converted Users': purchasers,
            'Incremental Users': gain_users,
            'Projected Revenue': sim_rev,
            'Incremental Revenue': gain_rev,
            'Revenue Growth': f"+{pct_growth:.1f}%" if pct_growth > 0 else "Baseline"
        })

    impact_df = pd.DataFrame(impact_rows)
    print("\nRevenue Impact Simulation across Bottleneck Optimization Scenarios:")
    print(impact_df.to_string(index=False))

    # ------------------------------------------------------------------
    # Task 5: Visualizing Funnel Dashboard (public/funnel_analysis.png)
    # ------------------------------------------------------------------
    print("\n------------------------------------------------------------------")
    print("Task 5: Generating Professional Funnel Visualization Dashboard...")
    print("------------------------------------------------------------------")
    plots_dir = os.path.join(os.path.dirname(__file__), 'public')
    os.makedirs(plots_dir, exist_ok=True)
    plot_filepath = os.path.join(plots_dir, 'funnel_analysis.png')

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Module 2.33: Funnel Analysis & Drop-Off Detection Dashboard', fontsize=17, fontweight='bold', y=0.98)

    # 1. Funnel Bar Chart with User Counts & Step Retention
    stage_labels = list(granular_stages.keys())
    stage_vals = list(granular_stages.values())
    bar_palette = ['#3b82f6', '#0284c7', '#06b6d4', '#10b981', '#f59e0b', '#ef4444']

    bars = axes[0, 0].bar(stage_labels, stage_vals, color=bar_palette, edgecolor='black', alpha=0.88)
    axes[0, 0].set_title('1. Sequential Onboarding Funnel (User Volume)', fontsize=12, fontweight='bold')
    axes[0, 0].set_ylabel('Active Users')
    axes[0, 0].set_ylim(0, max(stage_vals) * 1.15)
    axes[0, 0].set_xticks(range(len(stage_labels)))
    axes[0, 0].set_xticklabels(stage_labels, rotation=20, ha='right', fontsize=9.5)
    axes[0, 0].grid(True, linestyle=':', alpha=0.5)

    for bar, count in zip(bars, stage_vals):
        pct = (count / total_users) * 100.0
        axes[0, 0].text(
            bar.get_x() + bar.get_width() / 2.,
            count + 150,
            f"{count:,}\n({pct:.0f}%)",
            ha='center', va='bottom', fontsize=9, fontweight='bold'
        )

    # 2. Step-by-Step Drop-Off Rate (%) with Critical Leak Highlight
    step_transitions = [f"{r['from_stage']}\n➔ {r['to_stage']}" for _, r in funnel_metrics_df.iterrows()]
    drop_percentages = list(funnel_metrics_df['drop_rate_pct'])
    drop_colors = ['#ef4444' if p >= 40 else ('#f59e0b' if p >= 22 else '#3b82f6') for p in drop_percentages]

    drop_bars = axes[0, 1].bar(step_transitions, drop_percentages, color=drop_colors, edgecolor='black', alpha=0.88)
    axes[0, 1].axhline(25.0, color='#64748b', linestyle='--', linewidth=1.5, label='High Friction Threshold (25%)')
    axes[0, 1].set_title('2. Drop-Off Rate by Consecutive Stage (% Lost)', fontsize=12, fontweight='bold')
    axes[0, 1].set_ylabel('Drop-Off Rate (%)')
    axes[0, 1].set_ylim(0, max(drop_percentages) * 1.25)
    axes[0, 1].set_xticks(range(len(step_transitions)))
    axes[0, 1].set_xticklabels(step_transitions, rotation=15, ha='right', fontsize=8.5)
    axes[0, 1].legend(loc='upper left')
    axes[0, 1].grid(True, linestyle=':', alpha=0.5)

    for b, p, lost in zip(drop_bars, drop_percentages, funnel_metrics_df['lost_users']):
        axes[0, 1].text(
            b.get_x() + b.get_width() / 2.,
            p + 1.2,
            f"{p:.1f}%\n(-{lost:,})",
            ha='center', va='bottom', fontsize=9, fontweight='bold',
            color='#991b1b' if p >= 40 else 'black'
        )

    # 3. Cumulative Conversion Funnel Curve
    cum_conv_vals = [100.0] + list(funnel_metrics_df['cumulative_conversion_pct'])
    axes[1, 0].plot(range(len(stage_labels)), cum_conv_vals, marker='o', markersize=8, color='#6366f1', linewidth=2.8)
    axes[1, 0].fill_between(range(len(stage_labels)), cum_conv_vals, color='#6366f1', alpha=0.15)
    axes[1, 0].set_title('3. Cumulative Conversion Retention Curve', fontsize=12, fontweight='bold')
    axes[1, 0].set_ylabel('Conversion (%) of Top-of-Funnel')
    axes[1, 0].set_ylim(0, 110)
    axes[1, 0].set_xticks(range(len(stage_labels)))
    axes[1, 0].set_xticklabels(stage_labels, rotation=20, ha='right', fontsize=9.5)
    axes[1, 0].grid(True, linestyle=':', alpha=0.5)

    for i, (lbl, val) in enumerate(zip(stage_labels, cum_conv_vals)):
        axes[1, 0].text(i, val + 3.0, f"{val:.1f}%", ha='center', va='bottom', fontweight='bold', fontsize=9)

    # 4. Revenue Growth Modeling (Optimization Scenarios)
    scen_names = [s['Scenario'].replace(' (', '\n(') for s in impact_rows]
    scen_revs = [s['Projected Revenue'] / 1000.0 for s in impact_rows]
    scen_colors = ['#94a3b8', '#38bdf8', '#34d399', '#10b981', '#059669']

    rev_bars = axes[1, 1].bar(range(len(scen_names)), scen_revs, color=scen_colors, edgecolor='black', alpha=0.9)
    axes[1, 1].set_title('4. Financial Impact of Fixing Primary Bottleneck ($k ARR)', fontsize=12, fontweight='bold')
    axes[1, 1].set_ylabel('Projected First Purchase Revenue ($k)')
    axes[1, 1].set_ylim(0, max(scen_revs) * 1.2)
    axes[1, 1].set_xticks(range(len(scen_names)))
    axes[1, 1].set_xticklabels(scen_names, fontsize=8.5)
    axes[1, 1].grid(True, linestyle=':', alpha=0.5)

    for bar, val, row in zip(rev_bars, scen_revs, impact_rows):
        axes[1, 1].text(
            bar.get_x() + bar.get_width() / 2.,
            val + 12,
            f"${val:,.0f}k\n({row['Revenue Growth']})",
            ha='center', va='bottom', fontsize=8.5, fontweight='bold'
        )

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(plot_filepath, dpi=300)
    plt.close()
    print(f"✓ Visual funnel dashboard saved to: {plot_filepath}")

    # ------------------------------------------------------------------
    # Task 6: Automated Verification Assertions
    # ------------------------------------------------------------------
    print("\n------------------------------------------------------------------")
    print("Task 6: Running Automated Verification Assertions")
    print("------------------------------------------------------------------")
    # 1. Total volume validation
    assert total_users == 10000, f"Expected 10,000 users, got {total_users}"
    assert granular_stages['Sign Up Clicked'] == 10000
    assert granular_stages['Email Entered'] == 8000
    assert granular_stages['Password Created'] == 6000
    assert granular_stages['Email Verified'] == 5000
    assert granular_stages['Payment Added'] == 4000
    assert granular_stages['First Purchase'] == 2000

    # 2. Step drop-off rates validation
    step_drop_rates = list(funnel_metrics_df['drop_rate_pct'])
    assert abs(step_drop_rates[0] - 20.0) < 0.1, f"Step 1 drop expected 20%, got {step_drop_rates[0]}"
    assert abs(step_drop_rates[1] - 25.0) < 0.1, f"Step 2 drop expected 25%, got {step_drop_rates[1]}"
    assert abs(step_drop_rates[2] - 16.67) < 0.2, f"Step 3 drop expected ~16.7%, got {step_drop_rates[2]}"
    assert abs(step_drop_rates[3] - 20.0) < 0.1, f"Step 4 drop expected 20%, got {step_drop_rates[3]}"
    assert abs(step_drop_rates[4] - 50.0) < 0.1, f"Step 5 drop expected 50%, got {step_drop_rates[4]}"

    # 3. Overall conversion & biggest leak verification
    assert abs(overall_conversion - 20.0) < 0.1, f"Overall conversion expected 20%, got {overall_conversion}"
    assert biggest_leak['from_stage'] == 'Payment Added' and biggest_leak['to_stage'] == 'First Purchase'
    assert biggest_leak['drop_rate_pct'] == 50.0

    # 4. Dashboard chart file existence
    assert os.path.exists(plot_filepath), f"Chart file missing at {plot_filepath}"
    assert os.path.getsize(plot_filepath) > 10000, "Chart file corrupt or too small"

    print("✓ All Funnel Analysis & Drop-Off Detection Assertions Passed Successfully!")
    print("==================================================================\n")


if __name__ == '__main__':
    run_funnel_analysis()
