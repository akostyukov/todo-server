class Response:
    code = 200
    headers = ()
    data = ''

    def __init__(self, headers, data='', code=200):
        self.headers = headers
        self.data = data


class Request:
    data = ''
    cookie = ''
    task_id = ''
    user = None

    def __init__(self, data, cookie):
        self.data = data
        self.cookie = cookie
