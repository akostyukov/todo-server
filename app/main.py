import re
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse

from app.auth_views import login_page, register_page, login, register, logout
from app.config import env, session
from app.auth_decorators import auth, check_match
from app.forms import TaskForm
from app.models import Task, User, Token
from app.response_and_request import Response, Request


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
    headers = 200, 'Content-Type', 'text/html'
    data = env.get_template('index.html').render(
        form=TaskForm(),
        tasks=session.query(Task).filter_by(status=True, user_id=request.user.id).all()[::-1],
        done_tasks=session.query(Task).filter_by(status=False, user_id=request.user.id).all(),
        current_user=request.user.login
    )

    return Response(headers, data)


@auth
def add_task(request):
    headers = 302, 'Location', '/'
    Task.add_task(Task(request.data.get('task'), request.user.id))

    return Response(headers)


@auth
@check_match
def delete_task(request):
    headers = 302, 'Location', '/'
    Task.delete_task(request.task_id)

    return Response(headers)


@auth
@check_match
def done_task(request):
    headers = 302, 'Location', '/'
    Task.set_done(request.task_id)

    return Response(headers)


@auth
def clear_all(request):
    headers = 302, 'Location', '/'
    Task.clear_all(request.cookie)

    return Response(headers)


def middleware(request):
    if Token.check_user(request.cookie):
        request.user = User.get_user(request.cookie)

    return request


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
    request = Request(data, cookie)

    for url, method, handler in urls:
        received_url = re.match(url, path)
        if received_url is not None and received_url.group(0) == path and method == do_method:
            try:
                request.task_id = int(received_url.group('task_id'))
            except:
                pass

            request = middleware(request)
            return handler(request)


server = HTTPServer(('', 8000), TaskHandler)
server.serve_forever()
