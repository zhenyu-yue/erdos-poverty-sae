import requests
import pandas as pd
import os
import time

# --- CONFIGURATION ---
TARGET_STATES = {
    "MD": "24",
    "DC": "11",
    "VA": "51"
}

BASE_URL = "https://api.census.gov/data/2023/acs/acs5"

# The "E" variables (Estimates) we want
# We will automatically grab the "M" (Margin of Error) for these too.
VARIABLES_E = {
    "B01003_001E": "total_population",
    "B19013_001E": "median_household_income",
    "B17001_002E": "poverty_count",       # Number of people below poverty line
    "B17001_001E": "poverty_universe",    # Total people checked for poverty
    "B22001_002E": "snap_households",     # Households receiving SNAP
    "B03002_003E": "race_white_nh",
    "B03002_004E": "race_black",
    "B03002_012E": "race_hispanic",
}

def get_storage_path():
    """Anchor logic: saves to data/raw"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    storage_path = os.path.join(script_dir, "..", "data", "raw")
    if not os.path.exists(storage_path):
        os.makedirs(storage_path)
    return storage_path

def download_state_tracts(state_abbr, state_fips):
    print(f"  Fetching data for {state_abbr} (FIPS {state_fips})...")
    
    # 1. Generate the list of variables (Estimates AND Margins of Error)
    # The Census API uses 'M' suffix for Margin of Error (e.g., B19013_001M)
    api_vars = ["NAME"] # Always get the name
    col_rename = {"NAME": "census_name"}
    
    for code, friendly_name in VARIABLES_E.items():
        # Add Estimate
        api_vars.append(code)
        col_rename[code] = friendly_name
        
        # Add Margin of Error (replace 'E' with 'M' at the end)
        # e.g. B19013_001E -> B19013_001M
        moe_code = code[:-1] + "M" 
        api_vars.append(moe_code)
        col_rename[moe_code] = f"{friendly_name}_moe"

    # 2. Construct API Call
    var_string = ",".join(api_vars)
    api_url = f"{BASE_URL}?get={var_string}&for=tract:*&in=state:{state_fips}"
    
    try:
        r = requests.get(api_url)
        r.raise_for_status()
        
        # 3. Process Data
        data = r.json()
        headers = data[0]
        rows = data[1:]
        
        df = pd.DataFrame(rows, columns=headers)
        
        # Rename columns to our friendly names
        # Note: We only rename the ones we asked for; the API adds state/county/tract at the end
        df.rename(columns=col_rename, inplace=True)
        
        df["state_abbr"] = state_abbr
        return df
        
    except Exception as e:
        print(f"  ❌ Failed {state_abbr}: {e}")
        return None

def main():
    output_dir = get_storage_path()
    all_data = []
    
    print(f"--- Downloading Tract Data + Margins of Error ---")
    
    for state_abbr, fips in TARGET_STATES.items():
        df = download_state_tracts(state_abbr, fips)
        if df is not None:
            all_data.append(df)
        time.sleep(1)

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        
        # Create GEOID
        final_df["GEOID"] = final_df["state"] + final_df["county"] + final_df["tract"]
        
        # Convert numeric columns (they come as strings)
        # We exclude non-numeric columns like 'census_name', 'state_abbr', 'GEOID'
        cols_to_convert = [c for c in final_df.columns if c not in ["census_name", "state_abbr", "GEOID", "state", "county", "tract"]]
        
        for col in cols_to_convert:
            final_df[col] = pd.to_numeric(final_df[col], errors='coerce')
            
        # Calculate Coefficient of Variation (CV) for Poverty
        # CV = (MOE / 1.645) / Estimate
        # This is the "Badness Score" (High is Bad)
        # 1.645 is the Z-score for 90% confidence (Census standard)
        if "poverty_count" in final_df.columns:
            final_df["poverty_cv"] = (final_df["poverty_count_moe"] / 1.645) / final_df["poverty_count"]
            
        output_file = os.path.join(output_dir, "acs_tract_demographics_2023.csv")
        final_df.to_csv(output_file, index=False)
        
        print(f"\n✅ Success! Saved {len(final_df)} tracts to: {output_file}")
        
        # Preview the "Badness"
        print("\n--- The Evidence (Data Preview) ---")
        print(final_df[["GEOID", "poverty_count", "poverty_count_moe", "poverty_cv"]].head())
        
        # Quick Stat
        bad_tracts = final_df[final_df['poverty_cv'] > 0.3]
        print(f"\n🔥 Number of tracts with 'Unreliable' poverty data (CV > 0.3): {len(bad_tracts)} out of {len(final_df)}")
        print(f"   (That is {len(bad_tracts)/len(final_df):.1%} of the data!)")

    else:
        print("❌ No data downloaded.")

if __name__ == "__main__":
    main()