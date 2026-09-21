"""
2.38 SQL Business Metrics Query Design - Runner & Validator
Loads SQL queries from queries/*.sql, executes them using pandas and SQLAlchemy/DuckDB,
and validates the metric results against the assignment criteria.
"""
import os
import sys
import pandas as pd
import sqlalchemy
from init_db import DB_PATH, init_database

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure database exists
if not os.path.exists(DB_PATH):
    init_database(DB_PATH)

# Establish SQLAlchemy engine connection to DuckDB
engine = sqlalchemy.create_engine(f'duckdb:///{DB_PATH}')


def load_query(query_name):
    """Load SQL query from file."""
    query_file = os.path.join(os.path.dirname(__file__), 'queries', f'{query_name}.sql')
    with open(query_file, 'r', encoding='utf-8') as f:
        return f.read()


def run_metrics():
    print("==================================================")
    print("Executing Task 4: Load & Execute Business Metrics")
    print("==================================================")

    # 1. Monthly Active Users (Task 1)
    mau_query = load_query('monthly_active_users')
    mau = pd.read_sql(mau_query, engine)
    print("\nMonthly Active Users:")
    print(mau)

    # 2. Revenue by Segment (Task 2)
    revenue_query = load_query('revenue_by_segment')
    revenue = pd.read_sql(revenue_query, engine)
    print("\nRevenue by Segment:")
    print(revenue)

    # 3. Conversion Funnel (Task 3)
    funnel_query = load_query('conversion_funnel')
    funnel = pd.read_sql(funnel_query, engine)
    print("\nConversion Funnel:")
    print(funnel)

    print("\n==================================================")
    print("Executing Task 5: Validate Query Results")
    print("==================================================")
    validate_metrics(mau, revenue, funnel)

    # Bonus Queries for Comprehensive Understanding
    print("\n==================================================")
    print("Bonus Metrics: Cohort Retention & Rolling 7-Day")
    print("==================================================")
    try:
        cohort_query = load_query('retention_cohort')
        cohort = pd.read_sql(cohort_query, engine)
        print("\nRetention Cohort:")
        print(cohort)

        rolling_query = load_query('rolling_7day_active_users')
        rolling = pd.read_sql(rolling_query, engine)
        print("\nRolling 7-Day Active Users:")
        print(rolling)
    except Exception as ex:
        print(f"Bonus query note: {ex}")


def validate_metrics(mau_df, revenue_df, funnel_df):
    """Validate metric computation."""
    # Check for nulls
    assert mau_df.isnull().sum().sum() == 0, "MAU has nulls"
    assert revenue_df.isnull().sum().sum() == 0, "Revenue has nulls"

    # Check value ranges
    assert (revenue_df['monthly_revenue'] > 0).all(), "Revenue <= 0"
    assert (funnel_df['conversion_pct'] >= 0).all() and (funnel_df['conversion_pct'] <= 100).all(), "Conversion out of range"

    # Check consistency
    for idx, row in revenue_df.iterrows():
        assert row['order_count'] > 0, "Zero orders"
        assert row['monthly_revenue'] > 0, "Zero revenue"

    print("✓ All metrics validated")
    return True


if __name__ == '__main__':
    run_metrics()
