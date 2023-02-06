from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# application import config.
from src.app.config import db_settings

# DB URL for connection
SQLALCHEMY_DATABASE_URL = f"postgresql://{db_settings.username}:{db_settings.password}@{db_settings.hostname}:{db_settings.port}/{db_settings.name}"

# Creating DB engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Creating and Managing session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

print("Database is Ready!")

# Domain Modelling Dependency
Base = declarative_base()
