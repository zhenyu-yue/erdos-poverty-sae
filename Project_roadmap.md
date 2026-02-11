# 📌 Project Roadmap: Small Area Estimation of Poverty (The "Strict Schema" Approach)

## 1. Executive Summary
**The Goal:** To produce granular, stable estimates of poverty at the Census Tract level for the Washington D.C. Metropolitan Area.

**The Pivot:** We originally planned to use a rich feature set (Education, Rent, Employment). However, we discovered a **"Granularity Gap"**: these features exist for *people* (PUMS) but not for *small tracts*.

**The Solution:** We will implement a **Common Schema Model**. We train our classifier *only* on the features available in the standard Census Demographic tables (Sex by Age, and Race). We sacrifice feature complexity for **geographic precision**.

## 2. Geographic Scope: The DMV
We are restricting our analysis to the **Washington-Arlington-Alexandria Metro Area**.
* **Hierarchy:**
    * **Unit of Analysis:** Person (PUMS Microdata).
    * **Unit of Prediction:** Census Tract (11-digit GEOID).
    * **Unit of Validation:** County (5-digit FIPS) & PUMA (Spatial Cluster).

## 3. The Methodology (The "Pipeline")

### Step 1: The "Common Schema" Data
We align three datasets to share a single, strict vocabulary of features.

* **Training Data (PUMS):** Individual records ($N \approx 150k$).
    * *Features:* `Age`, `Sex`, `Race`.
    * *Target:* `is_poor` (Binary).
    * *Context:* `PUMA` (for regional random effects).
* **Prediction Data (Tracts):** Aggregate counts ($N \approx 1,500$ tracts).
    * *Buckets:* 46 Age/Sex bins (Table B01001) + 7 Race bins (Table B02001).
* **Validation Data (Anchors):**
    * *Admin:* USDA SNAP Participation (The "Reality").
    * *Model:* Census SAIPE Estimates (The "Official Benchmark").

### Step 2: The Baseline Model (Classification)
We treat poverty prediction as a probability problem, strictly constrained to demographic inputs.

* **Algorithm:** Logistic Regression (Baseline) vs. Random Forest/XGBoost (Challenger).
* **The Question:** "Given *only* a person's Age, Sex, and Race, how accurately can we predict their poverty status?"
* **Metric:** ROC-AUC and F1-Score (focusing on the "Invisible Poor" residuals).

### Step 3: Post-Stratification (The "Synthetic Sum")
Since we lack a single table with *Age x Sex x Race* for tracts, we use **Marginal Reconstruction** to bridge the gap:

1.  **The Optimization Problem:** We need to know how many people in a tract fall into specific "Age $\times$ Sex $\times$ Race" buckets (e.g., *Black Male, 20-24*), but the Census only gives us separate Age/Sex totals and Race totals.
2.  **The Solution (Iterative Proportional Fitting):** We mathematically solve for the demographic distribution that is **closest to the regional average (ACS PUMS)** while strictly satisfying the specific Age/Sex and Race counts of that Census Tract.
3.  **Prediction:** We apply our trained model probabilities to these synthesized counts to generate the final poverty estimate for the tract.
    $$\hat{Y}_{Tract} = \sum_{bucket} (\hat{P}_{bucket} \times \text{Synthesized Count}_{bucket})$$

## 4. Validation Strategy (The "Three-Way Truth")
We will validate our estimates by triangulating three conflicting sources:

1.  **The Survey (ACS):** High variance, but statistically unbiased.
    * *Test:* Do our estimates fall within the ACS Margin of Error? (They should be more precise).
2.  **The Admin Data (SNAP):** Hard counts of recipients.
    * *Test:* Correlation between our `Predicted_Poor` and `SNAP_Recipients`. (Ideally $r > 0.8$).
3.  **The Official Model (SAIPE):** County-level benchmarks.
    * *Test:* When we sum our Tracts to the County level, do we match the SAIPE estimate?

## 5. Key Deliverables (Checkpoint 1)
1.  **`00_pipeline.py`:** Robust ETL that merges PUMS, Tracts, and County data. (✅ Done)
2.  **`data_inventory.md`:** Strict definition of the "Common Schema." (✅ Done)
3.  **`02_baseline_model.ipynb`:** Proof that demographics contain a predictable signal. (Next Step)
