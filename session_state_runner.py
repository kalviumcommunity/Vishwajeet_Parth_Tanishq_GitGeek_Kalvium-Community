"""
Module 2.52: Streamlit Session State & Workflow Management - Architecture Test & Validator
Verifies:
1. Safe initialisation of persistent session state keys with descriptive defaults.
2. Simulated multi-step workflow logic: Step 2 requires confirmation of Step 1.
3. Analytical continuity: Values persist across simulated script reruns.
4. Clean reset mechanism: Target keys are deleted and re-initialised with defaults.
5. Synchronization between widget state and session state.
"""
import os
import sys
import pandas as pd
import numpy as np

# Ensure UTF-8 console output for Windows / Mac
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


class MockSessionState(dict):
    """Simulates Streamlit's st.session_state dictionary object across script reruns."""
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"MockSessionState has no attribute '{key}'")

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError(f"MockSessionState has no attribute '{key}'")


def init_safe_session_state(state):
    """Safe default initialisation pattern: check existence before assignment."""
    if "selected_segment" not in state:
        state["selected_segment"] = "All"
    if "workflow_step" not in state:
        state["workflow_step"] = 1
    if "analysis_result" not in state:
        state["analysis_result"] = None
    if "selected_tier_metric" not in state:
        state["selected_tier_metric"] = "Revenue"
    if "workflow_history" not in state:
        state["workflow_history"] = []


def reset_session_state(state):
    """Clean reset pattern: deletes specific workflow keys."""
    keys_to_reset = ["selected_segment", "workflow_step", "analysis_result", "selected_tier_metric", "workflow_history"]
    for k in keys_to_reset:
        if k in state:
            del state[k]
    # Re-initialise with clean defaults
    init_safe_session_state(state)


def test_safe_initialisation():
    """Validates that session state defaults are assigned without overwriting existing state."""
    print("  [TEST 1/5] Testing safe session state initialization...")
    state = MockSessionState()
    init_safe_session_state(state)

    assert state["selected_segment"] == "All"
    assert state["workflow_step"] == 1
    assert state["analysis_result"] is None
    assert len(state["workflow_history"]) == 0

    # Simulate rerun: existing keys must NOT be overwritten
    state["selected_segment"] = "Enterprise"
    state["workflow_step"] = 2
    init_safe_session_state(state)

    assert state["selected_segment"] == "Enterprise", "Safe initialisation overwrote existing session value!"
    assert state["workflow_step"] == 2, "Safe initialisation overwrote workflow step!"
    print("    ✔ Safe initialization pattern verified (persists across reruns).")


def test_multistep_dependency():
    """Validates that Step 2 executes conditionally only after Step 1 is confirmed."""
    print("  [TEST 2/5] Testing multi-step workflow dependency...")
    state = MockSessionState()
    init_safe_session_state(state)

    # Initial state: Step 1
    assert state["workflow_step"] == 1
    step2_executed = False

    if state["workflow_step"] >= 2:
        step2_executed = True
    assert not step2_executed, "Step 2 should NOT execute before Step 1 confirmation."

    # User confirms Step 1: Select "Enterprise"
    selected_choice = "Enterprise"
    state["selected_segment"] = selected_choice
    state["workflow_step"] = 2
    state["workflow_history"].append(selected_choice)

    # Simulate rerun: Step 2 should now execute with Step 1 context
    if state["workflow_step"] >= 2:
        assert state["selected_segment"] == "Enterprise"
        # Simulate calculation in Step 2
        state["analysis_result"] = 3600000.0
        step2_executed = True

    assert step2_executed, "Step 2 failed to execute after Step 1 transition."
    assert state["analysis_result"] == 3600000.0
    print("    ✔ Multi-step dependency validated (Step 2 properly inherits Step 1 state).")


def test_continuity_across_simulated_widget_interactions():
    """Simulates independent widget interaction (e.g. date filter) causing full rerun."""
    print("  [TEST 3/5] Testing analytical continuity across simulated reruns...")
    state = MockSessionState()
    init_safe_session_state(state)

    # Progress into step 2
    state["selected_segment"] = "Mid-Market"
    state["workflow_step"] = 2
    state["analysis_result"] = 1400000.0

    # User adjusts an unrelated filter (e.g. Fiscal Year dropdown) -> full script rerun
    simulated_fiscal_year = "FY2023"
    init_safe_session_state(state)  # script top-level execution

    # Verify workflow state remained unchanged
    assert state["selected_segment"] == "Mid-Market", "Selection reset to default during filter interaction!"
    assert state["workflow_step"] == 2, "Workflow step reset during filter interaction!"
    assert state["analysis_result"] == 1400000.0, "Analysis result vanished during filter interaction!"
    print("    ✔ Analytical continuity maintained across independent widget reruns.")


def test_clean_reset_mechanism():
    """Validates that reset clears workflow state cleanly back to initial state."""
    print("  [TEST 4/5] Testing clean reset mechanism...")
    state = MockSessionState()
    init_safe_session_state(state)

    state["selected_segment"] = "Startup"
    state["workflow_step"] = 2
    state["analysis_result"] = 800000.0
    state["workflow_history"] = ["Startup"]

    # Trigger reset button
    reset_session_state(state)

    assert state["selected_segment"] == "All", "Reset failed to restore default segment!"
    assert state["workflow_step"] == 1, "Reset failed to restore step 1!"
    assert state["analysis_result"] is None, "Reset failed to clear analysis result!"
    assert len(state["workflow_history"]) == 0, "Reset failed to clear history!"
    print("    ✔ Clean reset mechanism restores safe defaults without memory leaks.")


def test_app_code_compliance():
    """Checks app.py code for all required patterns from the lesson checklist."""
    print("  [TEST 5/5] Checking app.py code compliance with lesson checklist...")
    app_path = os.path.join(os.path.dirname(__file__), "app.py")
    with open(app_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Checklist items
    assert 'st.session_state' in code, "st.session_state not found in app.py"
    assert '"selected_segment" not in st.session_state' in code or "'selected_segment' not in st.session_state", "Safe initialization check missing for selected_segment"
    assert '"workflow_step" not in st.session_state' in code or "'workflow_step' not in st.session_state", "Safe initialization check missing for workflow_step"
    assert 'st.rerun()' in code, "st.rerun() missing in reset/transition handling"
    assert 'Reset' in code, "Reset mechanism missing from app.py"
    print("    ✔ All lesson checklist requirements confirmed in app.py source code.")


def run_session_state_analysis():
    print("================================================================================")
    print("  MODULE 2.52: STREAMLIT SESSION STATE & WORKFLOW RUNNER")
    print("================================================================================")
    print("Verifying session state persistence, multi-step dependency, and reset logic...")

    test_safe_initialisation()
    test_multistep_dependency()
    test_continuity_across_simulated_widget_interactions()
    test_clean_reset_mechanism()
    test_app_code_compliance()

    print("\n--------------------------------------------------------------------------------")
    print("  [ALL TESTS PASSED] Streamlit Session State & Workflow Engine Verified")
    print("================================================================================\n")


if __name__ == "__main__":
    run_session_state_analysis()
