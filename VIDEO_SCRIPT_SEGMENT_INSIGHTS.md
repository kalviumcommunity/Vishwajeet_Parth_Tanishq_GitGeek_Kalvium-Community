# Video Presentation Script: GroupBy Aggregation & Segment Insights
## Module 2.30: Multi-Dimensional Grouping, Pivot Tables & Customer Segmentation

> **Submission Video Checklist**:
> - **Webcam**: Ensure your face is **clearly visible** throughout the recording.
> - **Screen Share**: Display `SEGMENT_AGGREGATION_GUIDE.md`, `segment_aggregation_runner.py`, terminal output, and `public/segment_insights.png`.
> - **Google Drive**: Sharing permission must be set to **"Anyone with the link can view"**.
> - **Incognito Check**: Test the Drive link in an Incognito / Private window before submitting.
> - **Target Duration**: **3 to 5 minutes**.

---

## 🎬 Word-for-Word Speaking Script

### 1. Introduction & The Core Business Problem
**[On Screen: Display `SEGMENT_AGGREGATION_GUIDE.md` or executive summary]**

> *"Hello everyone! My name is [Your Name], and today I am presenting Module 2.30: GroupBy Aggregation and Segment Insights.*
>
> *In business analytics, a flat dataset of transactions or customer records tells you very little until you group and aggregate it. Often, companies make the mistake of reporting dataset-wide averages.*
>
> *For example, consider our customer churn dataset. If leadership looks only at the aggregate, they see a blended churn rate of **9.25%**. They might say, 'Our churn is around 9%, let's run a generic retention campaign across all customers.'*
>
> *This is what we call the **Homogeneity Fallacy**—assuming that every customer behaves like the average.*
>
> *In reality, when we slice the data by customer segment, the picture completely transforms:*
> - ***Enterprise customers (5% of the base)** have just **1% churn** and generate **70% of total revenue**.*
> - ***SMB customers (40% of the base)** suffer from a massive **12% churn rate**.*
> - ***Startups (55% of the base)** have an **8% churn rate**.*
>
> *The average masked the fact that our most valuable accounts are thriving, while our self-serve SMB tier is hemorrhaging customers. In this module, we implement multi-dimensional GroupBy analysis to turn flat data into actionable strategy."*

---

### 2. GroupBy Mechanics: The Split-Apply-Combine Pattern
**[On Screen: Highlight Task 2 in `segment_aggregation_runner.py`]**

> *"To extract these insights, we rely on the foundational **Split-Apply-Combine** pattern in Pandas:*
> 1. ***Split***: *We partition the dataset into distinct groups by key columns like `customer_type` and `product`.*
> 2. ***Apply***: *We perform aggregations within each subgroup.*
> 3. ***Combine***: *We stitch the individual outputs back into a clean analytical summary.*
>
> *We implemented the three core Pandas GroupBy methods:*
> - *First, **`.agg()`**: Used to collapse groups into single summary rows. We computed the sum of churned accounts, total counts, and mean churn rates per segment.*
> - *Second, **`.transform()`**: Used when we want to broadcast a group-level statistic back to every single row without losing individual customer records. For instance, we created `df['churn_rate_by_type']`, which attaches the segment-level churn benchmark directly to each customer row for deviation analysis.*
> - *Third, **`.apply()`**: Used for custom group-level logic, such as extracting and summing the top three spending customers within each segment using a lambda function."*

---

### 3. Multi-Dimensional Aggregation: Unstack vs. Pivot Tables
**[On Screen: Point to Task 3 and Task 4 in `segment_aggregation_runner.py`]**

> *"Next, business performance is rarely single-dimensional. In Task 3 and Task 4, we aggregated revenue across **two dimensions simultaneously**: customer type and product line.*
>
> *We demonstrated two complementary approaches:*
> - *Using `df.groupby(['customer_type', 'product'])['revenue'].sum().unstack()` to pivot the multi-index.*
> - *Using `pd.pivot_table()`, which provides a clean two-dimensional matrix of revenue and churn rates across our product catalog.*
>
> *This reveals not only which customer segment is churning, but specifically **which products** are experiencing elevated churn within each segment."*

---

### 4. Segment Ranking & Actionable Business Insights
**[On Screen: Show `public/segment_insights.png`, walking through Panels 1 to 4]**

> *"Let's examine our generated visual dashboard in `public/segment_insights.png`:*
>
> *In **Panel 1**, you can see the drastic difference in churn rates. Enterprise is down at 1.0% in green, Startup is at 8.0% in amber, and SMB is at 12.0% in red, compared to the dashed baseline.*
>
> *In **Panel 2**, we illustrate the **Pareto inequality**: Enterprise represents just 5% of the customer count, yet commands 70% of total company revenue.*
>
> *In **Panels 3 and 4**, our two-dimensional heatmaps expose product revenue distribution and vulnerability hotspots, highlighting that SMB customers on Developer Tools and Security Suite have churn rates exceeding 13% to 14%.*
>
> *Based on these findings, we formulated three distinct, evidence-based strategic interventions:*
> 1. ***For Enterprise***: *Status is healthy and highly profitable. Strategy: Dedicate white-glove executive business reviews and expansion incentives to protect the 70% revenue engine.*
> 2. ***For SMB***: *Status is high churn risk. Strategy: Deploy automated onboarding health checks, streamline self-serve setup, and trigger early warning alerts before accounts cancel.*
> 3. ***For Startups***: *Status is moderate churn with high volume. Strategy: Provide developer tutorials, community office hours, and milestone adoption nudges."*

---

### 5. Live Pipeline Execution & Conclusion
**[On Screen: Run `./venv/bin/python segment_aggregation_runner.py` in Terminal]**

> *"Let's execute the runner in terminal:*
> ```bash
> python segment_aggregation_runner.py
> ```
> *The runner executes the complete pipeline, logs the scorecards, generates the 4-panel visual chart, and runs our automated validation assertions:*
> - *Validates 2,000 customer records.*
> - *Confirms Enterprise 1.0% churn and 70% revenue share.*
> - *Confirms SMB 12.0% churn and Startup 8.0% churn.*
> - *Verifies broadcast transform shape and pivot table mathematical equivalence.*
>
> *All assertions pass!*
>
> *By replacing dataset-wide averages with multi-dimensional segment aggregation, we transform raw transaction logs into prioritized, high-impact business strategy. Thank you!"*
