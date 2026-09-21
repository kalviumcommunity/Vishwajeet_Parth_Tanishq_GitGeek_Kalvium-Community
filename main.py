"""
Main entry point for running SQL analytics, business metrics, and filtering validations.
"""
from metrics_runner import run_metrics
from run_filtering_analysis import run_all_queries

if __name__ == '__main__':
    print("\n=======================================================")
    print(">>> 1. RUNNING MODULE 2.38: SQL BUSINESS METRICS <<<")
    print("=======================================================\n")
    run_metrics()

    print("\n=======================================================")
    print(">>> 2. RUNNING MODULE: FILTERING & AGGREGATION (WHERE vs HAVING) <<<")
    print("=======================================================\n")
    run_all_queries()
