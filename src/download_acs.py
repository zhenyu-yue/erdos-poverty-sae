import os
import requests
from bs4 import BeautifulSoup
import zipfile
import io

# --- CONFIGURATION ---
BASE_URL = "https://www2.census.gov/programs-surveys/acs/data/pums/2024/1-Year/"

# Set this to False if you only want to download Maryland (for testing)
DOWNLOAD_ALL_STATES = True 
TEST_STATE = "md"  # Only used if DOWNLOAD_ALL_STATES is False

def get_storage_path():
    """
    Returns the absolute path to the 'data/raw' folder,
    relative to where THIS script is located.
    """
    # 1. Get the folder where this script (download_acs.py) lives
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Go up one level (..) and down into data/raw
    # resulting path: .../erdos-poverty-sae/data/raw
    storage_path = os.path.join(script_dir, "..", "data", "raw")
    
    # 3. Create the folder if it doesn't exist
    if not os.path.exists(storage_path):
        os.makedirs(storage_path)
        print(f"Created directory: {storage_path}")
    
    return storage_path

def download_acs_data():
    output_dir = get_storage_path()
    print(f"Saving data to: {output_dir}\n")

    print(f"Fetching file list from {BASE_URL}...")
    try:
        response = requests.get(BASE_URL)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error accessing URL: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all links that end in .zip and start with 'csv_'
    all_links = [a['href'] for a in soup.find_all('a', href=True)]
    csv_zips = [link for link in all_links if link.endswith('.zip') and link.startswith('csv_')]

    # Filter for specific state if strictly requested
    if not DOWNLOAD_ALL_STATES:
        csv_zips = [link for link in csv_zips if f"{TEST_STATE}.zip" in link.lower()]
        print(f"Test Mode: Downloading only '{TEST_STATE}' files.")

    print(f"Found {len(csv_zips)} files to download.")

    for i, link in enumerate(csv_zips):
        file_url = BASE_URL + link
        print(f"[{i+1}/{len(csv_zips)}] Downloading {link}...", end=" ", flush=True)

        try:
            r = requests.get(file_url)
            r.raise_for_status()
            
            # Unzip directly into data/raw
            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                z.extractall(output_dir)
            
            print("Done.")
        except Exception as e:
            print(f"Failed! ({e})")

    print(f"\nSuccess! All files extracted to: {output_dir}")

if __name__ == "__main__":
    download_acs_data()