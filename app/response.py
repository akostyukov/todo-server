class Response:
    headers = ()
    data = ''

    def __init__(self, headers, data=''):
        self.headers = headers
        self.data = data
