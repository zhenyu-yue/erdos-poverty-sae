# 📑 Technical Methodology: Model-Based Post-Stratification

This document details the mathematical framework used to bridge individual-level microdata (ACS PUMS) and aggregate-level geographic counts (Census Tracts).

---

## 1. Estimation via Weighted Sum
We define the estimated poverty count for a specific Census Tract $j$ ($\hat{Y}_j$) as the sum of predicted probabilities across $K$ demographic buckets, weighted by the estimated population of those buckets within the tract:

$$\hat{Y}_j = \sum_{k=1}^{K} (N_{jk} \times \hat{p}_k)$$

Where:
* $N_{jk}$: The estimated population count in tract $j$ for demographic bucket $k$.
* $\hat{p}_k$: The predicted probability (or poverty ratio) for the **representative individual** of bucket $k$.

---

## 2. Training on Individuals from ACS
We use the **ACS PUMS** (Public Use Microdata Sample) to learn the conditional probability of poverty given a specific demographic profile.

### The Weighted Objective Function
Given the microdata $D = \{(x_i, y_i, w_i)\}$, where $w_i$ is the `Person_Weight` (PWGTP), we fit the model parameters $\theta$ to minimize the weighted log-loss:

$$\min_{\theta} \sum_{i} w_i \left[ y_i \log(f(x_i; \theta)) + (1-y_i) \log(1-f(x_i; \theta)) \right]$$

### The Representative Individual
For each demographic bucket $k$ (e.g., *Asian Female, Age 25-29*), we construct a **representative individual** $X_k$ using the median or midpoint values of that category. We then compute the predicted poverty ratio:
$$\hat{p}_k = f(X_k; \hat{\theta})$$

---

## 3. Raking to find Population Composition in Tracts
Since Census Tract tables do not provide joint distributions (e.g., they show total "Asian" and total "Females 25-29" separately), we must estimate the composition $N_{jk}$ using **Iterative Proportional Fitting (IPF)**.

### The "Seed" Proportions
We start with a **Seed Matrix ($S$)**, which represents the **estimated proportions** of demographic overlaps observed at the regional level in the ACS PUMS.
* **Definition:** $s_{ij}$ is the probability that a person in the region belongs to Age/Sex group $i$ AND Race group $j$.



### The Constraints
We then "rake" this regional distribution until it matches the hard constraints of the specific tract $j$:
1.  **Constraint 1:** $\sum_j w_{ij} = \text{Tract Age/Sex Count}_i$
2.  **Constraint 2:** $\sum_i w_{ij} = \text{Tract Race Count}_j$

By iteratively scaling the regional proportions to meet these local totals, we find the population composition ($N_{jk}$) that is mathematically closest to the ACS distribution while remaining consistent with tract-level reality.

---

## 4. Uncertainty: Parametric Bootstrap
To quantify the error of our model-based estimates, we use a **Parametric Bootstrap**:

1.  **Resample:** Draw $B$ bootstrap samples from the ACS PUMS data.
2.  **Retrain:** Fit $B$ versions of the model $f(X; \theta_b)$.
3.  **Sum:** For each tract, calculate $\hat{Y}_{j,b}$ using the raked counts and the $b$-th model.
4.  **Variance:** The Standard Error is the standard deviation of these $B$ estimates.

---

## 5. Summary of Process
* **Step 1:** Fit a model on **individuals from ACS** to get poverty probabilities per profile.
* **Step 2:** Use **raking** to estimate the **population composition** (how many people of each profile) in each tract.
* **Step 3:** Use the **weighted sum** of probabilities and estimated counts to produce the final tract estimate.