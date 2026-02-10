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

def get_storage_path():
    # Save to data/raw relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level from src/ to root/, then into data/raw/
    storage_path = os.path.join(script_dir, "..", "data", "raw")
    os.makedirs(storage_path, exist_ok=True)
    return storage_path

# --- DEFINING VARIABLES ---
# We map Census Codes -> Our Clean Schema Names
VARIABLES = {
    "NAME": "census_name",
    
    # 1. OUTCOMES & TARGETS
    "B17001_002E": "poverty_count_est",  # Estimate
    "B17001_002M": "poverty_count_moe",  # Margin of Error (CRITICAL MISSING PIECE)
    "B01003_001E": "total_population",
    
    # 2. RACE BUCKETS (Table B02001)
    "B02001_002E": "race_white",
    "B02001_003E": "race_black",
    "B02001_004E": "race_native",    # Was missing
    "B02001_005E": "race_asian",
    "B02001_006E": "race_pacific",   # Was missing
    "B02001_007E": "race_other",     # Was missing
    "B02001_008E": "race_two_more",  # Was missing
    
    # 3. AGE x SEX BUCKETS (Table B01001)
    # Males
    "B01001_003E": "m_00_04", "B01001_004E": "m_05_09", "B01001_005E": "m_10_14",
    "B01001_006E": "m_15_17", "B01001_007E": "m_18_19", "B01001_008E": "m_20",
    "B01001_009E": "m_21",    "B01001_010E": "m_22_24", "B01001_011E": "m_25_29",
    "B01001_012E": "m_30_34", "B01001_013E": "m_35_39", "B01001_014E": "m_40_44",
    "B01001_015E": "m_45_49", "B01001_016E": "m_50_54", "B01001_017E": "m_55_59",
    "B01001_018E": "m_60_61", "B01001_019E": "m_62_64", "B01001_020E": "m_65_66",
    "B01001_021E": "m_67_69", "B01001_022E": "m_70_74", "B01001_023E": "m_75_79",
    "B01001_024E": "m_80_84", "B01001_025E": "m_85_plus",
    # Females
    "B01001_027E": "f_00_04", "B01001_028E": "f_05_09", "B01001_029E": "f_10_14",
    "B01001_030E": "f_15_17", "B01001_031E": "f_18_19", "B01001_032E": "f_20",
    "B01001_033E": "f_21",    "B01001_034E": "f_22_24", "B01001_035E": "f_25_29",
    "B01001_036E": "f_30_34", "B01001_037E": "f_35_39", "B01001_038E": "f_40_44",
    "B01001_039E": "f_45_49", "B01001_040E": "f_50_54", "B01001_041E": "f_55_59",
    "B01001_042E": "f_60_61", "B01001_043E": "f_62_64", "B01001_044E": "f_65_66",
    "B01001_045E": "f_67_69", "B01001_046E": "f_70_74", "B01001_047E": "f_75_79",
    "B01001_048E": "f_80_84", "B01001_049E": "f_85_plus",
}

def download_state_tracts(state_abbr, state_fips):
    print(f"  Fetching data for {state_abbr} (FIPS {state_fips})...")
    
    # We must chunk the request because 60+ variables exceeds API limits
    all_codes = list(VARIABLES.keys())
    chunk_size = 40
    chunks = [all_codes[i:i + chunk_size] for i in range(0, len(all_codes), chunk_size)]
    
    state_df = None
    
    for i, chunk in enumerate(chunks):
        # Ensure NAME is in every chunk for alignment
        if "NAME" not in chunk:
            chunk = ["NAME"] + chunk
            
        var_string = ",".join(chunk)
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
                # Merge on Geography columns
                # We drop 'NAME' and geo-ids from subsequent chunks to avoid duplicates
                chunk_df = chunk_df.drop(columns=['NAME', 'state', 'county', 'tract'], errors='ignore')
                state_df = pd.concat([state_df, chunk_df], axis=1)
                
        except Exception as e:
            print(f"  ❌ Failed chunk {i} for {state_abbr}: {e}")
            return None

    # Rename to our clean schema
    state_df.rename(columns=VARIABLES, inplace=True)
    
    # Clean up duplicated columns from the concat
    state_df = state_df.loc[:,~state_df.columns.duplicated()]
    state_df["state_abbr"] = state_abbr
    
    return state_df

def main():
    print(f"--- Downloading Tract Data (Buckets + MOE + Race) ---")
    all_data = []
    
    for state_abbr, fips in TARGET_STATES.items():
        df = download_state_tracts(state_abbr, fips)
        if df is not None:
            all_data.append(df)
        time.sleep(0.5)

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        
        # Convert Numeric Columns
        # Everything except these is a number
        non_numeric = ["census_name", "state_abbr", "GEOID", "state", "county", "tract"]
        for col in final_df.columns:
            if col not in non_numeric:
                final_df[col] = pd.to_numeric(final_df[col], errors='coerce')

        output_path = os.path.join(get_storage_path(), "acs_tract_demographics_2023.csv")
        final_df.to_csv(output_path, index=False)
        print(f"\n✅ Success! Saved {len(final_df)} tracts to: {output_path}")
    else:
        print("❌ Download failed.")

if __name__ == "__main__":
    main()