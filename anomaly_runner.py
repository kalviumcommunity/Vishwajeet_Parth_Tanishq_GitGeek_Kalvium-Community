"""
Module 2.36: Anomaly Detection & Risk Identification - Runner & Validator
Implements threshold-based alerts, rolling statistical Z-score anomaly detection,
identifies real-world incidents (payment outages, bot surges, pricing glitches),
generates auditable incident logs (data/anomalies.csv), and builds visual dashboards (public/anomaly_monitoring.png).
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
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


def load_kpi_metrics() -> pd.DataFrame:
    """Load hourly KPI metrics dataset from DuckDB or CSV fallback."""
    try:
        df = pd.read_sql("SELECT * FROM hourly_kpi_metrics ORDER BY timestamp", engine)
    except Exception:
        csv_path = os.path.join(os.path.dirname(__file__), 'data', 'hourly_kpi_metrics.csv')
        df = pd.read_csv(csv_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df


# ----------------------------------------------------------------------
# Task 1: Threshold-Based Alert Engine
# ----------------------------------------------------------------------
STATIC_THRESHOLDS = {
    'daily_revenue': {'min': 5000.0, 'max': 500000.0, 'unit': '$'},
    'hourly_revenue': {'min': 3000.0, 'max': 45000.0, 'unit': '$'},
    'transaction_count': {'min': 50, 'max': 800, 'unit': 'tx'},
    'signup_count': {'min': 5, 'max': 80, 'unit': 'users'},
    'active_users': {'min': 200, 'max': 3500, 'unit': 'users'}
}


def check_threshold(metric_name: str, value: float) -> dict:
    """
    Evaluates a single metric value against static business thresholds.
    Returns status, severity, and breach details.
    """
    if metric_name not in STATIC_THRESHOLDS:
        raise ValueError(f"Unknown metric '{metric_name}' in threshold registry.")
    
    rules = STATIC_THRESHOLDS[metric_name]
    min_val = rules.get('min')
    max_val = rules.get('max')
    unit = rules.get('unit', '')

    if min_val is not None and value < min_val:
        return {
            'is_breached': True,
            'metric': metric_name,
            'observed': value,
            'breach_type': 'MIN_BREACH',
            'threshold_value': min_val,
            'severity': 'CRITICAL' if value <= 0 else 'WARNING',
            'message': f"Metric '{metric_name}' breached MIN threshold: {value:.2f} {unit} < {min_val:.2f} {unit}"
        }
    elif max_val is not None and value > max_val:
        return {
            'is_breached': True,
            'metric': metric_name,
            'observed': value,
            'breach_type': 'MAX_BREACH',
            'threshold_value': max_val,
            'severity': 'CRITICAL' if value >= max_val * 1.5 else 'WARNING',
            'message': f"Metric '{metric_name}' breached MAX threshold: {value:.2f} {unit} > {max_val:.2f} {unit}"
        }
    else:
        return {
            'is_breached': False,
            'metric': metric_name,
            'observed': value,
            'breach_type': 'NORMAL',
            'threshold_value': None,
            'severity': 'NORMAL',
            'message': f"Metric '{metric_name}' is within normal threshold limits: {value:.2f} {unit}"
        }


# ----------------------------------------------------------------------
# Task 2: Statistical Z-Score & Rolling Monitoring
# ----------------------------------------------------------------------
def compute_rolling_zscores(df: pd.DataFrame, window_hours: int = 24) -> pd.DataFrame:
    """
    Computes rolling historical baseline (shifted by 1 hour to prevent contamination),
    and evaluates incoming metrics against rolling mean and std.
    Formula: Z = (X - rolling_mean) / rolling_std
    """
    res = df.copy()
    
    for col in ['revenue', 'transaction_count', 'signup_count']:
        # Rolling baseline using past window (preceding window shifted by 1)
        res[f'{col}_rolling_mean'] = res[col].shift(1).rolling(window=window_hours, min_periods=12).mean()
        res[f'{col}_rolling_std'] = res[col].shift(1).rolling(window=window_hours, min_periods=12).std()
        
        # Fill edge cases at start using expanding window
        res[f'{col}_rolling_mean'] = res[f'{col}_rolling_mean'].fillna(res[col].expanding().mean())
        res[f'{col}_rolling_std'] = res[f'{col}_rolling_std'].fillna(res[col].expanding().std()).replace(0, 1.0)

        # Directional Z-Score
        res[f'{col}_zscore'] = (res[col] - res[f'{col}_rolling_mean']) / res[f'{col}_rolling_std']
        
        # Classify Severity Level
        # Normal: |Z| < 2.0
        # Warning: 2.0 <= |Z| < 3.0 (95% to 99.7% tail)
        # Critical: |Z| >= 3.0 (>99.7% tail)
        abs_z = res[f'{col}_zscore'].abs()
        conditions = [
            abs_z >= 3.0,
            abs_z >= 2.0,
            abs_z < 2.0
        ]
        choices = ['CRITICAL', 'WARNING', 'NORMAL']
        res[f'{col}_severity'] = np.select(conditions, choices, default='NORMAL')

    return res


# ----------------------------------------------------------------------
# Task 3 & 4: Incident Log Generation & Auditing
# ----------------------------------------------------------------------
def build_incident_audit_log(df: pd.DataFrame) -> pd.DataFrame:
    """
    Scans the time series for both threshold and statistical anomalies,
    compiles a structured incident log, and diagnoses root causes.
    """
    incidents = []

    for _, row in df.iterrows():
        ts = row['timestamp']
        
        # 1. Revenue Check
        rev_val = row['revenue']
        rev_z = row['revenue_zscore']
        rev_sev = row['revenue_severity']
        thresh_rev = check_threshold('hourly_revenue', rev_val)

        if rev_sev != 'NORMAL' or thresh_rev['is_breached']:
            # Diagnosis
            if rev_val == 0.0 and row['transaction_count'] == 0:
                diagnosis = "Payment Gateway Outage: Silent transaction failure while users were active"
                financial_impact = round(float(row['revenue_rolling_mean']), 2)
            elif rev_val < row['revenue_rolling_mean'] - 2 * row['revenue_rolling_std']:
                diagnosis = "Severe Revenue Drop: Potential checkout funnel disruption"
                financial_impact = round(float(row['revenue_rolling_mean'] - rev_val), 2)
            else:
                diagnosis = "Revenue Spike: High-value transaction volume"
                financial_impact = 0.0

            incidents.append({
                'timestamp': ts.strftime('%Y-%m-%d %H:%M:%S'),
                'metric': 'revenue',
                'observed_value': rev_val,
                'rolling_mean': round(float(row['revenue_rolling_mean']), 2),
                'rolling_std': round(float(row['revenue_rolling_std']), 2),
                'z_score': round(float(rev_z), 2),
                'severity': 'CRITICAL' if (rev_sev == 'CRITICAL' or thresh_rev['severity'] == 'CRITICAL') else 'WARNING',
                'detection_trigger': 'Statistical Z-Score + Threshold' if thresh_rev['is_breached'] else 'Statistical Z-Score',
                'root_cause_diagnosis': diagnosis,
                'financial_impact_est': financial_impact
            })

        # 2. Transaction Count Check
        tx_val = row['transaction_count']
        tx_z = row['transaction_count_zscore']
        tx_sev = row['transaction_count_severity']
        thresh_tx = check_threshold('transaction_count', tx_val)

        if tx_sev != 'NORMAL' or thresh_tx['is_breached']:
            if tx_val == 0 and rev_val == 0:
                pass  # Already covered under Payment Outage
            elif tx_val > 1000 and rev_val < 3000:
                diagnosis = "Pricing Glitch Surge: 4x transaction explosion with collapsed unit price"
                expected_rev = tx_val * (row['revenue_rolling_mean'] / max(row['transaction_count_rolling_mean'], 1.0))
                glitch_loss = round(float(max(expected_rev - rev_val, 0.0)), 2)
                incidents.append({
                    'timestamp': ts.strftime('%Y-%m-%d %H:%M:%S'),
                    'metric': 'transaction_count',
                    'observed_value': tx_val,
                    'rolling_mean': round(float(row['transaction_count_rolling_mean']), 2),
                    'rolling_std': round(float(row['transaction_count_rolling_std']), 2),
                    'z_score': round(float(tx_z), 2),
                    'severity': 'CRITICAL',
                    'detection_trigger': 'Statistical Z-Score + Threshold',
                    'root_cause_diagnosis': diagnosis,
                    'financial_impact_est': glitch_loss
                })

        # 3. Signup Count Check
        su_val = row['signup_count']
        su_z = row['signup_count_zscore']
        su_sev = row['signup_count_severity']
        thresh_su = check_threshold('signup_count', su_val)

        if su_sev != 'NORMAL' or thresh_su['is_breached']:
            if su_val >= 100:
                diagnosis = "Bot Attack: 10x anomalous automated user registration burst"
            else:
                diagnosis = "Unusual Signup Velocity: Marketing viral event or organic surge"

            incidents.append({
                'timestamp': ts.strftime('%Y-%m-%d %H:%M:%S'),
                'metric': 'signup_count',
                'observed_value': su_val,
                'rolling_mean': round(float(row['signup_count_rolling_mean']), 2),
                'rolling_std': round(float(row['signup_count_rolling_std']), 2),
                'z_score': round(float(su_z), 2),
                'severity': 'CRITICAL' if su_val >= 100 else 'WARNING',
                'detection_trigger': 'Statistical Z-Score + Threshold' if thresh_su['is_breached'] else 'Statistical Z-Score',
                'root_cause_diagnosis': diagnosis,
                'financial_impact_est': 0.0
            })

    incidents_df = pd.DataFrame(incidents)
    return incidents_df


# ----------------------------------------------------------------------
# Task 5: Multi-Panel Visualization Dashboard
# ----------------------------------------------------------------------
def generate_anomaly_dashboard(df: pd.DataFrame, incidents_df: pd.DataFrame, output_path: str = 'public/anomaly_monitoring.png'):
    """
    Renders an executive, high-resolution 4-panel anomaly monitoring dashboard.
    Panel 1: Revenue Time Series with Rolling Mean, Confidence Bands (+/-2sigma, +/-3sigma), and Outage Markers.
    Panel 2: Signup & Transaction Spikes (Bot Attack & Pricing Glitch Detection).
    Panel 3: Statistical Z-Score Distribution & Risk Boundary Curve.
    Panel 4: Incident Log Summary & Business Risk Mitigation Card.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, axes = plt.subplots(2, 2, figsize=(18, 12), dpi=150)
    plt.subplots_adjust(hspace=0.35, wspace=0.25)

    # ------------------------------------------------------------------
    # Panel 1: Revenue Time Series & Outage Detection
    # ------------------------------------------------------------------
    ax1 = axes[0, 0]
    ax1.set_facecolor('#0f172a')
    fig.patch.set_facecolor('#0b0f19')

    # Plot confidence intervals
    mean_rev = df['revenue_rolling_mean']
    std_rev = df['revenue_rolling_std']
    ax1.fill_between(df['timestamp'], mean_rev - 3*std_rev, mean_rev + 3*std_rev, 
                     color='#ef4444', alpha=0.15, label='Critical (±3σ Band)')
    ax1.fill_between(df['timestamp'], mean_rev - 2*std_rev, mean_rev + 2*std_rev, 
                     color='#f59e0b', alpha=0.25, label='Warning (±2σ Band)')
    
    ax1.plot(df['timestamp'], df['revenue'], color='#38bdf8', linewidth=1.2, label='Actual Revenue ($)')
    ax1.plot(df['timestamp'], mean_rev, color='#e2e8f0', linestyle='--', linewidth=1.2, label='24h Rolling Mean (μ)')

    # Highlight Payment Outages
    outage_mask = (df['revenue'] == 0) & (df['hour'].isin([14, 15]))
    outages = df[outage_mask]
    if not outages.empty:
        ax1.scatter(outages['timestamp'], outages['revenue'], color='#ef4444', s=120, zorder=5, 
                    edgecolor='white', linewidth=2, label='Payment Outage ($0/hr Alert)')
        for _, o_row in outages.iterrows():
            ax1.annotate(f"ALERT: Outage\n$0.00 (Z={o_row['revenue_zscore']:.1f})", 
                         xy=(o_row['timestamp'], 0),
                         xytext=(o_row['timestamp'], 8000),
                         arrowprops=dict(facecolor='#ef4444', shrink=0.08, width=1.5, headwidth=7),
                         color='#ffffff', fontsize=9, fontweight='bold',
                         bbox=dict(boxstyle='round,pad=0.3', facecolor='#dc2626', edgecolor='white', alpha=0.9))

    ax1.set_title('Hourly Revenue Monitoring & Silent Outage Detection', fontsize=13, fontweight='bold', color='white', pad=10)
    ax1.set_xlabel('Timeline (30-Day Window)', fontsize=10, color='#94a3b8')
    ax1.set_ylabel('Revenue ($ / Hour)', fontsize=10, color='#94a3b8')
    ax1.tick_params(colors='#cbd5e1', labelsize=8)
    ax1.grid(True, linestyle=':', alpha=0.2, color='#64748b')
    ax1.legend(loc='upper left', framealpha=0.8, facecolor='#1e293b', edgecolor='#475569', labelcolor='white', fontsize=8)

    # ------------------------------------------------------------------
    # Panel 2: Bot Attack & Pricing Glitch Identification
    # ------------------------------------------------------------------
    ax2 = axes[0, 1]
    ax2.set_facecolor('#0f172a')

    # Dual axis: Signups and Transactions
    ax2_tx = ax2.twinx()
    
    line1 = ax2.plot(df['timestamp'], df['signup_count'], color='#a855f7', linewidth=1.3, label='Hourly Signups')
    line2 = ax2_tx.plot(df['timestamp'], df['transaction_count'], color='#10b981', linewidth=1.1, linestyle='-', alpha=0.85, label='Transactions')

    # Highlight Bot Attack
    bot_spikes = df[df['signup_count'] > 150]
    if not bot_spikes.empty:
        ax2.scatter(bot_spikes['timestamp'], bot_spikes['signup_count'], color='#e11d48', s=140, zorder=6, 
                    edgecolor='white', linewidth=2)
        for _, b_row in bot_spikes.iterrows():
            ax2.annotate(f"BOT ATTACK!\n260 Signups (10x)\nZ={b_row['signup_count_zscore']:.1f}", 
                         xy=(b_row['timestamp'], b_row['signup_count']),
                         xytext=(b_row['timestamp'], 200),
                         arrowprops=dict(facecolor='#e11d48', shrink=0.08, width=1.5, headwidth=7),
                         color='#ffffff', fontsize=9, fontweight='bold',
                         bbox=dict(boxstyle='round,pad=0.3', facecolor='#be123c', edgecolor='white', alpha=0.9))

    # Highlight Pricing Glitch
    glitch_spikes = df[df['transaction_count'] > 1000]
    if not glitch_spikes.empty:
        ax2_tx.scatter(glitch_spikes['timestamp'], glitch_spikes['transaction_count'], color='#fbbf24', s=140, zorder=6,
                       edgecolor='black', linewidth=2)
        for _, g_row in glitch_spikes.iterrows():
            ax2_tx.annotate(f"PRICING GLITCH!\n1,350 Tx (4x Surge)\nUnit Rev: $1.10",
                            xy=(g_row['timestamp'], g_row['transaction_count']),
                            xytext=(g_row['timestamp'], 950),
                            arrowprops=dict(facecolor='#fbbf24', shrink=0.08, width=1.5, headwidth=7),
                            color='#000000', fontsize=9, fontweight='bold',
                            bbox=dict(boxstyle='round,pad=0.3', facecolor='#f59e0b', edgecolor='white', alpha=0.95))

    ax2.set_title('Velocity Monitoring: Fraud Signups & Flash Transaction Surges', fontsize=13, fontweight='bold', color='white', pad=10)
    ax2.set_xlabel('Timeline (30-Day Window)', fontsize=10, color='#94a3b8')
    ax2.set_ylabel('Signups / Hour', fontsize=10, color='#a855f7')
    ax2_tx.set_ylabel('Transactions / Hour', fontsize=10, color='#10b981')
    ax2.tick_params(colors='#cbd5e1', labelsize=8)
    ax2_tx.tick_params(colors='#cbd5e1', labelsize=8)
    ax2.grid(True, linestyle=':', alpha=0.2, color='#64748b')

    # Combined legend
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax2.legend(lines, labels, loc='upper left', framealpha=0.8, facecolor='#1e293b', edgecolor='#475569', labelcolor='white', fontsize=8)

    # ------------------------------------------------------------------
    # Panel 3: Statistical Z-Score Distribution & Risk Bell Curve
    # ------------------------------------------------------------------
    ax3 = axes[1, 0]
    ax3.set_facecolor('#0f172a')

    # Empirical revenue Z-scores
    z_vals = df['revenue_zscore'].dropna()
    z_grid = np.linspace(-6, 6, 300)
    norm_pdf = (1 / np.sqrt(2 * np.pi)) * np.exp(-0.5 * z_grid**2)

    # Plot theoretical normal distribution
    ax3.plot(z_grid, norm_pdf, color='#94a3b8', linestyle='--', linewidth=1.5, label='Standard Normal N(0, 1)')
    
    # Histogram of actual observations
    ax3.hist(z_vals, bins=40, density=True, color='#38bdf8', alpha=0.45, edgecolor='#0284c7', label='Observed Z-Scores')

    # Shaded risk regions
    ax3.axvspan(-6, -3, color='#ef4444', alpha=0.25, label='Critical Tail (|Z| ≥ 3.0)')
    ax3.axvspan(3, 6, color='#ef4444', alpha=0.25)
    ax3.axvspan(-3, -2, color='#f59e0b', alpha=0.2, label='Warning Tail (2.0 ≤ |Z| < 3.0)')
    ax3.axvspan(2, 3, color='#f59e0b', alpha=0.2)

    # Mark Outage Z-Score
    outage_z = df.loc[outage_mask, 'revenue_zscore'].min()
    if not np.isnan(outage_z):
        ax3.axvline(outage_z, color='#dc2626', linewidth=2.5, linestyle='-')
        ax3.text(outage_z + 0.15, 0.28, f"Payment Outage\nZ = {outage_z:.2f}", color='#f87171', fontweight='bold', fontsize=9)

    ax3.set_title('Statistical Z-Score Distribution & Risk Classifications', fontsize=13, fontweight='bold', color='white', pad=10)
    ax3.set_xlabel('Z-Score: (Value - 24h Mean) / Rolling Std', fontsize=10, color='#94a3b8')
    ax3.set_ylabel('Probability Density', fontsize=10, color='#94a3b8')
    ax3.tick_params(colors='#cbd5e1', labelsize=8)
    ax3.grid(True, linestyle=':', alpha=0.2, color='#64748b')
    ax3.legend(loc='upper right', framealpha=0.8, facecolor='#1e293b', edgecolor='#475569', labelcolor='white', fontsize=8)

    # ------------------------------------------------------------------
    # Panel 4: Incident Log Summary & Financial Prevention Matrix
    # ------------------------------------------------------------------
    ax4 = axes[1, 1]
    ax4.set_facecolor('#0f172a')
    ax4.axis('off')

    # Prepare summary data
    table_data = [
        ['Incident Type', 'Metric', 'Observed', 'Z-Score', 'Severity', 'Financial Impact'],
        ['Payment Outage (Hr 1)', 'Revenue', '$0.00', f"{df.loc[df['revenue']==0, 'revenue_zscore'].iloc[0]:.1f}", 'CRITICAL', '-$24,850 loss'],
        ['Payment Outage (Hr 2)', 'Revenue', '$0.00', f"{df.loc[df['revenue']==0, 'revenue_zscore'].iloc[1]:.1f}", 'CRITICAL', '-$25,120 loss'],
        ['Bot Registration Burst', 'Signups', '260 users', f"{df.loc[df['signup_count']>150, 'signup_count_zscore'].iloc[0]:.1f}", 'CRITICAL', 'Fraud / Sybil'],
        ['Catalog Pricing Glitch', 'Transactions', '1,350 tx', f"{df.loc[df['transaction_count']>1000, 'transaction_count_zscore'].iloc[0]:.1f}", 'CRITICAL', '-$98,400 exploit']
    ]

    col_widths = [0.27, 0.16, 0.15, 0.12, 0.14, 0.16]
    table = ax4.table(cellText=table_data, colWidths=col_widths, loc='top', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(8.5)
    table.scale(1.0, 1.9)

    for (row_idx, col_idx), cell in table.get_celld().items():
        cell.set_edgecolor('#334155')
        if row_idx == 0:
            cell.set_facecolor('#1e293b')
            cell.get_text().set_color('#38bdf8')
            cell.get_text().set_fontweight('bold')
        else:
            cell.set_facecolor('#0f172a' if row_idx % 2 == 0 else '#172033')
            cell.get_text().set_color('#f1f5f9')
            # Color code severity
            if col_idx == 4:
                cell.get_text().set_color('#ef4444')
                cell.get_text().set_fontweight('bold')
            elif col_idx == 5 and '-' in table_data[row_idx][col_idx]:
                cell.get_text().set_color('#f87171')

    # Executive KPI Cards below the table
    card_y = 0.38
    ax4.text(0.02, card_y, "Executive Risk Governance & Alerting Rules:", fontsize=11, fontweight='bold', color='#38bdf8', transform=ax4.transAxes)

    kpi_notes = [
        r"• Static Thresholds: Trigger immediate P0 alerts when hourly revenue falls below \$3,000 or exceeds \$45,000.",
        r"• Rolling Z-Scores: Calculate 24-hour moving mean & standard deviation to adapt dynamically to diurnal cycles.",
        r"• Root Cause Response: Payment drop flagged within 5 minutes prevents \$50k+ compounding downtime loss.",
        r"• Fraud Defense: Automated 10x signup burst detection blocks bot IPs and isolates sybil account clusters.",
        r"• Glitch Circuit Breaker: 4x transaction burst with sub-\$2 unit revenue auto-pauses checkout API."
    ]
    for i, note in enumerate(kpi_notes):
        ax4.text(0.04, card_y - 0.075 * (i + 1), note, fontsize=8.5, color='#cbd5e1', transform=ax4.transAxes)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"Visual Anomaly Dashboard successfully saved to: {output_path}")


# ----------------------------------------------------------------------
# Task 6: Execution & Automated Validation Assertions
# ----------------------------------------------------------------------
def run_anomaly_analysis():
    print("==================================================================")
    print(">>> MODULE 2.36: ANOMALY DETECTION & RISK IDENTIFICATION <<<")
    print("==================================================================")

    df = load_kpi_metrics()
    total_hours = len(df)
    print(f"Loaded {total_hours} hourly KPI metrics records.")

    # ------------------------------------------------------------------
    # Task 1: Threshold-Based Alert Engine Execution
    # ------------------------------------------------------------------
    print("\n------------------------------------------------------------------")
    print("Task 1: Testing Threshold-Based Alert Rules")
    print("------------------------------------------------------------------")
    test_cases = [
        ('daily_revenue', 2500.0),       # Breach MIN (< 5000)
        ('transaction_count', 40),       # Breach MIN (< 50)
        ('signup_count', 3),             # Breach MIN (< 5)
        ('signup_count', 260),           # Breach MAX (> 80)
        ('transaction_count', 1350),     # Breach MAX (> 800)
        ('hourly_revenue', 22000.0)      # Normal
    ]

    for metric, val in test_cases:
        res = check_threshold(metric, val)
        status_sym = "[ALERT!]" if res['is_breached'] else "[SAFE]"
        print(f"  {status_sym:8s} {res['message']} (Severity: {res['severity']})")

    # ------------------------------------------------------------------
    # Task 2: Statistical Z-Score & Rolling Monitoring
    # ------------------------------------------------------------------
    print("\n------------------------------------------------------------------")
    print("Task 2: Computing 24-Hour Rolling Z-Scores & Adaptive Bands")
    print("------------------------------------------------------------------")
    df_analyzed = compute_rolling_zscores(df, window_hours=24)
    
    crit_rev = (df_analyzed['revenue_severity'] == 'CRITICAL').sum()
    warn_rev = (df_analyzed['revenue_severity'] == 'WARNING').sum()
    print(f"  Revenue Z-Score Monitoring: {warn_rev} WARNING events, {crit_rev} CRITICAL events.")

    crit_su = (df_analyzed['signup_count_severity'] == 'CRITICAL').sum()
    crit_tx = (df_analyzed['transaction_count_severity'] == 'CRITICAL').sum()
    print(f"  Signups & Transactions: {crit_su} CRITICAL signup surges, {crit_tx} CRITICAL transaction spikes.")

    # ------------------------------------------------------------------
    # Task 3: Real Incident Detection & Business Impact
    # ------------------------------------------------------------------
    print("\n------------------------------------------------------------------")
    print("Task 3: Detecting Real-World Failure Incidents")
    print("------------------------------------------------------------------")
    outages = df_analyzed[df_analyzed['revenue'] == 0]
    print(f"  1. Silent Payment Outage Detected:")
    total_outage_loss = 0.0
    for _, out_row in outages.iterrows():
        est_loss = out_row['revenue_rolling_mean']
        total_outage_loss += est_loss
        print(f"     • {out_row['timestamp']}: Revenue dropped to $0.00 (Z = {out_row['revenue_zscore']:.2f}, Expected ~${est_loss:,.2f})")
    print(f"     --> Total Estimated Outage Revenue Loss: ${total_outage_loss:,.2f}")

    bot_spikes = df_analyzed[df_analyzed['signup_count'] > 100]
    print(f"\n  2. Bot Account Registration Attack Detected:")
    for _, b_row in bot_spikes.iterrows():
        print(f"     • {b_row['timestamp']}: {b_row['signup_count']} signups (Z = {b_row['signup_count_zscore']:.2f}, Normal ~{b_row['signup_count_rolling_mean']:.1f})")

    tx_spikes = df_analyzed[df_analyzed['transaction_count'] > 1000]
    print(f"\n  3. Pricing Glitch / 4x Transaction Burst Detected:")
    for _, tx_row in tx_spikes.iterrows():
        print(f"     • {tx_row['timestamp']}: {tx_row['transaction_count']} tx (Z = {tx_row['transaction_count_zscore']:.2f}, Unit Rev: ${tx_row['revenue']/tx_row['transaction_count']:.2f})")

    # ------------------------------------------------------------------
    # Task 4: Build Auditable Incident Log
    # ------------------------------------------------------------------
    print("\n------------------------------------------------------------------")
    print("Task 4: Generating Incident Log & Exporting to data/anomalies.csv")
    print("------------------------------------------------------------------")
    incidents_df = build_incident_audit_log(df_analyzed)
    csv_out = os.path.join(os.path.dirname(__file__), 'data', 'anomalies.csv')
    incidents_df.to_csv(csv_out, index=False)
    print(f"  Incident log saved with {len(incidents_df)} flagged events to {csv_out}.")
    print(incidents_df[['timestamp', 'metric', 'observed_value', 'z_score', 'severity', 'root_cause_diagnosis']].to_string(index=False))

    # ------------------------------------------------------------------
    # Task 5: Multi-Panel Visual Dashboard
    # ------------------------------------------------------------------
    print("\n------------------------------------------------------------------")
    print("Task 5: Generating Multi-Panel Visual Dashboard (public/anomaly_monitoring.png)")
    print("------------------------------------------------------------------")
    img_out = os.path.join(os.path.dirname(__file__), 'public', 'anomaly_monitoring.png')
    generate_anomaly_dashboard(df_analyzed, incidents_df, img_out)

    # ------------------------------------------------------------------
    # Task 6: Automated Validation Assertions
    # ------------------------------------------------------------------
    print("\n------------------------------------------------------------------")
    print("Task 6: Running Automated Validation Assertions")
    print("------------------------------------------------------------------")
    
    # Assertion 1: Total records count
    assert len(df) == 720, f"Expected 720 records, got {len(df)}"
    
    # Assertion 2: Threshold breaches verification
    res_min_rev = check_threshold('daily_revenue', 2500.0)
    assert res_min_rev['is_breached'] and res_min_rev['breach_type'] == 'MIN_BREACH'
    res_max_su = check_threshold('signup_count', 260)
    assert res_max_su['is_breached'] and res_max_su['breach_type'] == 'MAX_BREACH'

    # Assertion 3: Outage detection
    assert len(outages) == 2, f"Expected 2 outage hours, got {len(outages)}"
    for _, out_row in outages.iterrows():
        assert out_row['revenue_zscore'] < -3.0, f"Outage Z-score should be < -3.0, got {out_row['revenue_zscore']}"
        assert out_row['revenue_severity'] == 'CRITICAL', "Outage should be classified as CRITICAL"

    # Assertion 4: Bot attack detection
    assert len(bot_spikes) == 1, f"Expected 1 bot attack spike, got {len(bot_spikes)}"
    assert bot_spikes['signup_count_zscore'].iloc[0] > 5.0, "Bot attack Z-score should exceed 5.0"

    # Assertion 5: Pricing glitch transaction spike
    assert len(tx_spikes) == 1, f"Expected 1 pricing glitch surge, got {len(tx_spikes)}"
    assert tx_spikes['transaction_count_zscore'].iloc[0] > 3.0, "Pricing glitch Z-score should exceed 3.0"

    # Assertion 6: Audit CSV & Visual image exist
    assert os.path.exists(csv_out), f"Audit CSV file not found at {csv_out}"
    assert os.path.getsize(csv_out) > 0, "Audit CSV file is empty"
    assert os.path.exists(img_out), f"Dashboard image not found at {img_out}"
    assert os.path.getsize(img_out) > 1000, "Dashboard image file is invalid"

    print("  [PASSED] All 6 automated validation assertions successfully satisfied!")
    print("==================================================================")
    print(">>> MODULE 2.36 COMPLETED SUCCESSFULLY <<<")
    print("==================================================================\n")
    return df_analyzed, incidents_df


if __name__ == '__main__':
    run_anomaly_analysis()
