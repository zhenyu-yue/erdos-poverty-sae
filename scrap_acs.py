import requests
from bs4 import BeautifulSoup
import os
import zipfile
import io

# URL provided
BASE_URL = "https://www2.census.gov/programs-surveys/acs/data/pums/2024/1-Year/"
OUTPUT_DIR = "acs_csv_all"

def download_all_csvs():
    # Create the output directory in the CURRENT folder
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory: {os.path.abspath(OUTPUT_DIR)}")
    else:
        print(f"Saving to existing directory: {os.path.abspath(OUTPUT_DIR)}")

    print(f"Fetching file list from {BASE_URL}...")
    try:
        response = requests.get(BASE_URL)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error accessing URL: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all links
    all_links = [a['href'] for a in soup.find_all('a', href=True)]
    
    # Filter: Must end in .zip AND start with 'csv_' (excludes SAS files)
    csv_zips = [link for link in all_links if link.endswith('.zip') and link.startswith('csv_')]

    print(f"Found {len(csv_zips)} CSV zip files. Starting download...")

    count = 0
    for link in csv_zips:
        file_url = BASE_URL + link
        print(f"[{count+1}/{len(csv_zips)}] Downloading {link}...", end=" ", flush=True)

        try:
            r = requests.get(file_url)
            r.raise_for_status()
            
            # Unzip directly into the folder
            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                z.extractall(OUTPUT_DIR)
            
            print("Done.")
            count += 1
        except Exception as e:
            print(f"Failed! ({e})")

    print(f"\nSuccess! All {count} files extracted to: {os.path.abspath(OUTPUT_DIR)}")

if __name__ == "__main__":
    download_all_csvs()