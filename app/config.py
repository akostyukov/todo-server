from jinja2 import Environment, PackageLoader
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

env = Environment(loader=PackageLoader(__name__, 'templates'))
engine = create_engine('sqlite:///data.db')
Session = sessionmaker(bind=engine)
session = Session()

from app.models import Base

Base.metadata.create_all(engine)
