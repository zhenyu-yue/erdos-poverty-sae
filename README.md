# Erdos Project: Small Area Estimation for Poverty & SNAP

This project uses Machine Learning (XGBoost/Mixed Effects) to estimate poverty and SNAP participation rates at the county level using ACS PUMS data.

## 📂 Project Structure

    erdos-poverty-sae/
    ├── data/                  <-- Data files (Ignored by Git)
    │   └── raw/               <-- Raw CSVs from Census & USDA
    ├── notebooks/             <-- Jupyter Notebooks for analysis
    ├── src/                   <-- Python scripts for automation
    ├── requirements.txt       <-- Python dependencies
    └── setup_env.sh           <-- One-click setup script

## 🚀 Quick Start Guide
### 1. Clone the Repo
```bash
git clone https://github.com/zhenyu-yue/erdos-poverty-sae.git
cd erdos-poverty-sae
```
(Alternatively, click [here](https://github.com/zhenyu-yue/erdos-poverty-sae.git) to visit the git repo, select "code" then "Download ZIP" and unzip the file.)


### 2. Set Up Environment
Don't forget to change your working directory to the project directory before proceeding.

**Option A: Automatic (Recommended)**
Run the setup script to create a clean environment:
```bash
bash setup_env.sh
conda activate poverty-project
```

**Option B: Manual (Fast)** If you prefer to use your current Python environment, just install the requirements directly:

```bash
pip install -r requirements.txt
```

### 3. Download the Data

#### A. ACS Census Data (PUMS) 
Run this script to automatically download the 2024 ACS PUMS data (Person & Housing records) into data/raw/:

```bash
python src/download_acs.py
```

#### B. USDA SNAP Data
1. Download the "Bi-Annual (January and July) State Project Area/County Level Participation and Issuance Data" zip file from the [USDA Website](https://www.fns.usda.gov/pd/supplemental-nutrition-assistance-program-snap). Move the zip file to `data/raw/`.

2. Run 
```bash
python src/process_snap.py
```

### 4. Run the Notebook
Try to run the following notebook with VScode or with Jupyter. 

```bash
jupyter notebook notebooks/01_data_exploration.ipynb
```
