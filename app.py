from bottle import get, post, request, route, run, static_file, error, debug, response
import mailman

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
def index():
    raise static_file('index.html', root='./resource')

@post('/')
def submit():
    try:
        req = request.json
        if req is None:
            raise ValueError

        mailman._mailman(req['name'], req['email'])
    except ValueError:
        response.status = 400
    except KeyError:
        response.status = 400
    response.status = 200
    return

# error handling
@error(404)
def mistake404(code):
    return static_file('404.html', root='./app')

# start
# debug(True)
run(host='localhost', port=8080, debug=True)
