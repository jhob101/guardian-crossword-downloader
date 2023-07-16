# Guardian Quick Crossword Downloader

Download Guardian Quick Crossword for the current day to Google Drive.  
Downloads the Observer Speedy on Sundays.

I then sync my SuperNote eInk tablet with Google Drive which downloads the crossword to the device.

## Authenticate with Google

Follow [this guide](https://d35mpxyw7m7k7g.cloudfront.net/bigdata_1/Get+Authentication+for+Google+Service+API+.pdf) to set up OAuth for Google Drive.

Save the `client_secrets.json` to the same directory as `main.py`

## Install Python Modules

```
pip install pydrive
pip install python-dotenv
```

## Create .env file
Copy `.env.example` to  `.env` and replace the GDRIVE_DIRECTORY value with the Google Drive Folder ID of the directory you want the crosswords to upload to.

I have mine uploading to `/Supernote/Document/Crosswords` which my Supernote syncs with.

Create & navigate to the directory in GDrive and then copy the ID from the end of the URL and paste this into the .env file:

`https://drive.google.com/drive/folders/`**`18D_PklYFxR-Kfgugq_c8nNRpRoOseZ_z`**

.env file should look something like this:

```
GDRIVE_DIRECTORY=18D_PklYFxR-Kfgugq_c8nNRpRoOseZ_z
```

## Run the script for the first time

```
python main.py
```

When first run you will be prompted to authenticate with Google.  Credentials will then be saved to `credentials.txt` so that authentication is not required every time the script is run.

## Setup as cron

Run every hour between 00:30 and 06:30 (just in case it fails on earlier run)

```
30 0-6 * * * python3 /home/pi/Python_Code/guardian-crossword-downloader/main.py
```

## All Set!

From then on the script should chug away happily downloading the crosswords to your Google Drive.

Happy Crosswording!
