#!/bin/bash
echo "--- Pulling latest changes from teammates ---"
git pull origin main

echo "--- Adding your changes ---"
git add .

echo "--- Saving (Committing) ---"
timestamp=$(date "+%Y-%m-%d %H:%M:%S")
git commit -m "Auto-save: $timestamp"

echo "--- Pushing to GitHub ---"
git push origin main

echo "SUCCESS! Everything is on GitHub."
