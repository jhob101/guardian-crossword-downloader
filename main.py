from pydrive.auth import GoogleAuth, AuthError
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
    credentials_path = os.path.join(set_working_directory(), "credentials.json")
    print(get_now() + f" - Checking credentials file: {credentials_path}")

    # Attempt to load existing credentials
    try:
        gauth.LoadCredentialsFile(credentials_path)
    except Exception as e: # Catch potential issues during load (e.g., file corrupt)
        print(get_now() + f" - Warning: Could not load credentials file: {e}. Will attempt to re-authenticate.")
        gauth.credentials = None # Ensure we trigger re-auth

    if gauth.credentials is None:
        print(get_now() + " - No valid credentials found, attempting interactive login...")
        try:
            gauth.LocalWebserverAuth() # This blocks until flow is complete or fails
            print(get_now() + " - Interactive login successful.")
            # Save credentials ONLY after successful authentication
            gauth.SaveCredentialsFile(credentials_path)
            print(get_now() + f" - Credentials saved to {credentials_path}")
        except AuthError as e:
            print(get_now() + f" - ERROR: Google Drive Authentication failed during interactive login: {e}")
            print(get_now() + " - Please check your network connection and browser pop-up settings.")
            print(get_now() + " - Exiting due to authentication failure.")
            exit(1) # Exit script if auth fails critically
        except Exception as e: # Catch other potential errors during auth
            print(get_now() + f" - ERROR: An unexpected error occurred during interactive login: {e}")
            print(get_now() + " - Exiting due to authentication failure.")
            exit(1)

    elif gauth.access_token_expired:
        print(get_now() + " - Credentials expired, attempting to refresh...")
        try:
            gauth.Refresh()
            print(get_now() + " - Credentials refreshed successfully.")
            # Save the refreshed credentials
            gauth.SaveCredentialsFile(credentials_path)
            print(get_now() + f" - Refreshed credentials saved to {credentials_path}")
        except AuthError as e: # Catch specific refresh errors
            print(get_now() + f" - ERROR: Failed to refresh Google Drive credentials: {e}")
            print(get_now() + " - This might require re-authentication.")
            # Optionally: Delete the invalid credentials file to force re-auth next time?
            # try:
            #     os.remove(credentials_path)
            #     print(get_now() + " - Removed potentially invalid credentials file.")
            # except OSError as del_e:
            #     print(get_now() + f" - Warning: Could not remove credentials file {credentials_path}: {del_e}")
            print(get_now() + " - Exiting due to authentication failure.")
            exit(1) # Exit script if refresh fails
        except Exception as e: # Catch other potential errors during refresh
             print(get_now() + f" - ERROR: An unexpected error occurred during credential refresh: {e}")
             print(get_now() + " - Exiting due to authentication failure.")
             exit(1)
    else:
        print(get_now() + " - Credentials valid, proceeding.")
        # No need to Authorize() here, PyDrive handles it implicitly when making calls
        # gauth.Authorize() # This call is often redundant

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


# Clean up old files that are confirmed to be on Google Drive
def cleanup_old_synced_files(drive, parent_id, save_path, today_date_obj):
    print(get_now() + " - Starting cleanup of old, synced files...")
    today_str = format_date_string(today_date_obj) # YYYYMMDD format for comparison
    deleted_count = 0

    # List files in the local save directory
    try:
        local_files = [f for f in os.listdir(save_path) if os.path.isfile(os.path.join(save_path, f))]
    except FileNotFoundError:
        print(get_now() + f" - Error: Local save path not found: {save_path}")
        return

    # Get list of files in Google Drive target folder for efficient checking
    drive_files = {}
    try:
        file_list = drive.ListFile({'q': f"'{parent_id}' in parents and trashed=false"}).GetList()
        for drive_file in file_list:
            drive_files[drive_file['title']] = drive_file['id']
    except Exception as e:
        print(get_now() + f" - Error listing files in Google Drive folder {parent_id}: {e}")
        # Decide if we should proceed without Drive confirmation or stop
        print(get_now() + " - Stopping cleanup due to GDrive error.")
        return


    for filename in local_files:
        # Basic check: Is it a PDF? Does it look like YYYYMMDD.<rest>.pdf?
        if filename.lower().endswith('.pdf') and len(filename) > 13 and filename[:8].isdigit():
            file_date_str = filename[:8]

            # Check 1: Is the file from a date *before* today?
            if file_date_str < today_str:
                file_path = os.path.join(save_path, filename)

                # Check 2: Does this file exist in Google Drive?
                if filename in drive_files:
                    print(get_now() + f" - Found old file '{filename}' locally and in GDrive. Deleting local copy.")
                    try:
                        delete_file(file_path)
                        deleted_count += 1
                    except Exception as e:
                        print(get_now() + f" - Error deleting local file {filename}: {e}")
                else: # Optional: Log if an old local file is NOT found in Drive
                    print(get_now() + f" - Found old local file '{filename}' but it's NOT in GDrive. Keeping local copy.")

    if deleted_count > 0:
        print(get_now() + f" - Cleanup finished. Deleted {deleted_count} old local file(s).")
    else:
        print(get_now() + " - Cleanup finished. No old local files needed deletion.")


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

    cleanup_old_synced_files(drive, parent_id, save_path, today)


if __name__ == "__main__":
    main()
