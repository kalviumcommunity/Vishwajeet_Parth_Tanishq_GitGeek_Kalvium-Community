# Video Presentation Script: Data Storytelling & Insight Narrative (Module 2.48)

**Target Duration:** 4 - 5 Minutes  
**Speaker:** Senior Analytics Engineer & Strategic Advisor  
**Visual Aid:** `public/data_storytelling_dashboard.png` & Interactive Streamlit App  

---

### [0:00 - 0:45] Act I: Introduction & The Five-Part Narrative Arc
*(Slide / Screen: Full view of the Data Storytelling Executive Briefing Dashboard)*

> "Hello everyone. Today, we are discussing the single most critical transition an analyst can make: moving from delivering data to delivering decisions. 
> 
> Too many brilliant analyses die quietly in slide decks because they overwhelm stakeholders with raw numbers, p-values, and correlation coefficients without connecting them to what the business actually cares about: revenue, retention, and strategic execution.
> 
> To solve this, we implement the **Five-Part Narrative Arc**:
> 1. **Context** — Framing what is at stake.
> 2. **Data** — Establishing analytical scope and confidence.
> 3. **Finding** — Delivering the core discovery without ambiguity.
> 4. **Why** — Unpacking the underlying causal mechanism.
> 5. **Action** — Proposing a concrete, 5-element recommendation."

---

### [0:45 - 1:45] Act II: Context & Data Grounding
*(Slide / Screen: Zoom into Panel 3 - Framework and Context)*

> "Let's apply this framework directly to our churn problem.
> 
> First, **Context**: Our business is currently experiencing **$2,000,000 in lost annual recurring revenue (ARR)** due to customer churn. In an era where customer acquisition costs are rising, preserving our existing customer base is our highest-leverage growth driver.
> 
> Second, **Data Scope**: We didn't look at a handful of customer anecdotes. We analyzed **50,000 customer accounts over a 24-month horizon**. We categorized their initial support ticket experiences into four response latency tiers: under 2 hours, 2 to 4 hours, 4 to 24 hours, and over 24 hours. Our regression models reveal an **R-squared of 0.40** — meaning support response latency alone explains 40% of the variance in customer churn."

---

### [1:45 - 2:45] Act III: The Finding & The Root Cause (Why)
*(Slide / Screen: Zoom into Panel 1 - Churn Rate vs Support Response Cohort)*

> "Now, look at Panel 1 for our **Finding**:
> 
> For customers answered in under 2 hours, annual churn is just **3.0%**. But when response times exceed 24 hours, churn surges to **12.2%**. That is a **4.0x escalation in churn risk**.
> 
> But why does this happen? That brings us to Stage 4: **Why**. 
> When a customer encounters technical friction and receives an answer within 2 hours, their momentum is unbroken and their faith in the product's reliability is reaffirmed. But when tickets sit unattended for more than 24 hours, psychological abandonment occurs. The customer feels neglected, active workflows stall, and they begin evaluating competitor solutions before our support team even sends their initial reply."

---

### [2:45 - 3:45] Act IV: Translating Technical Jargon & The Financial ROI Bridge
*(Slide / Screen: Zoom into Panel 2 - Financial ROI Bridge Waterfall)*

> "Notice how we communicate this. Instead of telling the executive board: *'We observed a statistically significant correlation with a p-value of 0.001 and heteroscedastic residual distributions'*, we say: *'There is an undeniable, reliable relationship where support delays directly drive customer cancellations.'*
> 
> This brings us to Panel 2: **The Financial ROI Bridge**.
> Currently, churn bleeds $2.0M annually. By implementing a strict under-2-hour first-response SLA, we project recovering **$560,000 in gross ARR** annually by cutting churn back down to baseline levels.
> Achieving this requires hiring **2 dedicated Tier-1 Support Engineers** at a total loaded cost of **$160,000**.
> 
> Subtracting the investment from the recovered ARR yields a **net annual financial benefit of +$400,000**, delivering a 250% annual return on investment."

---

### [3:45 - 4:45] Act V: The 5-Element Actionable Recommendation & Close
*(Slide / Screen: Zoom into Panel 4 - Executive Proposal 5-Element Action Plan)*

> "Finally, Stage 5: **Action**. An analysis is only complete when it provides an airtight proposal. We utilize the 5-Element Action Framework:
> 
> 1. **WHAT:** Hire 2 dedicated Tier-1 Support Engineers to enforce a <2 hour SLA during peak global business hours.
> 2. **WHY:** Eliminates the >24 hour response backlog responsible for the 4x churn spike.
> 3. **IMPACT:** Net positive annual cash flow of **+$400,000**.
> 4. **OWNER:** VP of Customer Operations for hiring, and Head of Support for operational execution.
> 5. **TIMELINE:** Post job descriptions by Dec 1; Onboard engineers by Jan 31; SLA operational by Jan 1.
> 
> By following this narrative arc, we didn't just present charts. We proved a problem, explained its cause, quantified its economic impact, and gave leadership an immediate, justifiable decision.
> 
> Thank you."
