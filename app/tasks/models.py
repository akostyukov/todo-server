from sqlalchemy import Column, String, Boolean, Integer, ForeignKey

from app.auth.models import User
from app.config import session, Base
from app.decorators import commit_transaction


class Task(Base):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True)
    task = Column(String(50), nullable=False)
    status = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    def __init__(self, task, user_id):
        self.task = task
        self.user_id = user_id

    @commit_transaction
    def add_task(self):
        session.add(self)

    @staticmethod
    @commit_transaction
    def set_done(task_id):
        session.query(Task).get(task_id).status = False

    @staticmethod
    @commit_transaction
    def delete_task(task_id):
        session.delete(session.query(Task).get(task_id))

    @staticmethod
    @commit_transaction
    def clear_all(cookie):
        session.query(Task).filter_by(user_id=User.get_user(cookie).id).delete()
