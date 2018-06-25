import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import requests
import dropbox
import os
import sys
import shelve

MAIL_DOMAIN = os.environ.get('MAIL_DOMAIN', None)
MAIL_API = os.environ.get('MAIL_API', None)
fromaddr = os.environ.get('FROM_ADDR', None)
token = os.environ.get('TOKEN', None)
filename = os.environ.get('FILENAME', None)
LOCAL_DIR = os.path.join(os.path.dirname(__file__), 'scratch/')
DROPBOX_DIR = '/'
CHUNK_SIZE = 2 * 1024 * 1024


def _post_office():
    return shelve.open('post_office.db', writeback=True)


def _clean(file):
    if os.path.isfile(LOCAL_DIR + file):
        os.remove(LOCAL_DIR + file)
    else:
        print("Error: %s not found" % file)


def _store(title, message):
    post_office = _post_office()
    post_office['title'] = title
    post_office['message'] = message
    post_office.close()


def _upload(file):
    print(os.listdir(LOCAL_DIR))
    dbx = dropbox.Dropbox(token)
    try:
        file_size = os.path.getsize(LOCAL_DIR + file)
        with open(LOCAL_DIR + file, 'rb') as f:
            if file_size <= CHUNK_SIZE:
                dbx.files_upload(f.read(), DROPBOX_DIR + filename,
                                 dropbox.files.WriteMode('overwrite'))
            else:
                upload_session_start_result = dbx.files_upload_session_start(
                    f.read(CHUNK_SIZE))
                cursor = dropbox.files.UploadSessionCursor(
                    session_id=upload_session_start_result.session_id,
                    offset=f.tell())
                commit = dropbox.files.CommitInfo(path=DROPBOX_DIR + filename)
                while f.tell() < file_size:
                    if ((file_size - f.tell()) <= CHUNK_SIZE):
                        dbx.files_upload_session_finish(
                            f.read(CHUNK_SIZE), cursor, commit)
                    else:
                        dbx.files_upload_session_append_v2(
                            f.read(CHUNK_SIZE), cursor)
                        cursor.offset = f.tell()
    except dropbox.exceptions.ApiError:
        return False
    _clean(file)
    return True


def _download():
    dbx = dropbox.Dropbox(token)
    try:
        dbx.files_download_to_file(LOCAL_DIR + filename,
                                   DROPBOX_DIR + filename)
    except dropbox.exceptions.ApiError:
        return False
    return True


def _send(toaddr):
    post_office = _post_office()
    attachment = open(LOCAL_DIR + filename, "rb")

    sent = requests.post(
        "https://api.mailgun.net/v3/" + MAIL_DOMAIN + "/messages",
        auth=("api", MAIL_API),
        files=[("attachment", (filename, attachment.read()))],
        data={
            "from": "tribal. <mailgun@" + MAIL_DOMAIN + ">",
            "to": [toaddr],
            "subject": post_office['title'],
            "text": post_office['message']
        })

    attachment.close()
    _clean(filename)
    return sent


def _mailman_send(toaddr):
    if _download():
        return _send(toaddr)
    else:
        return False


def _mailman_store(title, message, file):
    _store(title, message)
    return _upload(file)
