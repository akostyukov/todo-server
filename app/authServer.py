from app.config import env, session
from app.forms import UserForm
from app.models import User, Token
from app.response import Response


def login_page(cookie):
    if not cookie:
        headers = 200, 'Content-Type', 'text/html'
        data = env.get_template('login.html').render(form=UserForm())
    elif not Token.check_user(cookie):
        headers = 302, 'Location', '/login', ' ', 0
        data = ''
    else:
        headers = 302, 'Location', '/'
        data = ''

    return Response(headers, data)


def register_page(cookie):
    if not cookie:
        headers = 200, 'Content-Type', 'text/html'
        data = env.get_template('register.html').render(form=UserForm())
    else:
        headers = 302, 'Location', '/'
        data = ''

    return Response(headers, data)


def login(data, cookie):
    headers = [302, 'Location', '/']

    if not cookie:
        user = session.query(User).filter_by(login=data.get('login')[0]).first()

        if not user or not user.check_password(data.get('password')[0]):
            headers[2] = '/login'
        else:
            token = Token(user.id)
            session.add(token)
            session.commit()
            headers.append(token.token)

    return Response(headers)


def register(data, cookie):
    headers = 302, 'Location', '/login'

    user = session.query(User).filter_by(login=data.get('login')[0]).first()

    if not user:
        session.add(User(data.get('login')[0], data.get('password')[0]))
        session.commit()
    else:
        headers = headers = 302, 'Location', '/register'

    return Response(headers)


def logout(cookie):
    Token.delete_session(cookie['token'].value)
    headers = 302, 'Location', '/login', ' ', 0

    return Response(headers)
