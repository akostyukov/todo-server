from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base

from app.config import session
from app.decorators import commit_transaction

Base = declarative_base()


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    task = Column(String(50), nullable=False)
    status = Column(Boolean, default=True)

    def __init__(self, task):
        self.task = task

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
