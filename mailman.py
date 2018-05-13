import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import dropbox
import os

fromaddr     = os.environ.get('FROM_ADDR', 'mail.tribal.app@gmail.com')
fromaddr_pwd = os.environ.get('FROM_ADDR_PWD', None)
token        = os.environ.get('TOKEN', None)
filename     = os.environ.get('FILENAME', 'foo.pdf')

def _download():
    dbx = dropbox.Dropbox(token)
    print(dbx.users_get_current_account())
    for entry in dbx.files_list_folder('').entries:
        print(entry.name)
    try:
        dbx.files_download_to_file(filename, '/'+ filename)
    except dropbox.exceptions.ApiError:
        return False
    return True

def _construct(toaddr):
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Hello, world!"

    body = """
            Lorem ipsum dolor sit amet, consectetur adipiscing elit.
            Quisque rutrum lacus sed libero sollicitudin, sit amet finibus arcu iaculis.
            In nec varius risus, ut imperdiet tortor. Donec eu est id magna tristique ultricies non quis lorem.
            Sed pharetra quam eu libero convallis rhoncus. Nullam rutrum fermentum massa, aliquet placerat mi pharetra sit amet.
            Nulla vitae cursus arcu. In enim odio, facilisis nec vehicula et, tempor nec tortor. Praesent sed metus feugiat, gravida diam eu, interdum libero.
           """
    msg.attach(MIMEText(body, 'plain'))

    attachment = open(filename, "rb")

    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

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
    finally:
        if server != None:
            server.quit()


def _mailman(name, toaddr):
    if _download():
        _send(toaddr)
