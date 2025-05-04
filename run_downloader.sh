#!/bin/bash

# Get the absolute path of the directory where this script resides
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the script's directory
cd "$SCRIPT_DIR"

# Define the log file path
LOG_FILE="$SCRIPT_DIR/downloader.log"

# Run the Python script and append output (stdout & stderr) to the log file
echo "--- Running Crossword Downloader at $(date) ---" >> "$LOG_FILE"
$SCRIPT_DIR/venv/bin/python3 main.py >> "$LOG_FILE" 2>&1
echo "--- Finished Crossword Downloader at $(date) ---" >> "$LOG_FILE"

exit 0
