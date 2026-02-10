# Project Roadmap: Small Area Estimation of Poverty & SNAP in the DC Metro Area

## 1. Executive Summary
**The Goal:** To produce stable, granular estimates of **Poverty Status** and **SNAP Eligibility** at the Census Tract level for the Washington D.C. Metropolitan Area.

**The Problem:** Official Census (ACS) estimates for small tracts have high Margins of Error (often >50% CV), making them unreliable for local policy. Official model-based estimates (SAIPE) only exist at the County level, masking neighborhood-level inequality.

**The Solution:** We will use **Machine Learning (XGBoost)** combined with **Post-Stratification** (Small Area Estimation) to "borrow strength" from regional PUMS data. This allows us to predict tract-level poverty with significantly lower variance than the direct survey estimates.

## 2. Geographic Scope: The DMV
We are restricting our analysis to the **Washington-Arlington-Alexandria Metro Area**.
* **District of Columbia (FIPS 11):** All Wards.
* **Maryland (FIPS 24):** Montgomery County, Prince George's County.
* **Virginia (FIPS 51):** Arlington, Alexandria, Fairfax County.

*Rationale:* This region provides a perfect test case of extreme inequality (wealthy suburbs vs. pockets of deep poverty) that simple linear regression models often fail to capture.

## 3. The Methodology (The "Pipeline")

We will implement a **Model-Based Post-Stratification** pipeline.

### Step 1: Data Acquisition
* **Training Data:** ACS Public Use Microdata Sample (PUMS) for MD, DC, VA (Person & Housing records).
* **Target Data (The Canvas):** ACS Summary Tables (Tract-level counts) for specific demographic buckets (e.g., Age $\times$ Sex $\times$ Race).
* **Validation Data:** USDA SNAP Participation counts (County level) and SAIPE Poverty estimates.

### Step 2: The Model (XGBoost)
We train a binary classifier on individual people (PUMS).
* **Inputs ($X$):** Age, Sex, Race, Education, Employment Status, Family Structure, Rent Burden.
* **Contextual Features:** County-level unemployment rate (to capture local economic environment).
* **Targets ($Y$):**
    1.  `is_poor` (Income < 100% Federal Poverty Line).
    2.  `is_snap_eligible` (Income < 130% FPL + Asset proxies).

### Step 3: Post-Stratification (The "Bucket" Strategy)
We cannot feed "Tract Averages" into the model due to aggregation bias. Instead, we use the **Synthetic Reconstruction** method:

1.  **Buckets:** Divide the population into $K$ demographic buckets (e.g., *Bucket 1: Male, 18-24, Black*).
2.  **Counts:** Get the exact count $N_{jk}$ of people in bucket $k$ for Tract $j$ from ACS Tables (B01001, B02001).
3.  **Prediction:** Use XGBoost to predict the probability of poverty $P_k$ for a person in that bucket.
4.  **Aggregation:** Calculate the expected number of poor people in the tract:
    $$\hat{Y}_j = \sum_{k=1}^{K} (P_k \times N_{jk})$$

## 4. Validation & Uncertainty Quantification
Since we are replacing official errors with model estimates, we must prove our numbers are more stable.

### The Bootstrap (Parametric)
To calculate the confidence interval of our model's predictions:
1.  **Resample:** Draw $B=100$ bootstrap samples from the original PUMS training data (with replacement).
2.  **Retrain:** Train 100 separate XGBoost models.
3.  **Repredict:** Generate 100 predictions for every Census Tract.
4.  **Variance:** Calculate the standard deviation of these 100 predictions for each tract.

**Success Criterion:** Our Bootstrap Standard Error should be **smaller** than the ACS Margin of Error for the majority of tracts.

### Calibration Check
We aggregate our tract-level predictions up to the **County Level** and compare them against the official **SAIPE** estimates.
* *Goal:* Our summed predictions should fall within the 90% Confidence Interval of the SAIPE county total.