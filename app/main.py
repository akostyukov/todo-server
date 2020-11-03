import re
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse

from app.authServer import login_page, register_page, login, register, logout
from app.config import env, session
from app.auth_decor import auth
from app.forms import TaskForm
from app.models import Task, Token, User
from app.response import Response, Request


class TaskHandler(BaseHTTPRequestHandler):
    def set_headers(self, code, header, url, token=None, cookie_expires=None):
        self.send_response(code)
        self.send_header(header, url)

        if token:
            cookie = SimpleCookie()
            cookie['token'] = token
            cookie['token']['expires'] = cookie_expires
            self.send_header('Set-Cookie', cookie.output(header=''))

        self.end_headers()

    def do_GET(self):
        self.handler('get')

    def do_POST(self):
        post_data = parse.parse_qs(self.rfile.read(int(self.headers['Content-Length'])).decode())
        data = {key: post_data.get(key)[0] for key in post_data}
        self.handler('post', data)

    def handler(self, method, data=None):
        response = routes(self.path, method, data, SimpleCookie(self.headers.get('Cookie')))

        self.set_headers(*response.headers)
        self.wfile.write(response.data.encode())


@auth
def task_list(request):
    # if Token.check_user(cookie):
    headers = 200, 'Content-Type', 'text/html'
    data = env.get_template('index.html').render(
        form=TaskForm(),
        tasks=session.query(Task).filter_by(status=True, user_id=User.get_user(request.cookie).id).all()[::-1],
        done_tasks=session.query(Task).filter_by(status=False, user_id=User.get_user(request.cookie).id).all(),
        current_user=User.get_user(request.cookie).login
    )

    return Response(headers, data)


# else:
# headers = 302, 'Location', '/login'
# return Response(headers)

@auth
def add_task(request):
    if Token.check_user(request.cookie):
        headers = 302, 'Location', '/'

        session.add(Task(request.data.get('task'), User.get_user(request.cookie).id))
        session.commit()
    else:
        headers = 302, 'Location', '/login'

    return Response(headers)


@auth
def delete_task(request):
    if Token.check_user(request.cookie):
        headers = 302, 'Location', '/'

        if User.get_user(request.cookie).id == session.query(Task).get(request.task_id).user_id:
            session.query(Task).get(request.task_id).delete_task()
    else:
        headers = 302, 'Location', '/login'

    return Response(headers)


@auth
def done_task(request):
    if Token.check_user(request.cookie):
        headers = 302, 'Location', '/'

        if User.get_user(request.cookie).id == session.query(Task).get(request.task_id).user_id:
            session.query(Task).get(request.task_id).set_done()
    else:
        headers = 302, 'Location', '/login'

    return Response(headers)


@auth
def clear_all(request):
    headers = 302, 'Location', '/'
    Task.clear_all(request.cookie)

    return Response(headers)


urls = [
    ('/', 'get', task_list),
    ('/', 'post', add_task),
    (r'/delete/(?P<task_id>\d+)', 'get', delete_task),
    (r'/done/(?P<task_id>\d+)', 'get', done_task),
    ('/clear', 'get', clear_all),
    ('/login', 'get', login_page),
    ('/register', 'get', register_page),
    ('/login', 'post', login),
    ('/register', 'post', register),
    ('/logout', 'get', logout),
]


def routes(path, do_method, data, cookie):
    task_id = None
    req = Request()

    for url, method, handler in urls:
        received_url = re.match(url, path)
        req.user = None
        if received_url is not None and received_url.group(0) == path and method == do_method:
            try:
                req.task_id = int(received_url.group('task_id'))
            except:
                pass

            # if method == 'post':
            #     return handler(data, cookie)
            # if task_id is not None:
            #     return handler(task_id, cookie)
            # return handler(cookie)

            return handler(req)


server = HTTPServer(('', 8000), TaskHandler)
server.serve_forever()
