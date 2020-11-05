class Response:
    headers = ()
    data = ''

    def __init__(self, headers, data=''):
        self.headers = headers
        self.data = data


class Request:
    data = ''
    cookie = ''
    task_id = ''
    user = None
    task = None

    def __init__(self, data, cookie):
        self.data = data
        self.cookie = cookie
