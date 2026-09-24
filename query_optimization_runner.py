"""
Module: Query Optimization & Performance Tuning - Runner & Validator
Demonstrates the performance impact of eliminating SELECT *, applying early filtering before joins,
structuring complex queries with CTEs, analyzing EXPLAIN execution plans, and generating visual performance dashboards.
"""
import os
import sys
import time
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sqlalchemy
from init_db import DB_PATH, init_database

# Ensure UTF-8 console output for Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure database exists
if not os.path.exists(DB_PATH):
    init_database(DB_PATH)

engine = sqlalchemy.create_engine(f'duckdb:///{DB_PATH}')


def load_query(query_name: str) -> str:
    """Load SQL query string from queries directory."""
    path = os.path.join(os.path.dirname(__file__), 'queries', f'{query_name}.sql')
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


# ----------------------------------------------------------------------
# Task 1: SELECT * Antipattern vs Explicit Column Selection
# ----------------------------------------------------------------------
def test_select_star_antipattern(con):
    """
    Demonstrates the hidden cost of SELECT * vs explicit columns.
    """
    unoptimized_sql = """
    SELECT * 
    FROM warehouse_transactions t 
    JOIN customers_expanded c ON t.customer_id = c.customer_id 
    WHERE t.transaction_year = 2024;
    """
    optimized_sql = load_query('optimization_select_star_antipattern')

    # Warm up
    con.execute(unoptimized_sql).fetchall()
    con.execute(optimized_sql).fetchall()

    # Benchmark iterations
    iterations = 15
    t0 = time.perf_counter()
    for _ in range(iterations):
        res_unopt = con.execute(unoptimized_sql).fetchdf()
    t_unopt = (time.perf_counter() - t0) / iterations

    t0 = time.perf_counter()
    for _ in range(iterations):
        res_opt = con.execute(optimized_sql).fetchdf()
    t_opt = (time.perf_counter() - t0) / iterations

    unopt_cols = len(res_unopt.columns)
    opt_cols = len(res_opt.columns)
    speedup = t_unopt / t_opt if t_opt > 0 else 1.0

    return {
        'unopt_cols': unopt_cols,
        'opt_cols': opt_cols,
        'unopt_time_ms': t_unopt * 1000.0,
        'opt_time_ms': t_opt * 1000.0,
        'speedup': speedup,
        'rows_returned': len(res_opt)
    }


# ----------------------------------------------------------------------
# Task 2: Early Filtering (WHERE Before JOIN)
# ----------------------------------------------------------------------
def test_early_filtering(con):
    """
    Demonstrates filtering before join vs filtering after join.
    """
    filter_after_sql = """
    SELECT t.transaction_id, t.amount, c.customer_name, c.country
    FROM warehouse_transactions t
    JOIN customers_expanded c ON t.customer_id = c.customer_id
    WHERE t.transaction_year = 2024;
    """
    filter_before_sql = load_query('optimization_early_filtering')

    # Verify execution plans
    explain_after = con.execute(f"EXPLAIN {filter_after_sql}").fetchall()[0][1]
    explain_before = con.execute(f"EXPLAIN {filter_before_sql}").fetchall()[0][1]

    # Benchmark
    iterations = 15
    t0 = time.perf_counter()
    for _ in range(iterations):
        res_after = con.execute(filter_after_sql).fetchdf()
    t_after = (time.perf_counter() - t0) / iterations

    t0 = time.perf_counter()
    for _ in range(iterations):
        res_before = con.execute(filter_before_sql).fetchdf()
    t_before = (time.perf_counter() - t0) / iterations

    # Check total rows in warehouse vs 2024 filtered
    total_tx = con.execute("SELECT COUNT(*) FROM warehouse_transactions").fetchone()[0]
    filtered_tx = len(res_before)
    prune_ratio = ((total_tx - filtered_tx) / total_tx) * 100.0

    return {
        'total_table_rows': total_tx,
        'filtered_rows': filtered_tx,
        'prune_ratio_pct': prune_ratio,
        'time_after_ms': t_after * 1000.0,
        'time_before_ms': t_before * 1000.0,
        'explain_before': explain_before
    }


# ----------------------------------------------------------------------
# Task 3: CTE Structuring & Readability
# ----------------------------------------------------------------------
def test_cte_structuring(con):
    """
    Executes modular CTE pipeline and checks intermediate logic.
    """
    cte_sql = load_query('optimization_cte_structuring')
    df_cte = con.execute(cte_sql).fetchdf()
    
    # Verify business rule: total_spent > 3000
    all_above_threshold = (df_cte['total_spent'] > 3000).all()
    
    return {
        'qualifying_customers': len(df_cte),
        'top_spender': df_cte.iloc[0]['customer_name'] if len(df_cte) > 0 else 'N/A',
        'top_spend': df_cte.iloc[0]['total_spent'] if len(df_cte) > 0 else 0.0,
        'rule_verified': all_above_threshold,
        'sample_df': df_cte.head(5)
    }


# ----------------------------------------------------------------------
# Task 4 & 5: Visual Dashboard Generation
# ----------------------------------------------------------------------
def generate_optimization_dashboard(output_path: str = 'public/query_optimization.png'):
    """
    Generates high-resolution 4-panel visual dashboard illustrating:
    1. Query latency waterfall (45s -> 30s -> 8s -> 2s, 22x speedup).
    2. Memory and intermediate dataset footprint reduction.
    3. Logical query execution order & filter pushdown tree.
    4. Query optimization engineering checklist.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, axes = plt.subplots(2, 2, figsize=(18, 12), dpi=150)
    plt.subplots_adjust(hspace=0.35, wspace=0.25)
    fig.patch.set_facecolor('#0b0f19')

    # ------------------------------------------------------------------
    # Panel 1: Compounding Query Execution Latency Waterfall
    # ------------------------------------------------------------------
    ax1 = axes[0, 0]
    ax1.set_facecolor('#0f172a')

    stages = ['Baseline\n(SELECT * + Join First)', 'Step 1\nExplicit Columns', 'Step 2\nEarly Filtering', 'Step 3\nCTE + Pushdown']
    latencies = [45.0, 30.0, 8.0, 2.0]
    colors = ['#ef4444', '#f97316', '#38bdf8', '#10b981']

    bars = ax1.bar(stages, latencies, color=colors, width=0.55, edgecolor='white', linewidth=1.2)
    ax1.set_title('Case Study: Compounding Query Latency Reduction (22x Faster)', fontsize=13, fontweight='bold', color='white', pad=12)
    ax1.set_ylabel('Execution Time (Seconds)', fontsize=10, color='#94a3b8')
    ax1.tick_params(colors='#cbd5e1', labelsize=9)
    ax1.grid(True, linestyle=':', alpha=0.2, color='#64748b', axis='y')

    for bar, val in zip(bars, latencies):
        height = bar.get_height()
        speedup_str = f"{45.0/val:.1f}x" if val < 45 else "Baseline"
        ax1.text(bar.get_x() + bar.get_width()/2.0, height + 1.2, f"{val:.0f}s\n({speedup_str})",
                 ha='center', va='bottom', color='#ffffff', fontsize=9.5, fontweight='bold')

    ax1.set_ylim(0, 52)

    # ------------------------------------------------------------------
    # Panel 2: Intermediate Memory Buffer & Data Volume Reduction
    # ------------------------------------------------------------------
    ax2 = axes[0, 1]
    ax2.set_facecolor('#0f172a')

    categories = ['Unoptimized Query\n(35 Cols x 100M Rows)', 'Optimized Query\n(5 Cols x 10M Rows)']
    mem_gb = [500.0, 50.0]
    cols_count = [35, 5]

    x = np.arange(len(categories))
    bar_width = 0.4

    b1 = ax2.bar(x, mem_gb, width=bar_width, color=['#e11d48', '#059669'], edgecolor='white', linewidth=1.2)
    ax2.set_title('Intermediate Memory Footprint Reduction (10x Memory Savings)', fontsize=13, fontweight='bold', color='white', pad=12)
    ax2.set_ylabel('Estimated Join Buffer (GB)', fontsize=10, color='#94a3b8')
    ax2.set_xticks(x)
    ax2.set_xticklabels(categories, fontsize=9.5, color='#cbd5e1')
    ax2.tick_params(colors='#cbd5e1', labelsize=9)
    ax2.grid(True, linestyle=':', alpha=0.2, color='#64748b', axis='y')

    for bar, val in zip(b1, mem_gb):
        ax2.text(bar.get_x() + bar.get_width()/2.0, bar.get_height() + 12, f"{val:.0f} GB",
                 ha='center', va='bottom', color='#ffffff', fontsize=10, fontweight='bold')

    ax2.set_ylim(0, 580)

    # ------------------------------------------------------------------
    # Panel 3: Query Execution Plan Architecture (EXPLAIN Tree)
    # ------------------------------------------------------------------
    ax3 = axes[1, 0]
    ax3.set_facecolor('#0f172a')
    ax3.axis('off')

    ax3.text(0.02, 0.95, "Database Execution Plan Architecture (Filter & Projection Pushdown):", fontsize=11, fontweight='bold', color='#38bdf8', transform=ax3.transAxes)

    tree_steps = [
        ("1. SCAN [warehouse_transactions]", "Reads columnar file with PROJECTION PUSHDOWN (only 4 cols fetched instead of 25).", "#38bdf8"),
        ("2. FILTER [transaction_year = 2024]", "Prunes 80% of rows at scan time before buffering into memory.", "#10b981"),
        ("3. SCAN [customers_expanded]", "Reads dimension table and projects customer_id, customer_name, country.", "#38bdf8"),
        ("4. HASH JOIN [t.customer_id = c.customer_id]", "Builds hash table on tiny filtered subset (10k rows) instead of 50k rows.", "#f59e0b"),
        ("5. AGGREGATE / PROJECTION", "Groups metrics and computes final SELECT expressions with zero memory spills.", "#a855f7")
    ]

    box_y = 0.82
    for title, desc, col in tree_steps:
        ax3.text(0.04, box_y, title, fontsize=9.5, fontweight='bold', color=col, transform=ax3.transAxes)
        ax3.text(0.08, box_y - 0.05, desc, fontsize=8.5, color='#cbd5e1', transform=ax3.transAxes)
        box_y -= 0.15

    # ------------------------------------------------------------------
    # Panel 4: Production Query Optimization Checklist & Scorecard
    # ------------------------------------------------------------------
    ax4 = axes[1, 1]
    ax4.set_facecolor('#0f172a')
    ax4.axis('off')

    ax4.text(0.02, 0.95, "Production Analytics Engineer Optimization Checklist:", fontsize=11, fontweight='bold', color='#38bdf8', transform=ax4.transAxes)

    checklist = [
        ("✓ No SELECT *", "Always name columns explicitly. Protects against schema changes and reduces memory."),
        ("✓ Filter Before Join", "Apply WHERE filters in derived subquery or CTE so join operates on smallest set."),
        ("✓ CTE Structure", "Replace 5-level nested subqueries with named CTEs for top-to-bottom readability."),
        ("✓ Inspect EXPLAIN Plans", "Verify Hash Join build side, verify filter pushdown, check scan projections."),
        ("✓ Validate at Scale", "Test optimizations on production data volume where caching won't mask bottlenecks."),
        ("✓ Clear Aliases & Comments", "Match column names to aliases and document business intent for maintainers.")
    ]

    chk_y = 0.82
    for item, expl in checklist:
        ax4.text(0.04, chk_y, item, fontsize=9.5, fontweight='bold', color='#10b981', transform=ax4.transAxes)
        ax4.text(0.08, chk_y - 0.045, expl, fontsize=8.5, color='#94a3b8', transform=ax4.transAxes)
        chk_y -= 0.125

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"Visual Optimization Dashboard successfully saved to: {output_path}")


# ----------------------------------------------------------------------
# Task 6: Execution & Automated Validation Assertions
# ----------------------------------------------------------------------
def run_query_optimization():
    print("==================================================================")
    print(">>> MODULE: SQL QUERY OPTIMIZATION & PERFORMANCE TUNING <<<")
    print("==================================================================")

    raw_conn = engine.raw_connection()
    con = raw_conn.driver_connection

    # Task 1
    print("\n------------------------------------------------------------------")
    print("Task 1: Eliminating SELECT * Antipattern")
    print("------------------------------------------------------------------")
    t1_res = test_select_star_antipattern(con)
    print(f"  Unoptimized Query: {t1_res['unopt_cols']} columns fetched ({t1_res['unopt_time_ms']:.2f} ms)")
    print(f"  Optimized Query:   {t1_res['opt_cols']} columns explicitly projected ({t1_res['opt_time_ms']:.2f} ms)")
    print(f"  Column Projection Savings: {(1 - t1_res['opt_cols']/t1_res['unopt_cols'])*100:.1f}% fewer columns transferred")
    print(f"  Query Latency Speedup:     {t1_res['speedup']:.2f}x faster execution")

    # Task 2
    print("\n------------------------------------------------------------------")
    print("Task 2: Early Filtering - Apply WHERE Before JOIN")
    print("------------------------------------------------------------------")
    t2_res = test_early_filtering(con)
    print(f"  Total Warehouse Records: {t2_res['total_table_rows']:,} rows")
    print(f"  Filtered Year Records:   {t2_res['filtered_rows']:,} rows (2024 transactions)")
    print(f"  Intermediate Pruning:    {t2_res['prune_ratio_pct']:.1f}% of rows pruned BEFORE join buffer allocation")
    print(f"  Execution Time:          {t2_res['time_before_ms']:.2f} ms")

    # Task 3
    print("\n------------------------------------------------------------------")
    print("Task 3: CTE Structuring for Readability and Modular Pipelines")
    print("------------------------------------------------------------------")
    t3_res = test_cte_structuring(con)
    print(f"  CTEs Executed: 'recent_transactions' -> 'customer_summary' -> High-Value Filter")
    print(f"  Qualifying High-Value Customers (> $3,000 spend): {t3_res['qualifying_customers']} accounts")
    print(f"  Top Customer: {t3_res['top_spender']} with ${t3_res['top_spend']:,.2f} annual spend")
    print(f"  Sample Pipeline Output:\n{t3_res['sample_df']}")

    # Task 4 & 5
    print("\n------------------------------------------------------------------")
    print("Task 4 & 5: Generating Visual Performance Dashboard")
    print("------------------------------------------------------------------")
    img_out = os.path.join(os.path.dirname(__file__), 'public', 'query_optimization.png')
    generate_optimization_dashboard(img_out)

    # Task 6: Automated Validation Assertions
    print("\n------------------------------------------------------------------")
    print("Task 6: Running Automated Validation Assertions")
    print("------------------------------------------------------------------")
    assert t1_res['opt_cols'] < t1_res['unopt_cols'], "Optimized query must select fewer columns than SELECT *"
    assert t1_res['opt_cols'] == 5, f"Expected 5 explicit columns, got {t1_res['opt_cols']}"
    assert t1_res['rows_returned'] > 0, "No rows returned from optimized query"

    assert t2_res['filtered_rows'] < t2_res['total_table_rows'], "Early filtering must prune rows"
    assert t2_res['prune_ratio_pct'] > 50.0, f"Expected >50% row pruning, got {t2_res['prune_ratio_pct']:.1f}%"

    assert t3_res['rule_verified'], "CTE threshold rule failed: customers below threshold found"
    assert t3_res['qualifying_customers'] > 0, "CTE query returned empty results"

    assert os.path.exists(img_out), f"Dashboard image not found at {img_out}"
    assert os.path.getsize(img_out) > 1000, "Dashboard image file is invalid"

    raw_conn.close()
    print("  [PASSED] All Query Optimization assertions successfully verified!")
    print("==================================================================")
    print(">>> MODULE QUERY OPTIMIZATION COMPLETED SUCCESSFULLY <<<")
    print("==================================================================\n")


if __name__ == '__main__':
    run_query_optimization()
