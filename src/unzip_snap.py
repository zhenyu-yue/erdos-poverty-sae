import os
import shutil
import zipfile
import glob
import pandas as pd

# --- CONFIGURATION ---
ZIP_PATTERN = "snap-zip-fns388a*.zip" 
TARGET_FIPS_PREFIXES = ["24", "11", "51"] # MD, DC, VA

def get_project_paths():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_raw_dir = os.path.join(script_dir, "..", "data", "raw")
    downloads_dir = os.path.expanduser("~/Downloads")
    return os.path.abspath(project_raw_dir), os.path.abspath(downloads_dir)

def process_snap_data():
    raw_dir, downloads_dir = get_project_paths()
    
    if not os.path.exists(raw_dir):
        os.makedirs(raw_dir)

    # 1. FIND & MOVE ZIP
    print(f"Looking for '{ZIP_PATTERN}'...")
    search_path = os.path.join(downloads_dir, ZIP_PATTERN)
    found_files = glob.glob(search_path)
    
    zip_path = None
    if found_files:
        source_path = found_files[0]
        dest_path = os.path.join(raw_dir, os.path.basename(source_path))
        print(f"Moving {os.path.basename(source_path)} to project folder...")
        shutil.move(source_path, dest_path)
        zip_path = dest_path
    else:
        # Check local
        local_search = os.path.join(raw_dir, ZIP_PATTERN)
        found_local = glob.glob(local_search)
        if found_local:
            print("Found zip in project folder.")
            zip_path = found_local[0]
        else:
            print("❌ Zip file not found in Downloads or data/raw.")
            return

    # 2. UNZIP
    print(f"Unzipping {os.path.basename(zip_path)}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(raw_dir)
        extracted_files = zip_ref.namelist()

    # 3. FIND EXCEL
    excel_files = [f for f in extracted_files if f.endswith(('.xls', '.xlsx'))]
    if not excel_files:
        print("❌ No Excel files found inside zip.")
        return
    
    target_excel = excel_files[0]
    full_excel_path = os.path.join(raw_dir, target_excel)
    print(f"Processing Excel: {target_excel}")

    # 4. CLEAN & SAVE (The Critical Step)
    try:
        # SKIP the first 3 rows of garbage headers (Standard USDA format)
        df = pd.read_excel(full_excel_path, header=3)
        
        # Identify Columns (USDA format is usually: FIPS, Name, ... TotalPA, TotalNonPA, Total)
        # We assume the columns are roughly in this order.
        # We rename the first two and the Total Persons column (usually ~column 6 or 7)
        
        # Rename the first 2 columns safely
        df.rename(columns={df.columns[0]: 'fips', df.columns[1]: 'county_name'}, inplace=True)
        
        # Find the "Total" participation column dynamically
        # It usually contains "Total" and "People" or just "Total" as the header
        # Let's grab the column that represents "Total SNAP Persons"
        # In USDA NER files, it's often the 3rd numerical column.
        # Safer bet: Look for 'Total' in the name
        total_cols = [c for c in df.columns if "Total" in str(c) and "People" in str(c)]
        
        if total_cols:
             target_col = total_cols[0] # Take the first one found
             df['snap_persons_total'] = df[target_col]
        else:
            # Fallback: Assume it is Column Index 5 (0-based) based on standard NER format
            # [FIPS, Name, PA_Person, NonPA_Person, Total_Person, ...]
            print("⚠️ Could not auto-detect Total column. Using index 4 (5th col). Check result!")
            df['snap_persons_total'] = df.iloc[:, 4]

        # Filter for DMV (MD=24, DC=11, VA=51)
        # Clean FIPS: Ensure they are strings and have 5 digits (e.g., "24031")
        df['fips'] = df['fips'].astype(str).str.zfill(5) # "24031"
        
        # Filter rows where FIPS starts with our target state codes
        mask = df['fips'].str[:2].isin(TARGET_FIPS_PREFIXES)
        df_clean = df[mask].copy()
        
        # Select only clean columns
        final_df = df_clean[['fips', 'county_name', 'snap_persons_total']]
        
        # Save
        csv_path = os.path.join(raw_dir, "snap_county_data_clean.csv")
        final_df.to_csv(csv_path, index=False)
        
        print(f"\n✅ SUCCESS! Cleaned data saved to: {csv_path}")
        print(f"   Rows: {len(final_df)}")
        print(final_df.head(3))
        
    except Exception as e:
        print(f"❌ Error cleaning data: {e}")

if __name__ == "__main__":
    process_snap_data()