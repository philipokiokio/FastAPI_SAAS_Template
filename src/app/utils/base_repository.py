# 3rd party imports
from sqlalchemy.orm import Session

from src.app.config import test_status

# application import
from src.app.database import SessionLocal, get_test_db


class BaseRepo:
    # Base Resposity GetDB depency similar to the get_db in the FastAPI Documentation.
    """
    Base ORM for abstracting Database calls.

    """

    def __init__(self):
        self.db: Session = self.__testing_module__

    @property
    def __testing_module__(self):
        db_sess = self.get_sess.__next__()

        if test_status.should_test is True:
            return get_test_db().__next__()
        print("Database is Ready!")

        return db_sess

    @property
    def get_sess(self):
        """Get Session

        Yields:
            _type_: DB Session.
        Handles exception via rollback and closes connection upon DB tranzaction completed
        """

        db_sess = SessionLocal()

        try:
            yield db_sess

        except:
            db_sess.rollback()
        finally:
            db_sess.close()
        SessionLocal.remove()
