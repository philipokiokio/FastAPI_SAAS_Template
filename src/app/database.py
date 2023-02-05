from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.app.config import db_settings

SQLALCHEMY_DATABASE_URL = f"postgresql://{db_settings.username}:{db_settings.password}@{db_settings.hostname}:{db_settings.port}/{db_settings.name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

print("Database is Ready!")


Base = declarative_base()
