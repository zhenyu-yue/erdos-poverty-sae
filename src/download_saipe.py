import requests
import pandas as pd
import os
import time

# --- CONFIGURATION ---
# State FIPS codes: DC=11, MD=24, VA=51
TARGET_STATES = ["11", "24", "51"]
YEAR = "2023"  # Most recent final release usually
BASE_URL = "https://api.census.gov/data/timeseries/poverty/saipe"

# Variables we want:
# SAIHE = All ages in poverty (Count)
# SAIPE = All ages in poverty (Rate) - Note: Variable names vary slightly by year/dataset, 
# but usually: 'B01001_001E' equivalent. 
# actually SAIPE API uses different codes.
# B01001_001E is ACS. SAIPE uses:
# SAEPOVALL_PT: All ages in poverty count
# SAEPOVALL_MOE: Margin of Error
# SAEPOVRTALL_PT: All ages poverty rate
# SAEPOVRTALL_MOE: Rate Margin of Error
# NAME: County Name

VARIABLES = [
    "NAME",
    "SAEPOVALL_PT",    # Count: All ages in poverty
    "SAEPOVALL_MOE",   # MOE: Count
    "SAEPOVRTALL_PT",  # Rate: All ages poverty rate
    "SAEPOVRTALL_MOE"  # MOE: Rate
]

def get_storage_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    storage_path = os.path.join(script_dir, "..", "data", "raw")
    if not os.path.exists(storage_path):
        os.makedirs(storage_path)
    return storage_path

def download_saipe_state(state_fips):
    print(f"Fetching SAIPE {YEAR} for state {state_fips}...")
    
    # API Format: ?get=VAR1,VAR2&for=county:*&in=state:XX&time=YYYY
    var_str = ",".join(VARIABLES)
    url = f"{BASE_URL}?get={var_str}&for=county:*&in=state:{state_fips}&time={YEAR}"
    
    try:
        r = requests.get(url)
        r.raise_for_status()
        
        data = r.json()
        headers = data[0]
        rows = data[1:]
        
        df = pd.DataFrame(rows, columns=headers)
        return df
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return None

def main():
    output_dir = get_storage_path()
    all_dfs = []
    
    print(f"--- Downloading SAIPE {YEAR} Data ---")
    
    for fips in TARGET_STATES:
        df = download_saipe_state(fips)
        if df is not None:
            all_dfs.append(df)
        time.sleep(1)
        
    if all_dfs:
        final_df = pd.concat(all_dfs, ignore_index=True)
        
        # Rename cryptic columns to readable ones
        rename_map = {
            "SAEPOVALL_PT": "saipe_poverty_count",
            "SAEPOVALL_MOE": "saipe_poverty_count_moe",
            "SAEPOVRTALL_PT": "saipe_poverty_rate",
            "SAEPOVRTALL_MOE": "saipe_poverty_rate_moe",
            "state": "state_fips",
            "county": "county_fips"
        }
        final_df.rename(columns=rename_map, inplace=True)
        
        # Create a GEOID for merging later (State + County)
        final_df["GEOID"] = final_df["state_fips"] + final_df["county_fips"]
        
        # Save
        output_file = os.path.join(output_dir, f"saipe_counties_{YEAR}.csv")
        final_df.to_csv(output_file, index=False)
        print(f"\n✅ Success! Saved SAIPE data to: {output_file}")
        print(final_df[["NAME", "saipe_poverty_count", "saipe_poverty_rate"]].head())
    else:
        print("❌ No data found.")

if __name__ == "__main__":
    main()