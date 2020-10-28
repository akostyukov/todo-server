import cgi
from http.server import BaseHTTPRequestHandler, HTTPServer

from app.config import env, session
from app.decorators import commit_transaction
from app.forms import TaskForm
from app.models import Task
import re


class TaskHandler(BaseHTTPRequestHandler):
    def set_headers(self, code, header, url):
        self.send_response(code)
        self.send_header(header, url)
        self.end_headers()

    def do_GET(self):
        response = routes(self.path)

        self.set_headers(*response.headers)
        self.wfile.write(response.data.encode())

    @commit_transaction
    def do_POST(self):
        self.set_headers(303, 'Location', '/')

        data = cgi.FieldStorage(
            fp=self.rfile,
            environ={
                'REQUEST_METHOD': 'POST'
            }
        )

        session.add(Task(data.getvalue('task')))


class Response:
    headers = ()
    data = ''

    def task_list(self):
        self.headers = 200, 'Content-Type', 'text/html'
        self.data = (
            env.get_template('index.html').render(form=TaskForm(),
                                                  tasks=session.query(Task).filter_by(status=True).all()[::-1],
                                                  done_tasks=session.query(Task).filter_by(status=False).all())
        )
        return self

    def delete_task(self, task_id):
        self.headers = 303, 'Location', '/'
        session.query(Task).get(task_id).delete_task()

        return self

    def done_task(self, task_id):
        self.headers = 303, 'Location', '/'
        session.query(Task).get(task_id).set_done()

        return self

    def clear_all(self):
        self.headers = 303, 'Location', '/'
        Task.clear_all()

        return self


def routes(path):
    task_id = re.findall(r'/\w+/(\d+)', path)

    if path.startswith('/delete'):
        return Response().delete_task(task_id)
    elif path.startswith('/done'):
        return Response().done_task(task_id)
    elif path.startswith('/clear'):
        return Response().clear_all()
    else:
        return Response().task_list()


server = HTTPServer(('', 8000), TaskHandler)
server.serve_forever()
