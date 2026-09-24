# Video Script: Module 2.45 - Business Visualisation Principles

**Target Duration**: 4 - 5 Minutes  
**Speaker**: Visualisation Designer / Business Intelligence Specialist  
**Visual Assets**: Terminal execution (`./venv/bin/python visualisation_principles_runner.py`), `public/business_visualisation_principles.png`, and chart comparison breakdowns.

---

## Breakdown & Timeline

### 0:00 - 0:45 | Section 1: Introduction & The Pie Chart / Table Fallacy
* **Visual**: Camera on Speaker (Webcam Fullscreen).
* **Speaker Dialogue**:
  > "Hello everyone! Welcome to Module 2.45: Business Visualisation Principles.
  > 
  > Picture this familiar boardroom crisis: an analyst presents quarterly product line performance using a 3D pie chart. Six colorful slices are displayed on the slide. The CEO looks at it and asks: 'Which product grew the fastest this quarter?'
  > 
  > The pie chart cannot answer that question. A pie chart shows static proportions of a whole—it cannot communicate growth, velocity, or trends over time. Caught off guard, the analyst switches to a raw data table with dozens of rows and numbers. Instantly, the meeting grinds to a halt as executives squint to compare figures across columns. The core insight is buried, and critical business decisions are delayed.
  > 
  > Today, we're establishing the golden rule of analytical visualization: every data relationship has a chart type built specifically for it. When you match the chart type to the data relationship and apply complete labeling, your audience grasps the insight in under five seconds."

---

### 0:45 - 2:00 | Section 2: The Five Fundamental Chart Types
* **Visual**: Transition to Screen Share showing the decision matrix in `VISUALISATION_DESIGN_GUIDE.md`.
* **Speaker Dialogue**:
  > "Let's review the five chart types that solve ninety-nine percent of business reporting needs.
  > 
  > First, Bar Charts: the undisputed champion for category comparisons. When category names are long, like 'Cloud Enterprise Server', horizontal bars provide effortless left-to-right readability without tilted axis text.
  > 
  > Second, Line Charts: designed for continuous trends over time. The connected line implies temporal continuity. You should never use a line chart for discrete categories. Multiple lines allow instant comparison between customer tiers like Enterprise and SMB.
  > 
  > Third, Histograms: essential for uncovering value distributions. Histograms answer two crucial questions: 'What is typical?' and 'How spread out is the data?' Unlike a simple average, a histogram immediately reveals outliers, bimodal clusters, and heavy skewness.
  > 
  > Fourth, Scatter Plots: the definitive tool for exploring correlations between two variables, such as marketing spend versus revenue. By adding an OLS regression trendline, we quantify the relationship and calculate marginal ROI directly.
  > 
  > And Fifth, Stacked Bar Charts: used for part-to-whole composition over time, like quarterly revenue by product. The total bar height shows the whole, while colored segments reveal the components. But beware: always limit stacks to five segments maximum so they remain readable."

---

### 2:00 - 3:00 | Section 3: The 5 Labelling Rules & Accessibility
* **Visual**: Screen Share of Code Editor displaying `visualisation_principles_runner.py` functions and formatting.
* **Speaker Dialogue**:
  > "A chart without labels is just a picture without meaning. Every production chart must include five essential elements:
  > 
  > One: An Actionable Title that describes the finding, not just the chart type.
  > Two: Explicit X and Y axis labels with clear units.
  > Three: Human-readable number formatting—displaying '$5.2M' instead of '5200000', and 'Jan 2024' instead of ISO timestamps.
  > Four: Non-overlapping legends positioned cleanly in dead space.
  > And Five: Direct data labels on bars and peak points.
  > 
  > Furthermore, professional design requires color accessibility. Roughly eight percent of men experience red-green color blindness. That's why our design system enforces dual encoding: we never rely on color alone. We pair distinct colors with unique marker shapes—circles for Enterprise, squares for SMB—and distinct dash patterns. If you print our charts in black and white, every series remains completely distinguishable."

---

### 3:00 - 4:15 | Section 4: Live Execution & Dashboard Walkthrough
* **Visual**: Screen Share of Terminal running `python visualisation_principles_runner.py`, then displaying `public/business_visualisation_principles.png`.
* **Speaker Dialogue**:
  > "Let's run our automated visualization suite: `python visualisation_principles_runner.py`.
  > 
  > [Point to Terminal Output]
  > All test data aligns cleanly across product lines, twelve-month trends, order distributions, and marketing correlations.
  > 
  > [Switch to `public/business_visualisation_principles.png`]
  > 
  > Here is our executive six-panel showcase:
  > 
  > In Panel One, our horizontal bar chart clearly ranks Cloud Server at six point four-five million dollars, with clean direct data labels.
  > In Panel Two, our multi-line chart tracks Enterprise and SMB growth. Notice the green dashed line: that's our target reference line at five million dollars, which instantly contextualizes whether performance is ahead or behind. The red annotation highlights our Q4 peak close at six point five-six million dollars.
  > In Panel Three, our histogram exposes the sharp positive skew of order sizes: the median is one hundred and eighty-four dollars, while the mean is inflated to two hundred and sixty-four dollars.
  > In Panel Four, our scatter plot demonstrates a strong positive correlation of point nine-five, with a trendline proving a four-times marginal return on marketing spend.
  > In Panel Five, our stacked bar breaks down quarterly product composition up to eleven point seven million dollars in Q4.
  > And in Panel Six, our design scorecard reinforces these standards."

---

### 4:15 - 4:45 | Section 5: Summary & Key Takeaways
* **Visual**: Transition back to Speaker (Webcam Fullscreen).
* **Speaker Dialogue**:
  > "To wrap up:
  > One: Match the chart type to the data relationship.
  > Two: Always format numbers for human readability.
  > Three: Use dual encoding so charts are accessible to everyone.
  > And Four: Use reference lines and annotations to turn raw data into actionable insights.
  > 
  > All scripts, visual assets, and engineering documentation are verified and committed. Thank you for watching!"
