class Response:
    code = 200
    headers = ()
    data = ''

    def __init__(self, headers, data='', token=''):
        self.headers = headers
        self.data = data
        self.token = token

        if self.headers[0] != 'Content-Type':
            self.code = 302


class RedirectResponse(Response):
    code = 302

    def __init__(self, url):
        self.headers = [('Location', url)]
