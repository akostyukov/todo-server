from app.config import env, session
from app.forms import UserForm
from app.models import User
from app.response import Response
from http import cookies


def login_page():
    headers = 200, 'Content-Type', 'text/html'
    data = env.get_template('login.html').render(form=UserForm(), users=session.query(User).all())
    return Response(headers, data)


def register_page():
    headers = 200, 'Content-Type', 'text/html'
    data = env.get_template('register.html').render(form=UserForm())
    return Response(headers, data)


def login(data):
    headers = 302, 'Location', '/'
    return Response(headers)


def register(data):
    headers = 302, 'Location', '/login'

    session.add(User(data.getvalue('login'), data.getvalue('password')))
    session.commit()
    return Response(headers)
