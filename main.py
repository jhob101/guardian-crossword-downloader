from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import urllib.request
from datetime import date
import datetime
import os


def get_today_date():
    return date.today()


def format_date_string(date_obj):
    return date_obj.strftime("%Y%m%d")


def get_now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_yesterday_date(today):
    return today.replace(day=today.day - 1)


def format_yesterday_string(prefix, yesterday):
    return prefix + yesterday.strftime("%Y%m%d")


def set_working_directory():
    return os.path.realpath(os.path.dirname(__file__))


def get_save_path(directory):
    return directory + '/crosswords/'


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


def main():
    prefix = "gdn.quick."
    today = get_today_date()
    date_string = format_date_string(today)
    now = get_now()
    yesterday = get_yesterday_date(today)
    yesterday_string = format_yesterday_string(prefix, yesterday)
    current_working_directory = set_working_directory()
    save_path = get_save_path(current_working_directory)
    file_name = prefix + date_string + ".pdf"

    delete_file(save_path + yesterday_string + ".pdf")

    if check_file_exists(save_path + file_name):
        print(now + " - File already exists locally")
        exit()

    download_url = "https://crosswords-static.guim.co.uk/"
    download_file(download_url, save_path, file_name)

    gauth = authenticate()
    drive = get_drive_instance(gauth)

    parent_id = '18D_PklYFxR-Kfgugq_c8nNRpRoOseZ_z'
    file_id = check_file_exists_in_drive(drive, parent_id, file_name)

    if file_id is None:
        upload_file_to_drive(drive, parent_id, file_name, save_path)
    else:
        print(now + " - File already exists in GDrive: ", file_name)


if __name__ == '__main__':
    main()
