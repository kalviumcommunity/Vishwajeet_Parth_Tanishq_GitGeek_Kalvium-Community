"""
SQL Filtering, Grouping & Aggregation (WHERE vs HAVING) - Runner & Validator
Executes queries for Tasks 1 to 5, the core architecture question, and the bonus
percentage share calculation, running automated assertions to ensure correct behavior.
"""
import os
import sys
import pandas as pd
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


def load_query(query_name):
    """Load SQL query from file."""
    path = os.path.join(os.path.dirname(__file__), 'queries', f'{query_name}.sql')
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def run_all_queries():
    print("=================================================================")
    print("Core Question: Enterprise Customers with >$10k Annual Spending")
    print("=================================================================")
    q_core = load_query('enterprise_annual_spending')
    df_core = pd.read_sql(q_core, engine)
    print(df_core.head(5))
    print(f"Total qualifying Enterprise customers: {len(df_core)}")
    assert (df_core['customer_type'] == 'Enterprise').all(), "Non-Enterprise customer returned"
    assert (df_core['annual_spending'] > 10000).all(), "Spending <= 10000 found in results"

    print("\n=================================================================")
    print("Task 1: WHERE Filtering (Data Quality Before Grouping)")
    print("=================================================================")
    q1 = load_query('where_filtering')
    df1 = pd.read_sql(q1, engine)
    print(df1.head(5))
    print(f"Total customers evaluated: {len(df1)}")
    assert df1.isnull().sum().sum() == 0, "Task 1 has null values"
    assert (df1['annual_revenue'] > 0).all(), "Task 1 has non-positive revenue"

    print("\n=================================================================")
    print("Task 2: GROUP BY on Multiple Dimensions & Aggregations")
    print("=================================================================")
    q2 = load_query('group_by_aggregation')
    df2 = pd.read_sql(q2, engine)
    print(df2.head(5))
    assert 'customer_type' in df2.columns and 'month' in df2.columns, "Missing dimensions"
    assert (df2['monthly_revenue'] > 0).all(), "Invalid monthly revenue"

    print("\n=================================================================")
    print("Task 3: HAVING Filtering (Group Thresholds After Aggregation)")
    print("=================================================================")
    q3 = load_query('having_filtering')
    df3 = pd.read_sql(q3, engine)
    print(df3.head(5))
    print(f"Groups meeting HAVING conditions: {len(df3)}")
    assert (df3['annual_revenue'] > 10000).all(), "HAVING threshold failed: revenue <= 10000"
    assert (df3['transaction_count'] >= 5).all(), "HAVING threshold failed: count < 5"

    print("\n=================================================================")
    print("Task 4: WHERE + HAVING Combined in a Single Query")
    print("=================================================================")
    q4 = load_query('where_having_combined')
    df4 = pd.read_sql(q4, engine)
    print(df4)
    assert (df4['segment_customers'] >= 100).all(), "HAVING failed: customers < 100"
    assert (df4['segment_revenue'] > 100000).all(), "HAVING failed: revenue <= 100000"

    print("\n=================================================================")
    print("Task 5: ORDER BY Ranking with RANK() & LIMIT")
    print("=================================================================")
    q5 = load_query('order_by_ranking')
    df5 = pd.read_sql(q5, engine)
    print(df5)
    assert len(df5) <= 20, "LIMIT 20 exceeded"
    assert 'revenue_rank' in df5.columns, "RANK() column missing"
    assert df5['revenue_rank'].iloc[0] == 1, "Top rank is not 1"

    print("\n=================================================================")
    print("Bonus: Percentage Share Computation within Groups")
    print("=================================================================")
    q_bonus = load_query('percentage_share')
    df_bonus = pd.read_sql(q_bonus, engine)
    print(df_bonus)
    assert round(df_bonus['pct_of_total_revenue'].sum(), 0) in [99.0, 100.0, 101.0], "Percentage sum mismatch"

    print("\n=================================================================")
    print("✓ All Filtering, Grouping & Aggregation Queries Validated Successfully!")
    print("=================================================================")
    return True


if __name__ == '__main__':
    run_all_queries()
