import secrets
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from app.config import session, Base
from app.decorators import commit_transaction


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    login = Column(String(15), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    tasks = relationship('Task')
    tokens = relationship('Token')

    def __init__(self, login, password):
        self.login = login
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return True if check_password_hash(self.password, password) else False

    @staticmethod
    def get_user(cookie):
        token = session.query(Token).filter_by(token=cookie['token'].value).first()
        user = session.query(User).filter_by(id=token.user_id).first()
        return user


class Token(Base):
    __tablename__ = 'token'

    id = Column(Integer, primary_key=True)
    token = Column(String(100), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    def __init__(self, user_id):
        self.token = secrets.token_urlsafe(32)
        self.user_id = user_id

    @staticmethod
    @commit_transaction
    def delete_session(token):
        token = session.query(Token).filter_by(token=token).first()
        session.delete(token)

    @staticmethod
    def check_user(cookie):
        try:
            token = session.query(Token).filter_by(token=cookie['token'].value).first()
            user = session.query(User).filter_by(id=token.user_id).first()

            if user:
                return True
        except:
            return False

    @staticmethod
    def clear_all():
        session.query(Token).delete()
        session.commit()
