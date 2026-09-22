"""
Main entry point for running SQL analytics, business metrics, and multi-table join validations.
"""
from metrics_runner import run_metrics
from run_filtering_analysis import run_all_queries
from joins_runner import run_joins_analysis
from distribution_runner import run_distribution_analysis

if __name__ == '__main__':
    print("\n=======================================================")
    print(">>> 1. RUNNING MODULE 2.38: SQL BUSINESS METRICS <<<")
    print("=======================================================\n")
    run_metrics()

    print("\n=======================================================")
    print(">>> 2. RUNNING MODULE: FILTERING & AGGREGATION (WHERE vs HAVING) <<<")
    print("=======================================================\n")
    run_all_queries()

    print("\n=======================================================")
    print(">>> 3. RUNNING MODULE 2.40: SQL JOINS & MULTI-TABLE ANALYSIS <<<")
    print("=======================================================\n")
    run_joins_analysis()

    print("\n=======================================================")
    print(">>> 4. RUNNING MODULE 2.28: DISTRIBUTION ANALYSIS FOR BUSINESS TRENDS <<<")
    print("=======================================================\n")
    run_distribution_analysis()
