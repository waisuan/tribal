from bottle import get, post, request, route, run, static_file, error, debug, response, TEMPLATES, BottleException
import mailman
import os

# static set-up
@route('/favicon.ico')
def favicon():
    return static_file('favicon.ico', root='./resource/')

@route('/view/:path#.+#')
def server_static(path):
    return static_file(path, root='./resource/view/')

@route('/js/:path#.+#')
def server_static(path):
    return static_file(path, root='./resource/js/')

@route('/css/:path#.+#')
def server_static(path):
    return static_file(path, root='./resource/css/')

# route set-up
@get('/')
@get('/<path>')
def index(path=None):
    raise static_file('index.html', root='./resource')

@post('/')
def sendMail():
    try:
        req = request.json
        if req is None:
            raise ValueError
        if not mailman._mailman_send(req['name'], req['email']):
            raise RuntimeError
    except (ValueError, KeyError, RuntimeError):
        response.status = 400
        return
    response.status = 200
    return

@post('/admin')
def editMail():
    try:
        title = request.forms.get('title')
        message = request.forms.get('message')
        attachment = request.files.get('attachment')
        if attachment is None or title is None or message is None:
            raise ValueError
        name, ext = os.path.splitext(attachment.filename)
        if ext not in ('.pdf'):
            raise ValueError
        attachment.save('./scratch', True)
        if not mailman._mailman_store(title, message, attachment.filename):
            raise RuntimeError
    except (ValueError, KeyError, RuntimeError, BottleException):
        response.status = 400
        return
    response.status = 200
    return

# error handling
@error(404)
def mistake404(code):
    return static_file('404.html', root='./app')

# start
TEMPLATES.clear()
if os.environ.get('APP_LOCATION') == 'heroku':
    run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
elif os.environ.get('APP_LOCATION') == 'heroku_local':
    run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
else:
    run(host='localhost', port=8080, debug=True)
