# 3rd party imports
from sqlalchemy.orm import Session

# application import
from src.app.database import SessionLocal


class BaseRepo:
    # Base Resposity GetDB depency similar to the get_db in the FastAPI Documentation.
    """
    Base ORM for abstracting Database calls.

    """

    def __init__(self):
        self.db: Session = self.get_sess.__next__()

    @property
    def get_sess(self):
        """Get Session

        Yields:
            _type_: DB Session.
        Handles exception via rollback and closes connection upon DB tranzaction completed
        """
        db_sess: Session = SessionLocal()
        try:
            yield db_sess

        except:
            db_sess.rollback()
        finally:
            db_sess.close()
