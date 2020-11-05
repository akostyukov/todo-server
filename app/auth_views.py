from app.config import env, session
from app.forms import UserForm
from app.models import User, Token
from app.response_and_request import Response


def login_page(request):
    if not request.cookie:
        headers = 200, 'Content-Type', 'text/html'
        data = env.get_template('login.html').render(form=UserForm())
    elif not Token.check_user(request.cookie):
        headers = 302, 'Location', '/login', ' ', 0
        data = ''
    else:
        headers = 302, 'Location', '/'
        data = ''

    return Response(headers, data)


def register_page(request):
    if not request.cookie:
        headers = 200, 'Content-Type', 'text/html'
        data = env.get_template('register.html').render(form=UserForm())
    else:
        headers = 302, 'Location', '/'
        data = ''

    return Response(headers, data)


def login(request):
    headers = [302, 'Location', '/']

    if not request.cookie:
        user = session.query(User).filter_by(login=request.data.get('login')).first()

        if not user or not user.check_password(request.data.get('password')):
            headers[2] = '/login'
        else:
            token = Token(user.id)
            session.add(token)
            session.commit()
            headers.append(token.token)

    return Response(headers)


def register(request):
    headers = 302, 'Location', '/login'

    user = session.query(User).filter_by(login=request.data.get('login')).first()

    if not user:
        session.add(User(request.data.get('login'), request.data.get('password')))
        session.commit()
    else:
        headers = headers = 302, 'Location', '/register'

    return Response(headers)


def logout(request):
    Token.delete_session(request.cookie['token'].value)
    headers = 302, 'Location', '/login', ' ', 0

    return Response(headers)
