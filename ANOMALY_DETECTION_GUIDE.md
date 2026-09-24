# Engineering Guide: Anomaly Detection & Risk Identification (Module 2.36)

## Executive Summary
Modern digital businesses process thousands of transactions, user registrations, and events every hour. When critical infrastructure breaks or malicious actors exploit a system, catastrophic losses can mount silently before customers complain or teams manually notice.

**Module 2.36** establishes an enterprise-grade, dual-layer anomaly detection framework:
1. **Threshold-Based Alert Engine**: Fast, static operational boundary checks (`min`/`max` bounds) for definitive SLAs and hard failure thresholds.
2. **Statistical Z-Score & Rolling Monitoring**: Adaptive, dynamic confidence bands ($\pm 2\sigma$ Warning, $\pm 3\sigma$ Critical) calculated over 24-hour moving baselines to account for diurnal seasonality while preventing baseline contamination.

```
+---------------------------------------------------------------------------------------------------+
|                                  KPI Stream (Hourly Metrics)                                      |
+---------------------------------------------------------------------------------------------------+
                               |                                        |
                               v                                        v
               [Layer 1: Static Thresholds]            [Layer 2: Rolling Z-Score Engine]
               • Daily/Hourly Hard Min & Max           • Shifted 24h Baseline (μ, σ)
               • Immediate Boundary Violation          • Z = (X - μ_rolling) / σ_rolling
                               \                                        /
                                v                                      v
                        +------------------------------------------------------+
                        |               Incident Severity Classifier           |
                        | • Normal:   |Z| < 2.0  (Within 95% Distribution)     |
                        | • Warning:  2.0 <= |Z| < 3.0  (Investigate SLA)      |
                        | • Critical: |Z| >= 3.0 or Hard Breach (Immediate P0) |
                        +------------------------------------------------------+
                                                   |
                                                   v
                        +------------------------------------------------------+
                        |         Automated Incident Log & Mitigation          |
                        | • data/anomalies.csv (Auditable Incident Records)    |
                        | • Circuit Breakers, Gateway Failover, Bot IP Quota   |
                        | • Visual Telemetry Dashboard (anomaly_monitoring.png)|
                        +------------------------------------------------------+
```

---

## 1. The Real-World Failure Scenarios

### Scenario A: Payment Processing Outage (Silent Transaction Failure)
* **The Problem**: A third-party payment gateway misconfiguration causes 100% of transactions to fail silently. User signups and site browsing continue normally, but hourly revenue crashes from **~$25,000/hr to $0.00** for 2 consecutive hours.
* **The Danger**: Without continuous automated monitoring, companies only discover the failure hours later when customers send support complaints, resulting in **$50,000+ unrecoverable lost revenue**.
* **Detection**:
  - Layer 1: Hourly revenue breaches the hard minimum threshold ($0 < \$3,000$).
  - Layer 2: Hour 1 triggers $Z = -4.52$ ($p < 0.0001$), instantly generating a Critical P0 incident within minutes of downtime.

### Scenario B: Bot Account Creation Attack (Sybil Surge)
* **The Problem**: An automated credential-stuffing or promo-farming bot script registers accounts at **260 signups/hr** at 3:00 AM (baseline normal: ~25 signups/hr).
* **The Danger**: Product teams mistakenly celebrate artificial user growth, while infrastructure costs balloon, referral pools are drained, and security integrity is compromised.
* **Detection**:
  - Layer 1: Breaches maximum hourly signup threshold ($260 > 80$).
  - Layer 2: Statistical anomaly yields $Z = +32.51$, an extreme $>30\sigma$ outlier triggering immediate botnet quarantine.

### Scenario C: Catalog Pricing Glitch (Exploit Surge)
* **The Problem**: A database synchronization error lists premium catalog items for **$1.10** instead of standard retail pricing (~$75). Transaction volume explodes to **1,350 tx/hr** (4x normal peak of ~320 tx/hr).
* **The Danger**: Arbitrage bots and viral social media posts rapidly exhaust warehouse inventory at massive financial loss.
* **Detection**:
  - Layer 1: Transaction count breaches hard ceiling ($1,350 > 800$ tx).
  - Layer 2: Transaction Z-Score surges to $Z = +18.26$, accompanied by severe revenue collapse ($Z = -4.46$). Automated circuit breakers immediately halt the checkout pipeline.

---

## 2. Mathematical Foundation of Statistical Monitoring

### A. 24-Hour Rolling Historical Baseline
To prevent the anomaly itself from distorting the reference distribution, the baseline uses a **1-hour shifted historical window**:

$$\mu_t = \frac{1}{W} \sum_{i=1}^{W} X_{t-i}$$

$$\sigma_t = \sqrt{\frac{1}{W - 1} \sum_{i=1}^{W} (X_{t-i} - \mu_t)^2}$$

Where $W = 24$ hours. Shifting the window ensures that an extreme spike (e.g. 260 signups or 1,350 transactions) does not inflate $\sigma_t$ and mask subsequent anomalies.

### B. Standardized Z-Score Formulation
The incoming observation $X_t$ is normalized against the rolling baseline:

$$Z_t = \frac{X_t - \mu_t}{\sigma_t}$$

* **Directional Interpretation**:
  - $Z_t > 0$: Metric is above expectation (surges, promotional spikes, bot attacks).
  - $Z_t < 0$: Metric is below expectation (outages, database errors, funnel leaks).

### C. Severity Tiering & Confidence Intervals

| Tier | Statistical Boundary | Theoretical Probability | Operational Action |
| :--- | :--- | :--- | :--- |
| **Normal** | $|Z| < 2.0$ | $95.45\%$ of baseline | Healthy telemetry. Routine dashboard logging. |
| **Warning** | $2.0 \le |Z| < 3.0$ | $4.28\%$ of baseline | Slack alert to on-call engineer; automated diagnostic health check. |
| **Critical** | $|Z| \ge 3.0$ | $< 0.27\%$ ($> 3\sigma$) | P0 PagerDuty alert; automated circuit breaker / gateway fallback. |

---

## 3. Threshold-Based Rule Architecture

Static thresholds define non-negotiable operational boundaries independent of recent volatility:

```python
STATIC_THRESHOLDS = {
    'daily_revenue':    {'min': 5000.0, 'max': 500000.0, 'unit': '$'},
    'hourly_revenue':   {'min': 3000.0, 'max': 45000.0,  'unit': '$'},
    'transaction_count':{'min': 50,     'max': 800,      'unit': 'tx'},
    'signup_count':     {'min': 5,      'max': 80,       'unit': 'users'},
    'active_users':     {'min': 200,    'max': 3500,     'unit': 'users'}
}
```

* **Minimum Revenue Bound ($3,000/hr)**: Ensures that any silent payment gateway blackout is flagged even if rolling standard deviation is wide.
* **Maximum Signup Bound (80 users/hr)**: Catches automated account farming without requiring model recalculation.
* **Maximum Transaction Bound (800 tx/hr)**: Prevents uncontrolled coupon loops and catalog pricing bugs.

---

## 4. Empirical Results & Detected Incidents

The framework was evaluated across **720 hourly records (30 consecutive days)** seeded in DuckDB (`hourly_kpi_metrics`):

| Timestamp | Metric | Observed Value | Expected Mean ($\mu$) | Z-Score ($Z$) | Severity | Diagnosed Root Cause | Financial Impact |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **2024-01-15 03:00** | `signup_count` | 260 users | 25.3 users | **+32.51** | **CRITICAL** | Bot Attack: 10x registration burst | IP Farm Quarantined |
| **2024-01-22 18:00** | `transaction_count` | 1,350 tx | 280.2 tx | **+18.26** | **CRITICAL** | Pricing Glitch: 4x tx surge, $1.10 unit rev | -$98,400 exploit risk |
| **2024-01-22 18:00** | `revenue` | $1,485.00 | $19,450.00 | **-4.46** | **CRITICAL** | Pricing Glitch: Severe revenue collapse | Circuit breaker tripped |
| **2024-01-28 14:00** | `revenue` | $0.00 | $19,161.21 | **-4.52** | **CRITICAL** | Payment Gateway Outage (Hour 1) | -$24,850 revenue loss |
| **2024-01-28 15:00** | `revenue` | $0.00 | $18,146.87 | **-3.22** | **CRITICAL** | Payment Gateway Outage (Hour 2) | -$25,120 revenue loss |

* Total Flagged Incidents Exported to `data/anomalies.csv`: **27 events** (21 warning events representing diurnal viral spikes/dips, and 6 critical events representing real operational crises).
* Total Revenue Saved by Early Outage Detection: **$37,308+ to $50,000+**.

---

## 5. Visual Telemetry Dashboard

The automated runner generates a publication-ready 4-panel visual dashboard saved at `public/anomaly_monitoring.png`:

1. **Panel 1: Hourly Revenue Monitoring & Silent Outage Detection**:
   - Plots actual revenue against the 24-hour moving mean $\mu$.
   - Amber and red confidence corridors highlight $\pm 2\sigma$ and $\pm 3\sigma$ bounds.
   - Outage markers with red callout annotations identify the $0.00 failure at $Z = -4.52$.
2. **Panel 2: Velocity Monitoring (Signups & Transactions)**:
   - Dual-axis time series tracking hourly signups vs transactions.
   - Bot attack spike at 260 signups ($Z = 32.5$) and pricing glitch at 1,350 tx ($Z = 18.3$) clearly annotated.
3. **Panel 3: Statistical Z-Score Distribution & Risk Boundaries**:
   - Overlay of empirical Z-score histogram against the theoretical standard normal curve $\mathcal{N}(0, 1)$.
   - Shaded $\pm 2\sigma$ and $\pm 3\sigma$ risk tails clearly demarcate safe vs dangerous operating regimes.
4. **Panel 4: Executive Incident Summary & Risk Governance Table**:
   - High-contrast table listing critical incidents, detected metrics, Z-scores, and estimated financial impact.
   - Actionable bullet points outlining automated circuit breakers and failover SLAs.

---

## 6. How to Run & Verify

Run the anomaly detection suite standalone:
```bash
./venv/bin/python anomaly_runner.py
```

Or execute the complete end-to-end repository pipeline:
```bash
./venv/bin/python main.py
```

All 6 automated assertions verify threshold triggers, critical Z-score detections, audit CSV generation, and image validity.
