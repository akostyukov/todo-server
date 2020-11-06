from jinja2 import Environment, PackageLoader
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

auth_env = Environment(loader=PackageLoader('app.auth', 'templates'))
tasks_env = Environment(loader=PackageLoader('app.tasks', 'templates'))
engine = create_engine('sqlite:///data.db')
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

from app.tasks.models import Task
from app.auth.models import User, Token

Base.metadata.create_all(engine)
