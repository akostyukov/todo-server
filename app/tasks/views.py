from app.config import tasks_env, session
from app.auth_decorators import auth, check_match
from app.tasks.forms import TaskForm
from app.auth.models import User, Token
from app.tasks.models import Task
from app.response import Response, RedirectResponse


@auth
def task_list(request):
    headers = [('Content-Type', 'text/html')]
    data = tasks_env.get_template('index.html').render(
        form=TaskForm(),
        tasks=session.query(Task).filter_by(status=True, user_id=request.user.id).all()[::-1],
        done_tasks=session.query(Task).filter_by(status=False, user_id=request.user.id).all(),
        current_user=request.user.login
    )

    return Response(headers, data)


@auth
def add_task(request):
    Task.add_task(Task(request.data.get('task'), request.user.id))
    return RedirectResponse('/')


@auth
@check_match
def delete_task(request):
    Task.delete_task(request.task_id)
    return RedirectResponse('/')


@auth
@check_match
def done_task(request):
    Task.set_done(request.task_id)
    return RedirectResponse('/')


@auth
def clear_all(request):
    Task.clear_all(request.cookie)
    return RedirectResponse('/')


def middleware(request):
    if Token.check_user(request.cookie):
        request.user = User.get_user(request.cookie)

    return request
