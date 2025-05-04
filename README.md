# Guardian Quick Crossword Downloader

Download Guardian Quick Crossword for the current day to Google Drive.  
Downloads the Observer Speedy on Sundays.

I then sync my SuperNote eInk tablet with Google Drive which downloads the crossword to the device.

## Setup Instructions

Follow these steps to set up the downloader on your system (e.g., a Raspberry Pi or other Linux machine).

### 1. Clone the Repository

```bash
git clone <repository_url> # Replace with the actual URL if applicable
cd guardian-crossword-downloader
```

### 2. Create and Activate Virtual Environment

It's recommended to use a Python virtual environment to manage dependencies.

```bash
# Create the virtual environment directory named 'venv'
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# You should see (venv) prefixed to your shell prompt
# To deactivate later, simply run: deactivate
```

### 3. Install Dependencies

With the virtual environment *active*, install the required Python packages:

```bash
pip install -r requirements.txt
```

### 4. Authenticate with Google

Follow [this guide](https://d35mpxyw7m7k7g.cloudfront.net/bigdata_1/Get+Authentication+for+Google+Service+API+.pdf) to set up OAuth credentials for Google Drive access.

*   Download the credentials file and save it as `client_secrets.json` in the project's root directory (where `main.py` is located).

### 5. Configure Google Drive Folder

*   Copy the example environment file `.env.example` to `.env`:
    ```bash
    cp .env.example .env
    ```
*   Edit the `.env` file.
*   Find the Google Drive folder ID where you want the crosswords uploaded. Create the folder in Google Drive if it doesn't exist, navigate to it, and copy the ID from the end of the URL:
    `https://drive.google.com/drive/folders/`**`YOUR_FOLDER_ID_HERE`**
*   Replace the placeholder value in `.env` with your actual folder ID:
    ```
    GDRIVE_DIRECTORY=YOUR_FOLDER_ID_HERE
    ```

## Running the Script

### Manually

You can run the script directly using the provided shell script. This script ensures the correct Python environment is used and logs output.

```bash
# Make sure the script is executable (only needed once)
chmod +x run_downloader.sh

# Run the script
./run_downloader.sh
```

*   **First Run:** When you run the script for the very first time (either manually or via cron), you will likely be prompted in the terminal to visit a URL in your browser to authorize Google account access. Follow the instructions. Credentials will be saved to `credentials.json` for future runs.
*   **Logging:** Output from the script is appended to `downloader.log` in the project directory.
*   **Local Storage:** The script temporarily downloads crosswords to a `crosswords/` subdirectory before uploading.

### Automated (Cron Job)

To run the downloader automatically (e.g., daily), you can set up a cron job.

1.  Open the crontab editor:
    ```bash
    crontab -e
    ```
2.  Add a line similar to the following, **replacing `/path/to/project` with the actual absolute path** to the `guardian-crossword-downloader` directory on your system:

    ```cron
    # Example: Run daily at 7:00 AM
    0 7 * * * /path/to/project/guardian-crossword-downloader/run_downloader.sh
    ```
    *   This command tells cron to execute the `run_downloader.sh` script at 7:00 AM every day.
    *   The `run_downloader.sh` script handles activating the virtual environment and logging output to `downloader.log`.
3.  Save and close the crontab editor.

## All Set!

From then on the script should chug away happily downloading the crosswords to your Google Drive.

Happy Crosswording!
