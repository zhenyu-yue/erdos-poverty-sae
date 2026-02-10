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

# --- DEFINING THE BUCKETS (STRATA) ---
# We need counts for Sex x Age to build our "Representative People".
# Table B01001: Sex by Age
# To save space, I'll generate these codes programmatically.

VARIABLES_E = {
    "NAME": "census_name",
    # Validation Targets
    "B17001_002E": "poverty_count",
    "B22001_002E": "snap_households",
    # Overall Context
    "B01003_001E": "total_population",
    "B19013_001E": "median_household_income",
}

# Add Race Totals (Table B02001)
VARIABLES_E["B02001_002E"] = "race_white"
VARIABLES_E["B02001_003E"] = "race_black"
VARIABLES_E["B02001_005E"] = "race_asian"
VARIABLES_E["B03002_012E"] = "race_hispanic"

# Add Age x Sex Buckets (Table B01001)
# Males: 003E to 025E | Females: 027E to 049E
# We map them to generic names like "male_under_5", "male_5_to_9", etc.
# Note: This is a simplified mapping for readability.
AGE_SEX_MAP = {
    # MALES
    "B01001_003E": "m_00_04", "B01001_004E": "m_05_09", "B01001_005E": "m_10_14",
    "B01001_006E": "m_15_17", "B01001_007E": "m_18_19", "B01001_008E": "m_20",
    "B01001_009E": "m_21",    "B01001_010E": "m_22_24", "B01001_011E": "m_25_29",
    "B01001_012E": "m_30_34", "B01001_013E": "m_35_39", "B01001_014E": "m_40_44",
    "B01001_015E": "m_45_49", "B01001_016E": "m_50_54", "B01001_017E": "m_55_59",
    "B01001_018E": "m_60_61", "B01001_019E": "m_62_64", "B01001_020E": "m_65_66",
    "B01001_021E": "m_67_69", "B01001_022E": "m_70_74", "B01001_023E": "m_75_79",
    "B01001_024E": "m_80_84", "B01001_025E": "m_85_plus",
    
    # FEMALES (Similar structure, jumping to 027E)
    "B01001_027E": "f_00_04", "B01001_028E": "f_05_09", "B01001_029E": "f_10_14",
    "B01001_030E": "f_15_17", "B01001_031E": "f_18_19", "B01001_032E": "f_20",
    "B01001_033E": "f_21",    "B01001_034E": "f_22_24", "B01001_035E": "f_25_29",
    "B01001_036E": "f_30_34", "B01001_037E": "f_35_39", "B01001_038E": "f_40_44",
    "B01001_039E": "f_45_49", "B01001_040E": "f_50_54", "B01001_041E": "f_55_59",
    "B01001_042E": "f_60_61", "B01001_043E": "f_62_64", "B01001_044E": "f_65_66",
    "B01001_045E": "f_67_69", "B01001_046E": "f_70_74", "B01001_047E": "f_75_79",
    "B01001_048E": "f_80_84", "B01001_049E": "f_85_plus",
}

VARIABLES_E.update(AGE_SEX_MAP)

def get_storage_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    storage_path = os.path.join(script_dir, "..", "data", "raw")
    if not os.path.exists(storage_path):
        os.makedirs(storage_path)
    return storage_path

def download_state_tracts(state_abbr, state_fips):
    print(f"  Fetching data for {state_abbr} (FIPS {state_fips})...")
    
    # Chunking: The API limits query length (50 vars max usually). 
    # We have ~60 vars now. We must split the request.
    
    all_codes = list(VARIABLES_E.keys())
    # Split into chunks of 40 to be safe
    chunk_size = 40
    chunks = [all_codes[i:i + chunk_size] for i in range(0, len(all_codes), chunk_size)]
    
    state_df = None
    
    for i, chunk in enumerate(chunks):
        var_string = ",".join(chunk)
        # Always include NAME in every chunk to ensure alignment (though Census API order is stable)
        if "NAME" not in chunk:
            var_string = "NAME," + var_string
            
        api_url = f"{BASE_URL}?get={var_string}&for=tract:*&in=state:{state_fips}"
        
        try:
            r = requests.get(api_url)
            r.raise_for_status()
            data = r.json()
            headers = data[0]
            rows = data[1:]
            
            chunk_df = pd.DataFrame(rows, columns=headers)
            
            if state_df is None:
                state_df = chunk_df
            else:
                # Merge based on Geo ID parts
                state_df = pd.concat([state_df, chunk_df.drop(columns=['NAME', 'state', 'county', 'tract'], errors='ignore')], axis=1)
                
        except Exception as e:
            print(f"  ❌ Failed chunk {i} for {state_abbr}: {e}")
            return None

    # De-duplicate columns if any (like NAME appearing twice)
    state_df = state_df.loc[:,~state_df.columns.duplicated()]
    
    # Rename
    state_df.rename(columns=VARIABLES_E, inplace=True)
    state_df["state_abbr"] = state_abbr
    return state_df

def main():
    output_dir = get_storage_path()
    all_data = []
    
    print(f"--- Downloading Tract Buckets (Sex x Age) + Outcomes ---")
    
    for state_abbr, fips in TARGET_STATES.items():
        df = download_state_tracts(state_abbr, fips)
        if df is not None:
            all_data.append(df)
        time.sleep(1)

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        final_df["GEOID"] = final_df["state"] + final_df["county"] + final_df["tract"]
        
        # Convert numeric
        cols_to_skip = ["census_name", "state_abbr", "GEOID", "state", "county", "tract"]
        for col in final_df.columns:
            if col not in cols_to_skip:
                final_df[col] = pd.to_numeric(final_df[col], errors='coerce')
        
        output_file = os.path.join(output_dir, "acs_tract_demographics_2023.csv")
        final_df.to_csv(output_file, index=False)
        print(f"\n✅ Success! Saved {len(final_df)} tracts with demographic buckets.")
        print(f"   Saved to: {output_file}")

    else:
        print("❌ No data downloaded.")

if __name__ == "__main__":
    main()