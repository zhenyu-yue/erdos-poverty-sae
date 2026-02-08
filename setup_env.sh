#!/bin/bash

echo "--- Setting up Erdos Poverty Project Environment ---"

# 1. Check if Conda is installed
if command -v conda &> /dev/null; then
    echo "✅ Conda found."
    
    # Create environment if it doesn't exist
    # We use '|| true' so it doesn't crash if the env already exists
    conda create -n poverty-project python=3.9 -y || true
    
    echo "--- Activating Environment ---"
    # This trick makes conda activate work in scripts
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate poverty-project
else
    echo "⚠️ Conda not found. Using standard Python venv..."
    python3 -m venv venv
    source venv/bin/activate
fi

# 2. Install everything from requirements.txt
echo "--- Installing Libraries ---"
pip install -r requirements.txt

echo "--- Setup Complete! ---"
echo "To start working, type:"
echo "conda activate poverty-project"