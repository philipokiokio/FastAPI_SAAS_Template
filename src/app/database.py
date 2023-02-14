from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

# application import config.
from src.app.config import db_settings

# DB URL for connection
SQLALCHEMY_DATABASE_URL = f"postgresql://{db_settings.username}:{db_settings.password}@{db_settings.hostname}:{db_settings.port}/{db_settings.name}"

# Creating DB engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Creating and Managing session.
SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocal = scoped_session(SessionFactory)
print("Database is Ready!")

# Domain Modelling Dependency
Base = declarative_base()


TEST_SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL + "_test"
test_engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL)
TestSessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=test_engine)
TestSessionLocal = scoped_session(TestSessionLocal)


def get_test_db():
    print("Test Database is Ready!")

    try:
        test_db = TestSessionLocal()

        yield test_db
    # except:
    #     test_db.rollback()
    finally:
        test_db.close()
        print(True)
    TestSessionLocal.remove()
