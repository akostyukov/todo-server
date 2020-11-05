from jinja2 import Environment, PackageLoader
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

env = Environment(loader=PackageLoader(__name__, 'templates'))
engine = create_engine('sqlite:///data.db')
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

Base.metadata.create_all(engine)
