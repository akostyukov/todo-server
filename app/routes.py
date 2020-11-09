import re

from app.request import Request
from app.tasks.views import middleware


def routes(path, do_method, data, cookie):
    request = Request(data, cookie)

    from app.urls import urls

    for url, method, handler in urls:
        received_url = re.match(url, path)
        if received_url is not None and received_url.group(0) == path and method == do_method:
            try:
                request.task_id = int(received_url.group('task_id'))
            except:
                pass

            request = middleware(request)
            return handler(request)
