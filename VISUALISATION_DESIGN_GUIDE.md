# Engineering Guide: Business Visualisation Principles (Module 2.45)

## Executive Summary
Data dashboards fail not because underlying SQL queries are incorrect, but because visualizations miscommunicate the data relationships being explored. In executive meetings, presenting the wrong chart type—such as using a pie chart to answer growth questions or displaying a raw wall of numbers—stalls decision-making and buries critical insights.

**Module 2.45** establishes a production standard for analytical charting:
1. **Relationship-Driven Chart Selection**: Bar (comparison), Line (trend), Histogram (distribution), Scatter (correlation), Stacked Bar (composition).
2. **Complete Self-Explanatory Labelling**: The 5 essential elements (actionable title, X/Y axes with units, non-overlapping legend, human-readable ticks, data labels).
3. **Unified Palette & Dual-Encoding Accessibility**: Design system using high-contrast palettes paired with non-color encodings (markers, line styles) for color-blind inclusivity.
4. **Contextual Annotations & Reference Lines**: Transforming data displays into insight tools using `ax.annotate` and benchmark target lines (`axhline`).

```
+---------------------------------------------------------------------------------------------------+
|                                 CHART SELECTION DECISION MATRIX                                   |
+---------------------------------------------------------------------------------------------------+
   DATA RELATIONSHIP                CHART TYPE                  KEY USE CASE & CONSTRAINTS
  ─────────────────────────────────────────────────────────────────────────────────────────────
   Comparison across categories     Bar Chart (Horizontal)     Discrete items; long label readability
   Trends over continuous time      Line Chart                 Continuous time; multiple series <= 4
   Distribution of values           Histogram                  Spread, bimodal peaks, skewness
   Correlation between 2 variables  Scatter Plot + Trendline   Observations, clusters, outliers, ROI
   Part-to-whole composition        Stacked Bar                Composition + Total; max 5 segments
```

---

## 1. The Core Scenario: The Pie Chart & Table Fallacy

### The Anti-Pattern
An analyst presents quarterly revenue across 6 product lines using a pie chart. When leadership asks *"Which product grew the fastest this quarter?"*, the pie chart fails completely.
* **Why Pie Charts Fail**:
  - The human brain struggles to compare 2D angles and slice areas accurately.
  - Pie charts show static proportions of a whole, never **delta, velocity, or growth over time**.
  - Slices with small percentage differences appear visually identical.
* **Why Tables Stall Meetings**:
  - Switching to an unformatted table forces stakeholders into cognitive strain, scanning dozens of rows and columns to mentally calculate differences.

### The Solution: Direct Relationship Matching
* To compare current volumes across categories: use a **Horizontal Bar Chart** with sorted lengths and currency data labels.
* To show growth and velocity over time: use a **Multi-Line Time Series** with a target benchmark line.
* Result: Stakeholders comprehend the exact insight in **under 5 seconds** without verbal walkthroughs.

---

## 2. The Five Fundamental Chart Types

### A. Horizontal Bar Chart (Category Comparisons)
* **When to Use**: Comparing revenue, sales, or volume across discrete categories.
* **Best Practice**: Horizontal bars are preferred when category names are long (e.g. *"Cloud Enterprise Server"*), avoiding awkward tilted tick labels.
* **Implementation Standard**:
  - Always sort bars (descending or ascending) so the top performer is immediately obvious.
  - Attach explicit direct labels (`$6.45M`) to bar tips, eliminating the need to eyeball axis gridlines.

### B. Multi-Line Chart (Trends Over Time)
* **When to Use**: Showing how a metric changes along a continuous time dimension (monthly revenue, daily active users).
* **Best Practice**:
  - Connected lines imply continuity. Never use line charts for categorical dimensions.
  - Limit multi-series charts to 3–4 lines to avoid visual noise.
  - Include a horizontal target reference line (`axhline`) to anchor performance against business goals.

### C. Distribution Histogram (Spread & Skewness)
* **When to Use**: Displaying order value frequencies, customer age brackets, or latency percentiles.
* **Best Practice**:
  - Contrasting **Median** (green line) vs **Mean** (red dashed line) exposes positive or negative skewness immediately.
  - Answers *"What is typical?"* and *"Where are the extreme outliers?"* in a single glance.

### D. Scatter Plot with Trendline (Correlation)
* **When to Use**: Determining if two continuous variables share a relationship (e.g. Marketing Spend vs Generated Revenue).
* **Best Practice**:
  - Plot an Ordinary Least Squares (OLS) regression trendline with the Pearson correlation coefficient ($r = 0.95$).
  - Annotate the slope to communicate marginal ROI (e.g. *"Marginal ROI: $4.0x per $1 spend"*).

### E. Stacked Bar Chart (Part-to-Whole Composition)
* **When to Use**: Displaying how an aggregate total breaks down across discrete quarters or product lines.
* **Best Practice**:
  - **Constraint**: Maximum 5 segments per stack. Beyond 5 segments, segment heights become unreadable.
  - Label total bar height at the top so viewers observe both total scale and constituent composition.

---

## 3. Complete Labelling & Human Readability

Every production chart must incorporate these **Five Essential Labelling Elements**:

| Element | Production Requirement | Bad Example | Good Example |
| :--- | :--- | :--- | :--- |
| **1. Title** | Actionable statement answering *what* is shown | *"Bar Chart"* | *"Q4 Revenue by Product Line: Cloud Leads Growth"* |
| **2. X-Axis** | Metric or dimension name with units | *"X"* | *"Revenue (USD)"* or *"Fiscal Month (2024)"* |
| **3. Y-Axis** | Metric or dimension name with units | *"Y"* | *"Monthly Revenue (USD)"* or *"Transaction Count"* |
| **4. Legend** | Placed in dead space without overlapping data | Obscuring peak line | Top-left card with slate background |
| **5. Data Labels** | Explicit values formatted for human cognition | `5200000` | `"$5.2M"` via `FuncFormatter` |

---

## 4. Accessibility & Unified Colour Palette

### Accessibility & Color-Blind Safety
Approximately **8% of men and 0.5% of women** experience color vision deficiency (most commonly red-green daltonism).
* **Rule**: Never rely on color alone to convey distinct categories or statuses.
* **Dual-Encoding Strategy**:
  - **Color + Shape**: Enterprise series uses Blue + Circle (`o`), SMB uses Orange + Square (`s`), Startup uses Green + Triangle (`^`).
  - **Color + Line Style**: Target line uses Green + Dashed (`--`), actuals use Solid (`-`).
  - Charts remain 100% interpretable even when printed in monochrome or viewed through grayscale filters.

### Unified Design Palette (`PALETTE`)
```python
PALETTE = {
    'primary':    '#0284c7',   # Ocean Blue (Primary Series)
    'secondary':  '#f59e0b',   # Amber Orange (Comparison Series)
    'success':    '#10b981',   # Emerald Green (Targets / Healthy)
    'danger':     '#ef4444',   # Rose Red (Peaks / Alerts / Skew)
    'neutral':    '#64748b',   # Slate Grey (Grids / Borders)
    'panel_bg':   '#0f172a'    # Deep Slate (Dark Mode Surface)
}
```

---

## 5. Visual Showcase & Verification

The automated runner generates a publication-ready 6-panel visual dashboard saved at [`public/business_visualisation_principles.png`](./public/business_visualisation_principles.png).

### Running the Suite
```bash
# Standalone execution
python visualisation_principles_runner.py

# End-to-end full repository pipeline
python main.py
```

All automated verification assertions validate segment bounds, correlation bounds, skewness direction, currency formatters, and image file integrity.
