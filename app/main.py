import cgi
import re
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, HTTPServer

from app.authServer import login_page, register_page, login, register, logout
from app.config import env, session
from app.forms import TaskForm
from app.models import Task, Token
from app.response import Response


class TaskHandler(BaseHTTPRequestHandler):
    def set_headers(self, code, header, url, token=None, delete_cookie=None):
        self.send_response(code)
        self.send_header(header, url)

        if token:
            cookie = SimpleCookie()
            cookie['token'] = token
            cookie['token']['expires'] = delete_cookie
            self.send_header('Set-Cookie', cookie.output(header=''))

        self.end_headers()

    def do_GET(self):
        self.handler('get')

    def do_POST(self):
        data = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                'REQUEST_METHOD': 'POST'
            }
        )
        self.handler('post', data)

    def handler(self, method, data=None):
        response = routes(self.path, method, data, SimpleCookie(self.headers.get('Cookie')))

        self.set_headers(*response.headers)
        self.wfile.write(response.data.encode())


def task_list(cookie):
    if cookie and Token.check_user(cookie):
        headers = 200, 'Content-Type', 'text/html'
        data = env.get_template('index.html').render(form=TaskForm(),
                                                     tasks=session.query(Task).filter_by(status=True).all()[::-1],
                                                     done_tasks=session.query(Task).filter_by(status=False).all(),
                                                     current_user=Token.get_user(cookie)
                                                     )

        return Response(headers, data)
    else:
        headers = 302, 'Location', '/login'
        return Response(headers)


def add_task(data, cookie):
    if cookie and Token.check_user(cookie):
        headers = 302, 'Location', '/'

        session.add(Task(data.getvalue('task')))
        session.commit()
    else:
        headers = 302, 'Location', '/login'

    return Response(headers)


def delete_task(task_id, cookie):
    if cookie and Token.check_user(cookie):
        headers = 302, 'Location', '/'
        session.query(Task).get(task_id).delete_task()
    else:
        headers = 302, 'Location', '/login'

    return Response(headers)


def done_task(task_id, cookie):
    if cookie and Token.check_user(cookie):
        headers = 302, 'Location', '/'
        session.query(Task).get(task_id).set_done()
    else:
        headers = 302, 'Location', '/login'

    return Response(headers)


def clear_all(cookie):
    if cookie and Token.check_user(cookie):
        headers = 302, 'Location', '/'
        Task.clear_all()
    else:
        headers = 302, 'Location', '/login'

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

    for url, method, handler in urls:
        received_url = re.match(url, path)

        if received_url is not None and received_url.group(0) == path and method == do_method:
            try:
                task_id = int(received_url.group('task_id'))
            except:
                pass

            if method == 'post':
                return handler(data, cookie)
            if task_id is not None:
                return handler(task_id, cookie)
            return handler(cookie)


server = HTTPServer(('', 8000), TaskHandler)
server.serve_forever()
