from http.cookies import SimpleCookie

from app.config import env, session
from app.forms import UserForm
from app.models import User, Token
from app.response import Response


def login_page(cookie):
    headers = 200, 'Content-Type', 'text/html'
    data = env.get_template('login.html').render(form=UserForm(),
                                                 users=session.query(User).all(),
                                                 tokens=session.query(Token).all())
    return Response(headers, data)


def register_page(cookie):
    headers = 200, 'Content-Type', 'text/html'
    data = env.get_template('register.html').render(form=UserForm())
    return Response(headers, data)


def login(data, cookie):
    headers = [302, 'Location', '/']

    if not cookie:
        user = session.query(User).filter_by(login=data.getvalue('login')).first()

        if not user or not user.check_password(data.getvalue('password')):
            headers[2] = '/login'
        else:
            token = Token(user.id)
            session.add(token)
            session.commit()
            headers.append(token.token)

    return Response(headers)


def register(data, cookie):
    headers = 302, 'Location', '/login'

    session.add(User(data.getvalue('login'), data.getvalue('password')))
    session.commit()
    return Response(headers)


def logout(cookie):
    Token.delete_session(cookie['token'].value)
    headers = 302, 'Location', '/login', ' ', 0

    return Response(headers)
