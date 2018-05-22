import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import dropbox
import os
import sys

fromaddr     = os.environ.get('FROM_ADDR', None)
fromaddr_pwd = os.environ.get('FROM_ADDR_PWD', None)
token        = os.environ.get('TOKEN', None)
filename     = os.environ.get('FILENAME', 'foo.pdf')
mail_config       = os.environ.get('MAIL_CONFIG', 'mail_template.config')
LOCAL_DIR    = './scratch/'
DROPBOX_DIR  = '/'
CHUNK_SIZE = 2 * 1024 * 1024

def _clean(file):
    if os.path.isfile(LOCAL_DIR + file):
        os.remove(LOCAL_DIR + file)
    else:
        print("Error: %s not found" % file)

def _store(title, message):
    with open(mail_config, 'w') as mc:
        mc.write(title   + '\n')
        mc.write(message + '\n')
    return

def _upload(file):
    dbx = dropbox.Dropbox(token)
    try:
        file_size = os.path.getsize(LOCAL_DIR + file)
        with open(LOCAL_DIR + file, 'rb') as f:
            if file_size <= CHUNK_SIZE:
                dbx.files_upload(f.read(), DROPBOX_DIR + filename, dropbox.files.WriteMode('overwrite'))
            else:
                upload_session_start_result = dbx.files_upload_session_start(f.read(CHUNK_SIZE))
                cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id,
                                                           offset=f.tell())
                commit = dropbox.files.CommitInfo(path=DROPBOX_DIR + filename)
                while f.tell() < file_size:
                    if ((file_size - f.tell()) <= CHUNK_SIZE):
                        dbx.files_upload_session_finish(f.read(CHUNK_SIZE),
                                                        cursor,
                                                        commit)
                    else:
                        dbx.files_upload_session_append_v2(f.read(CHUNK_SIZE),
                                                           cursor)
                        cursor.offset = f.tell()
    except dropbox.exceptions.ApiError:
        return False
    _clean(file)
    return True

def _download():
    dbx = dropbox.Dropbox(token)
    # print(dbx.users_get_current_account())
    # for entry in dbx.files_list_folder('').entries:
    #     print(entry.name)
    try:
        dbx.files_download_to_file(LOCAL_DIR + filename, DROPBOX_DIR + filename)
    except dropbox.exceptions.ApiError:
        return False
    return True

def _construct(name, toaddr):
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Hello, " + name

    body = """
            Lorem ipsum dolor sit amet, consectetur adipiscing elit.
            Quisque rutrum lacus sed libero sollicitudin, sit amet finibus arcu iaculis.
            In nec varius risus, ut imperdiet tortor. Donec eu est id magna tristique ultricies non quis lorem.
            Sed pharetra quam eu libero convallis rhoncus. Nullam rutrum fermentum massa, aliquet placerat mi pharetra sit amet.
            Nulla vitae cursus arcu. In enim odio, facilisis nec vehicula et, tempor nec tortor. Praesent sed metus feugiat, gravida diam eu, interdum libero.
           """
    msg.attach(MIMEText(body, 'plain'))

    attachment = open(LOCAL_DIR + filename, "rb")

    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    msg.attach(part)
    attachment.close()
    return msg

def _send(name, toaddr):
    msg = _construct(name, toaddr)

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


def _mailman_send(name, toaddr):
    if  _download():
        return _send(name, toaddr)
    else:
        return False

def _mailman_store(title, message, file):
    _store(title, message)
    return _upload(file)
