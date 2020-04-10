from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from settings import Settings

settings = Settings()

engine = create_engine('sqlite:///{0}'.format(settings.local_db_name))
Session = sessionmaker(bind=engine)
Base = declarative_base()
