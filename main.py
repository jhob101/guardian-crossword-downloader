from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import urllib.request
from datetime import date
import datetime
import os

prefix = "gdn.quick."

today = date.today()
date_string = today.strftime("%Y%m%d")

# get the datetime now
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

yesterday = today.replace(day=today.day-1)
yesterday_string = prefix + yesterday.strftime("%Y%m%d")

# Set the current working directory
current_working_directory = os.path.realpath(os.path.dirname(__file__))

# Upload path and file name
save_path = current_working_directory+'/crosswords/'

file_name = prefix + date_string + ".pdf"

# Delete yesterday's file
if os.path.isfile(save_path+yesterday_string+".pdf"):
    os.remove(save_path+yesterday_string+".pdf")

# if file already exists exit
if os.path.isfile(save_path+file_name):
    print(now + " - File already exists locally")
    exit()

# Try to down the file and exit if not found
try:
    urllib.request.urlretrieve("https://crosswords-static.guim.co.uk/" + file_name, save_path + file_name)
except Exception as e:
    print(now + " - Error downloading file:", e)
    exit()

# Download today's file
gauth = GoogleAuth()

gauth.LoadCredentialsFile(current_working_directory+"/credentials.txt")
if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()
# Save the current credentials to a file
gauth.SaveCredentialsFile(current_working_directory+"/credentials.txt")

drive = GoogleDrive(gauth)

# Check if the file already exists in the directory that it would be uploaded to.
file_id = None
parent_id = '18D_PklYFxR-Kfgugq_c8nNRpRoOseZ_z'

# Check if the file already exists in the directory that it would be uploaded to.
for file in drive.ListFile({'q': "'" + parent_id + "' in parents and trashed=false"}).GetList():
    print('Title: %s, ID: %s' % (file['title'], file['id']))
    if (file['title'] == file_name):
        file_id = file['id']
        break


if file_id is None:
    # The file doesn't exist, so upload it.
    gfile = drive.CreateFile({'title': [file_name], 'parents': [{'id': '18D_PklYFxR-Kfgugq_c8nNRpRoOseZ_z'}]})
    gfile.SetContentFile(save_path + file_name)
    gfile.Upload()
    print(now + " - File uploaded to GDrive: ", file_name)
else:
    # The file already exists, so don't upload it.
    print(now + " - File already exists in GDrive: ", file_name)