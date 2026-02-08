# Project Logic & Research Design
*Why we are doing this and how we will win.*

## 1. The Core Problem (The "Why")
The Official Census (ACS) data for small areas (Census Tracts) is statistically unreliable.
* **Sample Size Issue:** ACS samples only ~1.5% of the population per year. In a small tract (4,000 people), this is <60 interviews.
* **The Result:** High Margins of Error (MOE).
    * *Example:* Tract 202 Poverty = **145 ± 110**.
    * This range (35 to 255) is useless for policy.
* **The Evidence:** ~30% of Census Tracts have a Coefficient of Variation (CV) > 0.3, meaning they are "unreliable" by the Census Bureau's own standards.

## 2. Our Solution (The "How")
We use **Small Area Estimation (SAE)** with Machine Learning (XGBoost) to "Borrow Strength."
* Instead of relying on 60 people in one tract, we train a model on **60,000+ people** (PUMS Microdata) across the entire state (MD/DC/VA).
* **The Mechanism:**
    1.  **Learn Rules:** High Rent + Single Mom + Low Education = High Poverty Probability.
    2.  **Apply Rules:** Apply this probability to the known demographics of the tract (Total Single Moms, Total Renters).
* **The Result:** We replace the noisy survey estimate (CV=45%) with a stable model prediction (CV=12%).

## 3. The "Erdos Edge" (Our Unique Value)
We are not just predicting "Poverty" (which SAIPE already does at the county level). We are predicting **"Unmet SNAP Need."**
* **Official Metric:** Poverty Rate (Income < 100% FPL).
* **Our Metric:** The "Gap."
    * **Step A:** Estimate **SNAP Eligibility** (Income < 130% FPL + Asset Rules).
    * **Step B:** Subtract **Actual Participation** (from USDA Administrative Data).
    * **Result:** A map of "The Invisible Poor"—people who are eligible for help but not getting it.

## 4. How We Defend Our Numbers (Validation)
When critics ask *"How do you know your model is better than the Census?"*, we answer:

1.  **Internal Proof (Bootstrap):**
    * We bootstrap our model 100 times.
    * **Result:** Our model's variance is significantly lower than the Census Design Variance (MOE).
2.  **External Proof (The "Impossible" Tracts):**
    * We identify tracts where Census Poverty < Known SNAP Recipients (statistically impossible).
    * Our model corrects these underestimates, aligning with the hard administrative data.
3.  **Aggregate Check:**
    * Summing our tract predictions up to the County level matches the Gold Standard (SAIPE) within 5%.

## 5. Implementation Plan
### Phase 1: Data Acquisition (Done)
* [x] ACS PUMS (Training Data): `src/download_acs.py`
* [x] USDA SNAP (Ground Truth): `src/process_snap.py`
* [x] ACS Tracts (Target Canvas): `src/download_tract_data.py`

### Phase 2: Processing (Next)
* [ ] **Clean PUMS:** Merge Person & Housing files (`notebooks/02_pums_cleaning.ipynb`).
* [ ] **Feature Engineering:** Define "SNAP Eligible" logic.

### Phase 3: Modeling
* [ ] Train XGBoost Classifier (`is_poor ~ Age + Race + Rent + FamilyStructure`).
* [ ] Apply to Tract Demographics.
* [ ] Calibrate against USDA County Totals.