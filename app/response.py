class Response:
    headers = ()
    data = ''

    def __init__(self, headers, data=''):
        self.headers = headers
        self.data = data


class Request:
    headers = ()
    data = ''
    method = ''
    cookie = None
    user = None
    task_id = None
