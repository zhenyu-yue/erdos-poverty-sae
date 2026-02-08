import os
import shutil
import zipfile
import glob
import pandas as pd

# --- CONFIGURATION ---
# We look for this pattern in your Downloads folder
ZIP_PATTERN = "snap-zip-fns388a*.zip" 

def get_project_paths():
    """
    Returns the paths for:
    1. The project's data/raw folder
    2. The user's Downloads folder
    """
    # 1. Project data/raw folder (relative to this script)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_raw_dir = os.path.join(script_dir, "..", "data", "raw")
    
    # 2. User's Downloads folder (works on Mac/Linux/Windows)
    downloads_dir = os.path.expanduser("~/Downloads")
    
    return os.path.abspath(project_raw_dir), os.path.abspath(downloads_dir)

def process_snap_data():
    raw_dir, downloads_dir = get_project_paths()
    
    # Ensure raw directory exists
    if not os.path.exists(raw_dir):
        os.makedirs(raw_dir)
        print(f"Created directory: {raw_dir}")

    print(f"Looking for '{ZIP_PATTERN}' in {downloads_dir}...")

    # 1. Find the zip file in Downloads
    search_path = os.path.join(downloads_dir, ZIP_PATTERN)
    found_files = glob.glob(search_path)
    
    if not found_files:
        # Fallback: Check if it's already in the project folder
        search_path_local = os.path.join(raw_dir, ZIP_PATTERN)
        found_files = glob.glob(search_path_local)
        
        if not found_files:
            print("❌ File not found! Please make sure you downloaded it.")
            return
        else:
            print("Found file already in project folder.")
            zip_path = found_files[0]
    else:
        # Move it from Downloads to project folder
        source_path = found_files[0]
        filename = os.path.basename(source_path)
        dest_path = os.path.join(raw_dir, filename)
        
        print(f"Moving {filename} to project data folder...")
        shutil.move(source_path, dest_path)
        zip_path = dest_path

    # 2. Unzip
    print(f"Unzipping {os.path.basename(zip_path)}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(raw_dir)
        extracted_files = zip_ref.namelist()

    # 3. Find the Excel file
    # We look for .xls or .xlsx
    excel_files = [f for f in extracted_files if f.endswith(('.xls', '.xlsx'))]
    
    if not excel_files:
        print("❌ No Excel files found inside the zip.")
        return

    # Usually the main data file is the largest one or has a specific name
    # We'll just take the first one found for now, or print them if ambiguous
    target_excel = excel_files[0] 
    full_excel_path = os.path.join(raw_dir, target_excel)
    
    print(f"Processing Excel file: {target_excel}")
    
    # 4. Convert to CSV
    try:
        # Read Excel
        df = pd.read_excel(full_excel_path)
        
        # Save CSV
        csv_name = "snap_county_data_clean.csv"
        csv_path = os.path.join(raw_dir, csv_name)
        
        df.to_csv(csv_path, index=False)
        print(f"\n✅ SUCCESS! Data saved to: {csv_path}")
        print(f"   (Original Excel file is still at: {full_excel_path})")
        
    except Exception as e:
        print(f"❌ Error converting to CSV: {e}")
        print("Try running: pip install openpyxl xlrd")

if __name__ == "__main__":
    process_snap_data()