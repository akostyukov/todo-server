from http.cookies import SimpleCookie
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib import parse

from app.routes import routes


class TaskHandler(BaseHTTPRequestHandler):
    def set_headers(self, response):
        for keyword, value in response.headers:
            self.send_response(response.code)
            self.send_header(keyword, value)
        self.end_headers()

    def do_GET(self):
        self.handler('get')

    def do_POST(self):
        post_data = parse.parse_qs(self.rfile.read(int(self.headers['Content-Length'])).decode())
        data = {key: post_data.get(key)[0] for key in post_data}
        self.handler('post', data)

    def handler(self, method, data=None):
        response = routes(self.path, method, data, SimpleCookie(self.headers.get('Cookie')))

        self.set_headers(response)
        self.wfile.write(response.data.encode())


server = HTTPServer(('', 8000), TaskHandler)
server.serve_forever()
