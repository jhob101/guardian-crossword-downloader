from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import urllib.request
import datetime
import os
from dotenv import load_dotenv


def get_today_date():
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.date()


def get_yesterday_date(today):
    return today.replace(day=today.day - 1)


# Get datetime in format YYYY-MM-DD HH:MM:SS
def get_now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Get date in format YYYYMMDD
def format_date_string(date_obj):
    return date_obj.strftime("%Y%m%d")


def get_remote_filename(crossword_type, date_obj):
    return  crossword_type + '.' + format_date_string(date_obj)  + ".pdf"


def set_working_directory():
    return os.path.realpath(os.path.dirname(__file__))


def get_save_path(directory):
    sub_directory = '/crosswords/'
    crosswords_directory = directory + sub_directory

    # if directory does not exist, create it
    if not os.path.exists(crosswords_directory):
        print(get_now() + " - Creating directory: ", crosswords_directory)
        os.makedirs(crosswords_directory)

    return crosswords_directory


def delete_file(file_path):
    if os.path.isfile(file_path):
        os.remove(file_path)


def check_file_exists(file_path):
    return os.path.isfile(file_path)


def download_file(url, file_name, save_path, local_filename):
    try:
        urllib.request.urlretrieve(url + file_name, save_path + local_filename)
    except Exception as e:
        print(get_now() + " - Error downloading file:", e)
        exit()


def authenticate():
    gauth = GoogleAuth()
    current_working_directory = set_working_directory()

    gauth.LoadCredentialsFile(current_working_directory + "/credentials.json")
    print (get_now() + " - Checking credentials for: " + current_working_directory + "/credentials.json")
    if gauth.credentials is None:
        print(get_now() + " - No credentials found, requesting user to log in")
        gauth.LocalWebserverAuth()
        if not os.path.exists(current_working_directory + "credentials.json"):
          gauth.SaveCredentialsFile(current_working_directory + "/credentials.json")
    elif gauth.access_token_expired:
        print(get_now() + " - Token expired, refreshing...")
        gauth.Refresh()
    else:
        print(get_now() + " - Credentials exist, authorising...")
        gauth.Authorize()

    return gauth


def get_drive_instance(gauth):
    return GoogleDrive(gauth)


def check_file_exists_in_drive(drive, parent_id, file_name):
    for file in drive.ListFile({'q': "'" + parent_id + "' in parents and trashed=false"}).GetList():
        # print('Title: %s, ID: %s' % (file['title'], file['id']))
        if file['title'] == file_name:
            return file['id']
    return None


def upload_file_to_drive(drive, parent_id, file_name, save_path):
    gfile = drive.CreateFile({'title': file_name, 'parents': [{'id': parent_id}]})
    gfile.SetContentFile(save_path + file_name)
    gfile.Upload()
    print(get_now() + " - File uploaded to GDrive: ", file_name)


def get_crossword_type_key(day):
    if day.weekday() == 6:  # if Sunday, get the Observer speedy crossword
        key = "obs.speedy"
    else:  # otherwise get the Guardian quick crossword
        key = "gdn.quick"
    return key


def clean_files_on_date(current_working_directory, date_to_remove):
    prefix = get_crossword_type_key(date_to_remove)
    yesterday_filename = rewrite_filename(get_remote_filename(prefix, date_to_remove))
    save_path = get_save_path(current_working_directory)
    # if file exists locally, delete it
    if check_file_exists(save_path + yesterday_filename):
        delete_file(save_path + yesterday_filename)
        return True
    return False

import os

def rewrite_filename(filename):
    # Split off the extension
    name, ext = os.path.splitext(filename)

    # Split the name into parts
    parts = name.split('.')

    date_part = parts[-1]
    rest = parts[:-1]

    # Reconstruct in the desired format
    new_name = f"{date_part}." + ".".join(rest) + ext
    return new_name



def main():
    load_dotenv()
    # Set up variables
    now = get_now()  # Used for logging

    current_working_directory = set_working_directory()
    save_path = get_save_path(current_working_directory)

    today = get_today_date()
    today_filename = get_remote_filename(get_crossword_type_key(today), today)
    local_today_filename = rewrite_filename(today_filename)

    # Check if file exists locally
    if check_file_exists(save_path + local_today_filename):
        print(now + " - File already exists locally")
    else:  # Download file
        print(now + " - File does not exist locally, downloading...")
        download_host = "https://crosswords-static.guim.co.uk/"
        download_file(download_host, today_filename, save_path, local_today_filename)

    # Check if file exists in GDrive
    gauth = authenticate()
    drive = get_drive_instance(gauth)

    # parent_id = '18D_PklYFxR-Kfgugq_c8nNRpRoOseZ_z'
    # Get parent directory from .env file
    parent_id = os.getenv('GDRIVE_DIRECTORY')

    file_id = check_file_exists_in_drive(drive, parent_id, local_today_filename)

    if file_id is None:  # Upload file to GDrive
        upload_file_to_drive(drive, parent_id, local_today_filename, save_path)
    else:
        print(now + " - File already exists in GDrive: ", local_today_filename)

    # Clean up files
    yesterday = get_yesterday_date(today)
    if clean_files_on_date(current_working_directory, yesterday):
        print(get_now() + " - Deleted file: ", rewrite_filename(get_remote_filename(get_crossword_type_key(yesterday), yesterday)))


if __name__ == '__main__':
    main()
