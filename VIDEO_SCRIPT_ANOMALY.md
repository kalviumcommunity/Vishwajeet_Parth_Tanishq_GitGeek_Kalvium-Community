# Video Script: Module 2.36 - Anomaly Detection & Risk Identification

**Target Duration**: 4 - 5 Minutes  
**Speaker**: Data & Analytics Engineer / Anomaly Detection Specialist  
**Visual Assets**: Terminal execution (`./venv/bin/python anomaly_runner.py`), DuckDB database, `data/anomalies.csv`, and `public/anomaly_monitoring.png`.

---

## Breakdown & Timeline

### 0:00 - 0:45 | Section 1: Introduction & The Problem of Silent Failures
* **Visual**: Camera on Speaker (Webcam Fullscreen).
* **Speaker Dialogue**:
  > "Hello everyone! Welcome to Module 2.36: Anomaly Detection and Risk Identification.
  > 
  > In fast-moving data platforms and modern digital products, defining KPIs is only half the battle. The most critical operational challenge is knowing immediately when something goes wrong. 
  > 
  > Consider this real-world crisis: a payment processing bug causes all transactions to silently fail. The website appears completely normal. Users are browsing and adding items to carts, but every checkout fails silently. For two hours, revenue drops from twenty-five thousand dollars an hour to zero dollars. Nobody notices until frustrated customers post on social media and submit angry support tickets. By then, over fifty thousand dollars in direct revenue has vanished.
  > 
  > Or imagine a bot attack that registers ten thousand fake accounts in thirty minutes, or a pricing catalog bug that lists premium software for one dollar instead of one hundred. Without continuous automated anomaly detection, businesses operate blind. Today, we built an enterprise-grade, dual-layer monitoring engine that catches these failures within minutes."

---

### 0:45 - 1:45 | Section 2: Architecture - Static Thresholds vs Rolling Z-Scores
* **Visual**: Transition to Screen Share showing the architecture diagram in `ANOMALY_DETECTION_GUIDE.md`.
* **Speaker Dialogue**:
  > "To build a robust defense, our system implements two complementary detection layers.
  > 
  > Layer One is our Static Threshold-Based Alert Engine. We define hard operational guardrails: for example, hourly revenue should never drop below three thousand dollars, hourly transactions must stay between fifty and eight hundred, and hourly signups between five and eighty. These rules are fast, deterministic, and catch unmistakable hard outages.
  > 
  > Layer Two is our Adaptive Statistical Z-Score Engine. Business metrics exhibit strong diurnal patterns—higher activity during midday and lower at night. A static threshold might miss a subtle twenty percent drop during peak business hours. 
  > 
  > To solve this, we compute a twenty-four-hour rolling baseline: rolling mean mu and rolling standard deviation sigma. Critically, we shift this reference window by one hour. Why? Because if a massive anomaly occurs, including that anomalous point in the standard deviation calculation would inflate sigma, contaminating the baseline and hiding subsequent spikes!
  > 
  > We then compute the directional Z-score: Z equals X minus rolling mean divided by rolling standard deviation. Any point with an absolute Z-score between two and three is flagged as a Warning. Anything exceeding three sigma is classified as a Critical incident."

---

### 1:45 - 3:00 | Section 3: Live Terminal Execution & Incident Discovery
* **Visual**: Screen Share of Terminal. Run `./venv/bin/python anomaly_runner.py`.
* **Speaker Dialogue**:
  > "Let's see the engine in action. I'll execute our runner script: `python anomaly_runner.py`.
  > 
  > [Point to Terminal Output]
  > 
  > Look at Task One: our threshold validation tests pass immediately, flagging test breaches in daily revenue, signup volume, and transaction count.
  > 
  > Next, in Task Three, our engine scans 720 hours—thirty full days of live DuckDB telemetry—and uncovers three major simulated incidents:
  > 
  > First, the Silent Payment Outage on January 28th at 14:00 and 15:00. Revenue dropped to exactly zero dollars. In hour one, the Z-score collapsed to minus 4.52—well beyond our minus 3.0 critical boundary. In hour two, it recorded minus 3.22. Total estimated revenue loss: over thirty-seven thousand dollars!
  > 
  > Second, on January 15th at 3 AM, a Bot Registration Attack struck. Normal night signups are around twenty-five users. Suddenly, signups surged to two hundred and sixty users in a single hour. Our engine computed a staggering Z-score of plus 32.51!
  > 
  > Third, on January 22nd at 6 PM, our pricing glitch struck: transactions exploded four-fold to one thousand three hundred and fifty transactions, giving a Z-score of plus 18.26, while revenue crashed to just one dollar and ten cents per transaction.
  > 
  > All twenty-seven detected anomalies are automatically formatted with root cause diagnoses and exported into `data/anomalies.csv` for auditable security compliance."

---

### 3:00 - 4:15 | Section 4: Deep Dive into the Visual Telemetry Dashboard
* **Visual**: Open `public/anomaly_monitoring.png` in high-resolution viewer.
* **Speaker Dialogue**:
  > "Now let's examine the executive dashboard generated by our script at `public/anomaly_monitoring.png`.
  > 
  > [Point to Panel 1 - Top Left]
  > In the top-left panel, we monitor Hourly Revenue. The bright cyan line shows actual revenue, while the dashed line traces the 24-hour moving mean. The amber shaded corridor represents the plus-or-minus two-sigma warning zone, and the red corridor represents the three-sigma critical threshold. Look at January 28th: the red dot and callout tag immediately show the revenue dropping to zero dollars at Z equals minus 4.52.
  > 
  > [Point to Panel 2 - Top Right]
  > In the top-right panel, we track velocity metrics: signups in purple and transactions in green. You can clearly see the bot attack needle soaring to two hundred and sixty signups, and the pricing glitch needle spiking to one thousand three hundred and fifty transactions.
  > 
  > [Point to Panel 3 - Bottom Left]
  > In the bottom-left panel, we plot the statistical Z-score distribution. The white dashed curve is the theoretical standard normal bell curve. Notice our observed distribution in cyan, with the red vertical line pinpointing our payment outage far out in the critical left tail.
  > 
  > [Point to Panel 4 - Bottom Right]
  > Finally, in the bottom-right panel, we provide an executive risk governance table and automated response rules: from triggering automated circuit breakers to halting buggy checkout pipelines."

---

### 4:15 - 4:45 | Section 5: Summary & Key Takeaways
* **Visual**: Transition back to Speaker (Webcam Fullscreen).
* **Speaker Dialogue**:
  > "To recap:
  > One: Never rely solely on customer complaints or daily averages. Silent failures occur in minutes, not days.
  > Two: Pair static thresholds for hard failure limits with rolling Z-scores for dynamic, season-aware detection.
  > Three: Always use shifted baseline windows so that extreme anomalies don't contaminate your reference standard deviation.
  > And Four: Tie statistical detection directly to automated actions—circuit breakers, pager alerts, and quarantine pipelines.
  > 
  > All code, tests, and documentation are committed and verified. Thank you for watching!"
