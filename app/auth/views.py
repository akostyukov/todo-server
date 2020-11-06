from http.cookies import SimpleCookie

from app.config import auth_env, session
from app.auth.forms import UserForm
from app.auth.models import User, Token
from app.response_and_request import Response, RedirectResponse


def login_page(request):
    if not request.cookie:
        headers = [('Content-Type', 'text/html')]
        data = auth_env.get_template('login.html').render(form=UserForm())
    elif not Token.check_user(request.cookie):
        headers = [('Location', '/login'), delete_cookie()]
        data = ''
    else:
        headers = [('Location', '/')]
        data = ''

    return Response(headers, data)


def register_page(request):
    if not request.cookie:
        headers = [('Content-Type', 'text/html')]
        data = auth_env.get_template('register.html').render(form=UserForm())
    else:
        return RedirectResponse('/login')

    return Response(headers, data)


def login(request):
    headers = [('Location', '/')]

    if not request.cookie:
        user = session.query(User).filter_by(login=request.data.get('login')).first()

        if not user or not user.check_password(request.data.get('password')):
            return RedirectResponse('/login')
        else:
            token = Token(user.id)
            session.add(token)
            session.commit()

            cookie = SimpleCookie()
            cookie['token'] = token.token
            headers.append(('Set-cookie', cookie.output(header='')))

    return Response(headers)


def register(request):
    headers = [('Location', '/login')]

    user = session.query(User).filter_by(login=request.data.get('login')).first()

    if not user:
        session.add(User(request.data.get('login'), request.data.get('password')))
        session.commit()
    else:
        return RedirectResponse('/register')

    return Response(headers)


def logout(request):
    Token.delete_session(request.cookie['token'].value)
    headers = [('Location', '/login'), delete_cookie()]

    return Response(headers)


def delete_cookie():
    cookie = SimpleCookie()
    cookie['token'] = ' '
    cookie['token']['expires'] = 0

    return 'Set-Cookie', cookie.output(header='')
