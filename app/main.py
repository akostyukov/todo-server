import cgi
import re
from http.server import BaseHTTPRequestHandler, HTTPServer

from app.config import env, session
from app.forms import TaskForm
from app.models import Task


class TaskHandler(BaseHTTPRequestHandler):
    def set_headers(self, code, header, url):
        self.send_response(code)
        self.send_header(header, url)
        self.end_headers()

    def do_GET(self):
        response = routes_get(self.path)

        self.set_headers(*response.headers)
        self.wfile.write(response.data.encode())

    def do_POST(self):
        data = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                'REQUEST_METHOD': 'POST'
            }
        )

        response = routes_post(self.path, data)
        self.set_headers(*response.headers)
        self.wfile.write(response.data.encode())


class Response:
    headers = ()
    data = ''

    def __init__(self, headers, data=''):
        self.headers = headers
        self.data = data


def task_list():
    headers = 200, 'Content-Type', 'text/html'
    data = env.get_template('index.html').render(form=TaskForm(),
                                                 tasks=session.query(Task).filter_by(status=True).all()[::-1],
                                                 done_tasks=session.query(Task).filter_by(status=False).all()
                                                 )
    return Response(headers, data)


def add_task(data):
    headers = 303, 'Location', '/'

    session.add(Task(data.getvalue('task')))
    session.commit()

    return Response(headers)


def delete_task(task_id):
    headers = 303, 'Location', '/'
    session.query(Task).get(task_id).delete_task()

    return Response(headers)


def done_task(task_id):
    headers = 303, 'Location', '/'
    session.query(Task).get(task_id).set_done()

    return Response(headers)


def clear_all():
    headers = 303, 'Location', '/'
    Task.clear_all()

    return Response(headers)


def routes_get(path):
    task_id = re.findall(r'/\w+/(\d+)', path)

    if path.startswith('/delete'):
        return delete_task(task_id)
    elif path.startswith('/done'):
        return done_task(task_id)
    elif path.startswith('/clear'):
        return clear_all()
    else:
        return task_list()


def routes_post(path, data):
    if path.startswith('/'):
        return add_task(data)


server = HTTPServer(('', 8000), TaskHandler)
server.serve_forever()
