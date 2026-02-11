# Small Area Estimation of Poverty in the DMV
*A model-based approach to improving the precision of neighborhood-level economic indicators.*

## Objective
The American Community Survey (ACS) provides critical socioeconomic data, but at the Census Tract level, estimates often suffer from high Margins of Error (MOEs) due to small sample sizes. This project implements a Model-Based Post-Stratification pipeline to "borrow strength" from regional microdata (PUMS), producing stable, granular poverty estimates for the Washington-Arlington-Alexandria Metropolitan Area.

## Key Performance Indicators (KPIs)

| Metric | Result | Definition |
| :--- | :--- | :--- |
| **CV Reduction** | | Percent improvement in the Coefficient of Variation compared to official ACS estimates. |
| **Weighted F1-Score** | | Model performance on the poverty class using the ACS PUMS test set. |
| **SNAP Correlation** | | Pearson correlation ($r$) between model estimates and administrative SNAP participation records. |
| **SAIPE Benchmarking** | | Mean Absolute Percent Error (MAPE) when aggregating tract estimates to the County level. |

## Methodology
The pipeline utilizes a "Big Version" spatial estimation strategy to transform individual-level behavior into aggregate-level geography:

1.  **Training on Individuals from ACS:** An XGBoost classifier is trained on individual-level ACS PUMS data to learn the conditional probability of poverty given Age, Sex, and Race. The model is optimized using a weighted log-loss function to account for the PUMS survey design.
2.  **Raking to Find Population Composition:** Since Census Tract tables do not provide joint distributions (e.g., they show total "Race" and total "Age/Sex" separately), we use **Iterative Proportional Fitting (IPF)** to estimate the joint distribution. This process "rakes" regional demographic proportions from PUMS until they satisfy local tract-level marginal constraints.
3.  **Estimation and Weighted Sum:** We construct **representative individuals** for each of the 322 demographic buckets (Age x Sex x Race) and calculate their predicted poverty probabilities. The final tract estimate is the weighted sum of these probabilities multiplied by the synthesized population counts.



---
For technical details on the Raking algorithm and variance estimation, see [METHODOLOGY.md](./METHODOLOGY.md).  
To set up the environment and run the pipeline, see [STARTERS_GUIDE.md](./STARTERS_GUIDE.md).