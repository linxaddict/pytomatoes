from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///db.sqlite3', echo=True)
Base = declarative_base()
