import os
import requests
from bs4 import BeautifulSoup
import zipfile
import io

# --- CONFIGURATION ---
# 1. Choose your region (Capitalize them)
TARGET_STATES = ["MD", "DC", "VA"] 

# 2. Base URL for 2023 ACS 1-Year PUMS (Compatible with 2023 Tract Data)
BASE_URL = "https://www2.census.gov/programs-surveys/acs/data/pums/2023/1-Year/"

def get_storage_path():
    """Anchor logic: saves to data/raw"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    storage_path = os.path.join(script_dir, "..", "data", "raw")
    if not os.path.exists(storage_path):
        os.makedirs(storage_path)
    return storage_path

def download_acs_data():
    output_dir = get_storage_path()
    print(f"Saving data to: {output_dir}\n")
    print(f"Target Region: {TARGET_STATES}")

    print(f"Fetching file list from Census Bureau...")
    try:
        response = requests.get(BASE_URL)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error accessing URL: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all zip links
    all_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.zip')]
    
    # FILTER: Only keep files that match our target states
    # Census files look like: csv_pmd.zip (Person Maryland), csv_hmd.zip (Housing Maryland)
    target_files = []
    for link in all_links:
        for state in TARGET_STATES:
            # Check for state abbreviation in filename (e.g. 'md.zip')
            if f"{state.lower()}.zip" in link.lower():
                target_files.append(link)

    print(f"Found {len(target_files)} files to download.")

    for i, link in enumerate(target_files):
        file_url = BASE_URL + link
        print(f"[{i+1}/{len(target_files)}] Downloading {link}...", end=" ", flush=True)

        try:
            r = requests.get(file_url)
            r.raise_for_status()
            
            # Unzip directly
            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                z.extractall(output_dir)
            
            print("Done.")
        except Exception as e:
            print(f"Failed! ({e})")

    print(f"\nSuccess! All files extracted to: {output_dir}")

if __name__ == "__main__":
    download_acs_data()