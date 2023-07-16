from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import urllib.request
from datetime import date
import datetime
import os
from dotenv import load_dotenv

def get_today_date():
    return date.today()


def get_yesterday_date(today):
    return today.replace(day=today.day - 1)


# Get datetime in format YYYY-MM-DD HH:MM:SS
def get_now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Get date in format YYYYMMDD
def format_date_string(date_obj):
    return date_obj.strftime("%Y%m%d")


def get_filename(prefix, date_obj):
    return prefix + format_date_string(date_obj) + ".pdf"


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


def download_file(url, save_path, file_name):
    try:
        urllib.request.urlretrieve(url + file_name, save_path + file_name)
    except Exception as e:
        print(get_now() + " - Error downloading file:", e)
        exit()


def authenticate():
    gauth = GoogleAuth()
    current_working_directory = set_working_directory()
    gauth.LoadCredentialsFile(current_working_directory + "/credentials.txt")
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    gauth.SaveCredentialsFile(current_working_directory + "/credentials.txt")
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


def get_prefix(day):
    if day.weekday() == 6:  # if Sunday, get the Observer speedy crossword
        prefix = "obs.speedy."
    else:  # otherwise get the Guardian quick crossword
        prefix = "gdn.quick."
    return prefix


def clean_files_on_date(current_working_directory, date_to_remove):
    prefix = get_prefix(date_to_remove)
    yesterday_filename = get_filename(prefix, date_to_remove)
    save_path = get_save_path(current_working_directory)
    # if file exists locally, delete it
    if check_file_exists(save_path + yesterday_filename):
        delete_file(save_path + yesterday_filename)
        return True
    return False


def main():
    load_dotenv()
    # Set up variables
    now = get_now()  # Used for logging

    current_working_directory = set_working_directory()
    save_path = get_save_path(current_working_directory)

    today = get_today_date()
    today_filename = get_filename(get_prefix(today), today)

    # Check if file exists locally
    if check_file_exists(save_path + today_filename):
        print(now + " - File already exists locally")
    else:  # Download file
        print(now + " - File does not exist locally, downloading...")
        download_host = "https://crosswords-static.guim.co.uk/"
        download_file(download_host, save_path, today_filename)

    # Check if file exists in GDrive
    gauth = authenticate()
    drive = get_drive_instance(gauth)

    # parent_id = '18D_PklYFxR-Kfgugq_c8nNRpRoOseZ_z'
    # Get parent directory from .env file
    parent_id = os.getenv('GDRIVE_DIRECTORY')

    file_id = check_file_exists_in_drive(drive, parent_id, today_filename)

    if file_id is None:  # Upload file to GDrive
        upload_file_to_drive(drive, parent_id, today_filename, save_path)
    else:
        print(now + " - File already exists in GDrive: ", today_filename)

    # Clean up files
    yesterday = get_yesterday_date(today)
    if clean_files_on_date(current_working_directory, yesterday):
        print(get_now() + " - Deleted file: ", get_filename(get_prefix(yesterday), yesterday))


if __name__ == '__main__':
    main()
