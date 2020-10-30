import cgi
import re
import datetime
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, HTTPServer

from app.authServer import login_page, register_page, login, register
from app.config import env, session
from app.forms import TaskForm
from app.models import Task
from app.response import Response


class TaskHandler(BaseHTTPRequestHandler):
    def set_headers(self, code, header, url):
        self.send_response(code)
        self.send_header(header, url)

        cookie = SimpleCookie()
        cookie['login'] = "some login"
        cookie['password'] = "some password"
        self.send_header("Set-Cookie", cookie.output())

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
        response = routes(self.path, method, data)
        self.set_headers(*response.headers)
        self.wfile.write(response.data.encode())


def task_list():
    headers = 200, 'Content-Type', 'text/html'
    data = env.get_template('index.html').render(form=TaskForm(),
                                                 tasks=session.query(Task).filter_by(status=True).all()[::-1],
                                                 done_tasks=session.query(Task).filter_by(status=False).all(),
                                                 )
    return Response(headers, data)


def add_task(data):
    headers = 302, 'Location', '/'

    session.add(Task(data.getvalue('task')))
    session.commit()

    return Response(headers)


def delete_task(task_id):
    headers = 302, 'Location', '/'
    session.query(Task).get(task_id).delete_task()

    return Response(headers)


def done_task(task_id):
    headers = 302, 'Location', '/'
    session.query(Task).get(task_id).set_done()

    return Response(headers)


def clear_all():
    headers = 302, 'Location', '/'
    Task.clear_all()

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
]


def routes(path, do_method, data):
    task_id = None

    for url, method, handler in urls:
        received_url = re.match(url, path)

        if received_url is not None and received_url.group(0) == path and method == do_method:
            try:
                task_id = int(received_url.group('task_id'))
            except:
                pass

            if method == 'post':
                return handler(data)
            if task_id is not None:
                return handler(task_id)
            return handler()


server = HTTPServer(('', 8000), TaskHandler)
server.serve_forever()
