from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from app.config import session
from app.decorators import commit_transaction

Base = declarative_base()


class Task(Base):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True)
    task = Column(String(50), nullable=False)
    status = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    def __init__(self, task):
        self.task = task
        self.user_id = 1

    @commit_transaction
    def set_done(self):
        self.status = False

    @commit_transaction
    def delete_task(self):
        session.delete(session.query(Task).get(self.id))

    @staticmethod
    def clear_all():
        session.query(Task).delete()
        session.commit()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    login = Column(String(15), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    tasks = relationship('Task')

    def __init__(self, login, password):
        self.login = login
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return True if check_password_hash(self.password, password) else False
