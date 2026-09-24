"""
Main entry point for running SQL analytics, business metrics, and multi-table join validations.
"""
from metrics_runner import run_metrics
from run_filtering_analysis import run_all_queries
from joins_runner import run_joins_analysis
from distribution_runner import run_distribution_analysis
from segment_aggregation_runner import run_segment_aggregation
from funnel_analysis_runner import run_funnel_analysis
from anomaly_runner import run_anomaly_analysis
from query_optimization_runner import run_query_optimization
from visualisation_principles_runner import run_visualisation_principles
from data_storytelling_runner import run_data_storytelling
from streamlit_structure_runner import run_streamlit_structure_analysis
from session_state_runner import run_session_state_analysis

if __name__ == '__main__':
    print("\n=======================================================")
    print(">>> 1. RUNNING MODULE 2.38: SQL BUSINESS METRICS <<<")
    print("=======================================================\n")
    run_metrics()

    print("\n=======================================================")
    print(">>> 2. RUNNING MODULE: FILTERING & AGGREGATION (WHERE vs HAVING) <<<")
    print("=======================================================")
    run_all_queries()

    print("\n=======================================================")
    print(">>> 3. RUNNING MODULE 2.40: SQL JOINS & MULTI-TABLE ANALYSIS <<<")
    print("=======================================================\n")
    run_joins_analysis()

    print("\n=======================================================")
    print(">>> 4. RUNNING MODULE 2.28: DISTRIBUTION ANALYSIS FOR BUSINESS TRENDS <<<")
    print("=======================================================\n")
    run_distribution_analysis()

    print("\n=======================================================")
    print(">>> 5. RUNNING MODULE 2.30: GROUPBY AGGREGATION & SEGMENT INSIGHTS <<<")
    print("=======================================================\n")
    run_segment_aggregation()

    print("\n=======================================================")
    print(">>> 6. RUNNING MODULE 2.33: FUNNEL ANALYSIS & DROP-OFF DETECTION <<<")
    print("=======================================================\n")
    run_funnel_analysis()

    print("\n=======================================================")
    print(">>> 7. RUNNING MODULE 2.36: ANOMALY DETECTION & RISK IDENTIFICATION <<<")
    print("=======================================================\n")
    run_anomaly_analysis()

    print("\n=======================================================")
    print(">>> 8. RUNNING MODULE: SQL QUERY OPTIMIZATION & PERFORMANCE TUNING <<<")
    print("=======================================================\n")
    run_query_optimization()

    print("\n=======================================================")
    print(">>> 9. RUNNING MODULE 2.45: BUSINESS VISUALISATION PRINCIPLES <<<")
    print("=======================================================\n")
    run_visualisation_principles()

    print("\n=======================================================")
    print(">>> 10. RUNNING MODULE 2.48: DATA STORYTELLING & INSIGHT NARRATIVE <<<")
    print("=======================================================\n")
    run_data_storytelling()

    print("\n=======================================================")
    print(">>> 11. RUNNING MODULE 2.51: STREAMLIT APP STRUCTURE & NAVIGATION <<<")
    print("=======================================================\n")
    run_streamlit_structure_analysis()

    print("\n=======================================================")
    print(">>> 12. RUNNING MODULE 2.52: STREAMLIT SESSION STATE & WORKFLOWS <<<")
    print("=======================================================\n")
    run_session_state_analysis()



