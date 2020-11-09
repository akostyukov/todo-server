class Request:
    data = ''
    cookie = ''
    task_id = ''
    user = None

    def __init__(self, data, cookie):
        self.data = data
        self.cookie = cookie
