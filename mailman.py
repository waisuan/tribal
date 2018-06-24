import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import dropbox
import os
import sys
import shelve

fromaddr = os.environ.get('FROM_ADDR', None)
fromaddr_pwd = os.environ.get('FROM_ADDR_PWD', None)
token = os.environ.get('TOKEN', None)
filename = os.environ.get('FILENAME', None)
LOCAL_DIR = './scratch/'
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


def _construct(toaddr):
    post_office = _post_office()

    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = post_office['title']

    body = post_office['message']
    msg.attach(MIMEText(body, 'plain'))

    attachment = open(LOCAL_DIR + filename, "rb")

    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',
                    "attachment; filename= %s" % filename)

    msg.attach(part)
    attachment.close()
    return msg


def _send(toaddr):
    msg = _construct(toaddr)
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(fromaddr, fromaddr_pwd)
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
    except:
        print("Error whilst sending mail: ", sys.exc_info()[0])
        return False
    finally:
        if server != None:
            server.quit()
    _clean(filename)
    return True


def _mailman_send(toaddr):
    if _download():
        return _send(toaddr)
    else:
        return False


def _mailman_store(title, message, file):
    _store(title, message)
    return _upload(file)
