"""
Module 2.45: Business Visualisation Principles - Runner & Validator
Demonstrates the five fundamental chart types, complete labeling rules, human-readable formatting,
unified accessible color palettes with dual-encoding, high-impact annotations, and target reference lines.
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Ensure UTF-8 console output for Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# ----------------------------------------------------------------------
# Core Visual Design Standards: Unified Palette & Accessibility
# ----------------------------------------------------------------------
PALETTE = {
    'primary': '#0284c7',     # Ocean Blue
    'secondary': '#f59e0b',   # Amber Orange
    'success': '#10b981',     # Emerald Green
    'danger': '#ef4444',      # Rose Red
    'purple': '#a855f7',      # Violet
    'neutral': '#64748b',     # Slate Grey
    'dark_bg': '#0b0f19',     # Obsidian Black
    'panel_bg': '#0f172a',    # Deep Slate
    'text': '#f8fafc',        # Clean White
    'text_muted': '#94a3b8'   # Light Grey
}

CHART_COLORS = ['#0284c7', '#f59e0b', '#10b981', '#a855f7', '#06b6d4', '#ec4899']

# Dual-encoding styles for accessibility (color-blindness support)
ACCESSIBILITY_STYLES = {
    'Enterprise': {'color': '#0284c7', 'marker': 'o', 'linestyle': '-'},
    'SMB':        {'color': '#f59e0b', 'marker': 's', 'linestyle': '--'},
    'Startup':    {'color': '#10b981', 'marker': '^', 'linestyle': ':'}
}


def currency_formatter(x, pos):
    """Formats large currency values into readable $K or $M strings."""
    if abs(x) >= 1e6:
        return f"${x*1e-6:.1f}M"
    elif abs(x) >= 1e3:
        return f"${x*1e-3:.0f}K"
    else:
        return f"${x:.0f}"


# ----------------------------------------------------------------------
# Task 1: Generate Mock Realistic Datasets
# ----------------------------------------------------------------------
def generate_sample_data():
    """Generates deterministic business datasets for the 5 chart types."""
    np.random.seed(42)

    # 1. Bar Chart Data: Q4 Revenue by Product Line (Discrete Category Comparison)
    products = ['Cloud Enterprise Server', 'Security Gateway Suite', 'Database Cluster Node',
                'API Management Platform', 'Analytics Dashboard Pro']
    revenue_q4 = [6450000.0, 4820000.0, 3950000.0, 2680000.0, 1850000.0]
    df_products = pd.DataFrame({'product': products, 'revenue': revenue_q4})

    # 2. Line Chart Data: Monthly Revenue Trends (Continuous Time Series across Segments)
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    base_ent = np.linspace(3.2e6, 5.8e6, 12) + np.random.normal(0, 1.2e5, 12)
    base_smb = np.linspace(1.8e6, 2.7e6, 12) + np.random.normal(0, 0.8e5, 12)
    # Seasonal peak in November / December
    base_ent[10] += 6.5e5
    base_ent[11] += 8.2e5
    df_trends = pd.DataFrame({
        'month': months,
        'Enterprise': base_ent,
        'SMB': base_smb
    })

    # 3. Histogram Data: Order Value Distribution (Skewness & Spread)
    # Log-normal distribution typical of e-commerce / SaaS spend
    order_values = np.random.lognormal(mean=5.2, sigma=0.85, size=4000)
    order_values = np.clip(order_values, 20.0, 3500.0)

    # 4. Scatter Plot Data: Marketing Spend vs Incremental Revenue (Correlation)
    spend = np.random.uniform(15000, 120000, 80)
    # Linear relationship with noise: Revenue = 3.8 * Spend + $40k + Noise
    rev = 3.8 * spend + 40000.0 + np.random.normal(0, 45000.0, 80)
    df_scatter = pd.DataFrame({'marketing_spend': spend, 'revenue': rev})

    # 5. Stacked Bar Data: Quarterly Product Composition (Part-to-Whole, max 4 segments)
    quarters = ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024']
    comp_data = {
        'Cloud Server': [2.8e6, 3.4e6, 4.1e6, 5.2e6],
        'Security Suite': [1.9e6, 2.2e6, 2.6e6, 3.1e6],
        'Analytics Pro': [1.2e6, 1.5e6, 1.7e6, 2.0e6],
        'Developer SaaS': [0.8e6, 1.0e6, 1.1e6, 1.4e6]
    }
    df_comp = pd.DataFrame(comp_data, index=quarters)

    return df_products, df_trends, order_values, df_scatter, df_comp


# ----------------------------------------------------------------------
# Task 2: Build Multi-Panel Business Visualisation Showcase
# ----------------------------------------------------------------------
def generate_visualisation_showcase(output_path: str = 'public/business_visualisation_principles.png'):
    """
    Renders an executive 6-panel showcase illustrating:
    1. Horizontal Bar Chart with Currency Formatting & Data Labels.
    2. Multi-Line Time Series with Dual Encoding (Markers + Line Styles) & Annotation.
    3. Distribution Histogram with Mean vs Median Reference Lines.
    4. Scatter Plot with OLS Regression Trendline & Correlation Coefficient.
    5. Stacked Bar Composition (Part-to-Whole) showing Whole & Parts.
    6. Visual Design Principles & Accessibility Scorecard.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_products, df_trends, order_values, df_scatter, df_comp = generate_sample_data()

    fig, axes = plt.subplots(3, 2, figsize=(20, 18), dpi=150)
    plt.subplots_adjust(hspace=0.38, wspace=0.25)
    fig.patch.set_facecolor(PALETTE['dark_bg'])

    # ------------------------------------------------------------------
    # Panel 1: Bar Chart (Comparison Across Categories)
    # ------------------------------------------------------------------
    ax1 = axes[0, 0]
    ax1.set_facecolor(PALETTE['panel_bg'])
    y_pos = np.arange(len(df_products))
    
    # Sort descending so top product is at top
    df_prod_sorted = df_products.sort_values('revenue', ascending=True)
    bars = ax1.barh(df_prod_sorted['product'], df_prod_sorted['revenue'], 
                    color=PALETTE['primary'], edgecolor='white', linewidth=1.0, height=0.6)
    
    ax1.set_title('1. BAR CHART: Comparison Across Categories\n(Q4 Revenue by Product Line)', 
                  fontsize=12, fontweight='bold', color=PALETTE['text'], pad=10)
    ax1.set_xlabel('Revenue (USD)', fontsize=10, color=PALETTE['text_muted'])
    ax1.set_ylabel('Product Line', fontsize=10, color=PALETTE['text_muted'])
    ax1.xaxis.set_major_formatter(ticker.FuncFormatter(currency_formatter))
    ax1.tick_params(colors=PALETTE['text_muted'], labelsize=9)
    ax1.grid(True, linestyle=':', alpha=0.2, color=PALETTE['neutral'], axis='x')

    # Data labels on bars for effortless readability
    for bar in bars:
        w = bar.get_width()
        ax1.text(w + 1.2e5, bar.get_y() + bar.get_height()/2.0, f"${w*1e-6:.2f}M",
                 ha='left', va='center', color='white', fontsize=8.5, fontweight='bold')
    ax1.set_xlim(0, 7.5e6)

    # ------------------------------------------------------------------
    # Panel 2: Line Chart (Trends Over Continuous Time with Dual Encoding)
    # ------------------------------------------------------------------
    ax2 = axes[0, 1]
    ax2.set_facecolor(PALETTE['panel_bg'])

    x_vals = np.arange(len(df_trends))
    for segment in ['Enterprise', 'SMB']:
        style = ACCESSIBILITY_STYLES[segment]
        ax2.plot(x_vals, df_trends[segment], label=f'{segment} Segment', 
                 color=style['color'], marker=style['marker'], markersize=6,
                 linestyle=style['linestyle'], linewidth=2.0)

    # Target Reference Line
    target_val = 5.0e6
    ax2.axhline(y=target_val, color=PALETTE['success'], linestyle='--', linewidth=1.8, label=r'Target (\$5.0M Benchmark)')

    # High-Impact Peak Annotation
    peak_idx = 11  # Dec
    peak_val = df_trends['Enterprise'].iloc[peak_idx]
    ax2.annotate(
        f"Peak Q4 Close\n(\${peak_val*1e-6:.2f}M)",
        xy=(peak_idx, peak_val),
        xytext=(peak_idx - 2.5, peak_val + 5.5e5),
        arrowprops=dict(facecolor=PALETTE['danger'], shrink=0.08, width=1.5, headwidth=6),
        fontsize=9, fontweight='bold', color='white',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#dc2626', edgecolor='white', alpha=0.9)
    )

    ax2.set_title('2. LINE CHART: Trends Over Time & Target Benchmark\n(Monthly Revenue Progression by Customer Tier)',
                  fontsize=12, fontweight='bold', color=PALETTE['text'], pad=10)
    ax2.set_xlabel('Fiscal Month (2024)', fontsize=10, color=PALETTE['text_muted'])
    ax2.set_ylabel('Monthly Revenue (USD)', fontsize=10, color=PALETTE['text_muted'])
    ax2.set_xticks(x_vals)
    ax2.set_xticklabels(df_trends['month'], fontsize=9, color=PALETTE['text_muted'])
    ax2.yaxis.set_major_formatter(ticker.FuncFormatter(currency_formatter))
    ax2.tick_params(colors=PALETTE['text_muted'], labelsize=9)
    ax2.grid(True, linestyle=':', alpha=0.2, color=PALETTE['neutral'])
    ax2.legend(loc='upper left', framealpha=0.85, facecolor=PALETTE['panel_bg'], 
               edgecolor=PALETTE['neutral'], labelcolor='white', fontsize=8.5)
    ax2.set_ylim(1.0e6, 7.8e6)

    # ------------------------------------------------------------------
    # Panel 3: Histogram (Distribution of Values & Spread)
    # ------------------------------------------------------------------
    ax3 = axes[1, 0]
    ax3.set_facecolor(PALETTE['panel_bg'])

    mean_val = np.mean(order_values)
    median_val = np.median(order_values)

    counts, bins, patches = ax3.hist(order_values, bins=45, color=PALETTE['primary'], 
                                     alpha=0.6, edgecolor='white', linewidth=0.5)

    # Mean vs Median reference lines exposing positive skewness
    ax3.axvline(median_val, color=PALETTE['success'], linewidth=2.0, linestyle='-', label=f'Median: \${median_val:.0f}')
    ax3.axvline(mean_val, color=PALETTE['danger'], linewidth=2.0, linestyle='--', label=f'Mean (Skewed): \${mean_val:.0f}')

    # Annotation explaining skewness
    ax3.text(0.48, 0.72, f"Skewed Distribution:\nMean (\${mean_val:.0f}) > Median (\${median_val:.0f})\nUse Median for typical customer",
             transform=ax3.transAxes, fontsize=8.5, color='white',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#1e293b', edgecolor=PALETTE['secondary'], alpha=0.9))

    ax3.set_title('3. HISTOGRAM: Distribution of Values & Spread\n(Customer Order Size Frequency Distribution)',
                  fontsize=12, fontweight='bold', color=PALETTE['text'], pad=10)
    ax3.set_xlabel('Order Value (USD)', fontsize=10, color=PALETTE['text_muted'])
    ax3.set_ylabel('Transaction Count', fontsize=10, color=PALETTE['text_muted'])
    ax3.xaxis.set_major_formatter(ticker.FuncFormatter(currency_formatter))
    ax3.tick_params(colors=PALETTE['text_muted'], labelsize=9)
    ax3.grid(True, linestyle=':', alpha=0.2, color=PALETTE['neutral'], axis='y')
    ax3.legend(loc='upper right', framealpha=0.85, facecolor=PALETTE['panel_bg'], 
               edgecolor=PALETTE['neutral'], labelcolor='white', fontsize=8.5)

    # ------------------------------------------------------------------
    # Panel 4: Scatter Plot (Correlation Between Two Variables)
    # ------------------------------------------------------------------
    ax4 = axes[1, 1]
    ax4.set_facecolor(PALETTE['panel_bg'])

    x_sp = df_scatter['marketing_spend']
    y_rv = df_scatter['revenue']

    # Scatter dots with opacity to show density
    ax4.scatter(x_sp, y_rv, color=PALETTE['secondary'], s=55, alpha=0.75, edgecolors='white', linewidth=0.8, label='Regional Campaigns')

    # OLS Trendline: Y = m*X + c
    slope, intercept = np.polyfit(x_sp, y_rv, 1)
    corr_coef = np.corrcoef(x_sp, y_rv)[0, 1]
    x_line = np.linspace(x_sp.min(), x_sp.max(), 100)
    y_line = slope * x_line + intercept

    ax4.plot(x_line, y_line, color=PALETTE['danger'], linewidth=2.0, linestyle='-', label=f'Trendline (r = {corr_coef:.2f})')

    ax4.set_title('4. SCATTER PLOT: Correlation Between Variables\n(Marketing Spend vs Incremental Revenue)',
                  fontsize=12, fontweight='bold', color=PALETTE['text'], pad=10)
    ax4.set_xlabel('Marketing Campaign Spend (USD)', fontsize=10, color=PALETTE['text_muted'])
    ax4.set_ylabel('Generated Revenue (USD)', fontsize=10, color=PALETTE['text_muted'])
    ax4.xaxis.set_major_formatter(ticker.FuncFormatter(currency_formatter))
    ax4.yaxis.set_major_formatter(ticker.FuncFormatter(currency_formatter))
    ax4.tick_params(colors=PALETTE['text_muted'], labelsize=9)
    ax4.grid(True, linestyle=':', alpha=0.2, color=PALETTE['neutral'])
    ax4.legend(loc='upper left', framealpha=0.85, facecolor=PALETTE['panel_bg'], 
               edgecolor=PALETTE['neutral'], labelcolor='white', fontsize=8.5)

    # Annotation quantifying ROI
    ax4.text(0.55, 0.18, f"Strong Positive Correlation (r = {corr_coef:.2f})\nMarginal ROI: \${slope:.1f}x per \$1 Spend",
             transform=ax4.transAxes, fontsize=8.5, color='white',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#1e293b', edgecolor=PALETTE['success'], alpha=0.9))

    # ------------------------------------------------------------------
    # Panel 5: Stacked Bar Chart (Part-to-Whole Composition)
    # ------------------------------------------------------------------
    ax5 = axes[2, 0]
    ax5.set_facecolor(PALETTE['panel_bg'])

    q_idx = np.arange(len(df_comp))
    bottom_vals = np.zeros(len(df_comp))
    colors_stacked = ['#0284c7', '#f59e0b', '#10b981', '#a855f7']

    for i, col_name in enumerate(df_comp.columns):
        vals = df_comp[col_name].values
        ax5.bar(q_idx, vals, bottom=bottom_vals, label=col_name, color=colors_stacked[i],
                width=0.55, edgecolor='white', linewidth=0.8)
        bottom_vals += vals

    # Total label on top of each stack
    for idx, total_h in enumerate(bottom_vals):
        ax5.text(idx, total_h + 2.5e5, f"${total_h*1e-6:.1f}M", ha='center', va='bottom',
                 color='white', fontsize=9, fontweight='bold')

    ax5.set_title('5. STACKED BAR: Part-to-Whole Composition\n(Quarterly Revenue Composition by Product Line)',
                  fontsize=12, fontweight='bold', color=PALETTE['text'], pad=10)
    ax5.set_xlabel('Fiscal Quarter', fontsize=10, color=PALETTE['text_muted'])
    ax5.set_ylabel('Total Revenue (USD)', fontsize=10, color=PALETTE['text_muted'])
    ax5.set_xticks(q_idx)
    ax5.set_xticklabels(df_comp.index, fontsize=9, color=PALETTE['text_muted'])
    ax5.yaxis.set_major_formatter(ticker.FuncFormatter(currency_formatter))
    ax5.tick_params(colors=PALETTE['text_muted'], labelsize=9)
    ax5.grid(True, linestyle=':', alpha=0.2, color=PALETTE['neutral'], axis='y')
    ax5.legend(loc='upper left', framealpha=0.85, facecolor=PALETTE['panel_bg'], 
               edgecolor=PALETTE['neutral'], labelcolor='white', fontsize=8.0)
    ax5.set_ylim(0, 13.5e6)

    # ------------------------------------------------------------------
    # Panel 6: Design Framework & Complete Labelling Matrix
    # ------------------------------------------------------------------
    ax6 = axes[2, 1]
    ax6.set_facecolor(PALETTE['panel_bg'])
    ax6.axis('off')

    ax6.text(0.02, 0.95, "The 5 Essential Labelling Elements & Design Principles:", 
             fontsize=11.5, fontweight='bold', color=PALETTE['primary'], transform=ax6.transAxes)

    principles = [
        ("1. Actionable Title", "Answers 'What does this show?' (e.g. 'Q4 Revenue by Product Line')."),
        ("2. Explicit X & Y Axes", "Always includes units (e.g. 'Revenue (USD)', 'Month', 'Transactions')."),
        ("3. Human-Readable Ticks", "Formats \$5.2M instead of 5200000; 'Jan 2024' instead of '2024-01-01'."),
        ("4. Accessible Palette", "Unified colors; dual encoding (shapes, dash patterns) for color blindness."),
        ("5. Meaningful Annotations", "Highlights peaks, drops, thresholds, and target reference lines (axhline)."),
        ("6. Right Chart for Relationship", "Bar (comparison), Line (trend), Hist (spread), Scatter (correlation).")
    ]

    box_y = 0.82
    for title, desc in principles:
        ax6.text(0.04, box_y, title, fontsize=9.5, fontweight='bold', color=PALETTE['success'], transform=ax6.transAxes)
        ax6.text(0.08, box_y - 0.045, desc, fontsize=8.5, color='#cbd5e1', transform=ax6.transAxes)
        box_y -= 0.13

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"Visualisation Showcase successfully saved to: {output_path}")


# ----------------------------------------------------------------------
# Task 3: Execution & Automated Verification Assertions
# ----------------------------------------------------------------------
def run_visualisation_principles():
    print("==================================================================")
    print(">>> MODULE 2.45: BUSINESS VISUALISATION PRINCIPLES <<<")
    print("==================================================================")

    df_products, df_trends, order_values, df_scatter, df_comp = generate_sample_data()

    print("\n------------------------------------------------------------------")
    print("Task 1: Validating Chart Type Dataset Alignments")
    print("------------------------------------------------------------------")
    print(f"  • Bar Chart Categories:    {len(df_products)} products (Top: {df_products.iloc[0]['product']})")
    print(f"  • Line Chart Series:        {len(df_trends)} continuous months across 2 customer segments")
    print(f"  • Histogram Observations:   {len(order_values):,} order transactions (Mean: ${np.mean(order_values):.1f}, Median: ${np.median(order_values):.1f})")
    print(f"  • Scatter Plot Data Points: {len(df_scatter)} marketing campaigns (Correlation r: {np.corrcoef(df_scatter['marketing_spend'], df_scatter['revenue'])[0,1]:.2f})")
    print(f"  • Stacked Bar Quarters:     {len(df_comp)} quarters across {len(df_comp.columns)} product lines")

    print("\n------------------------------------------------------------------")
    print("Task 2: Generating Professional Visualisation Showcase Dashboard")
    print("------------------------------------------------------------------")
    img_out = os.path.join(os.path.dirname(__file__), 'public', 'business_visualisation_principles.png')
    generate_visualisation_showcase(img_out)

    print("\n------------------------------------------------------------------")
    print("Task 3: Running Automated Verification Assertions")
    print("------------------------------------------------------------------")
    # Assertion 1: Stacked segments must be <= 5 to maintain readability
    assert len(df_comp.columns) <= 5, f"Stacked bar must have at most 5 segments, got {len(df_comp.columns)}"

    # Assertion 2: Correlation calculation must be statistically valid
    r = np.corrcoef(df_scatter['marketing_spend'], df_scatter['revenue'])[0, 1]
    assert 0.7 < r <= 1.0, f"Expected strong positive correlation, got {r:.2f}"

    # Assertion 3: Histogram must exhibit positive skewness (Mean > Median)
    assert np.mean(order_values) > np.median(order_values), "Order distribution should exhibit positive skewness"

    # Assertion 4: Currency formatter test
    assert currency_formatter(5200000, None) == "$5.2M", "Currency formatter failed on millions"
    assert currency_formatter(45000, None) == "$45K", "Currency formatter failed on thousands"

    # Assertion 5: Image creation and validity
    assert os.path.exists(img_out), f"Visualisation image not found at {img_out}"
    assert os.path.getsize(img_out) > 5000, "Visualisation image file is empty or corrupted"

    print("  [PASSED] All Business Visualisation Principles assertions verified successfully!")
    print("==================================================================")
    print(">>> MODULE 2.45 COMPLETED SUCCESSFULLY <<<")
    print("==================================================================\n")


if __name__ == '__main__':
    run_visualisation_principles()
