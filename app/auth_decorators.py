from app.config import session
from app.auth.models import Token
from app.tasks.models import Task
from app.response_and_request import Response


def auth(func):
    def wrapped(request):
        if Token.check_user(request.cookie):
            return func(request)
        else:
            headers = 302, 'Location', '/login'
            return Response(headers)

    return wrapped


def check_match(func):
    def wrapped(request):
        if request.user.id == session.query(Task).get(request.task_id).user_id:
            return func(request)
        else:
            headers = 403, 'Location', '/'
            return Response(headers)

    return wrapped
