from sqlalchemy.orm import Session

from src.app.database import SessionLocal


class BaseRepo:
    # Base Resposity GetDB depency similar to the get_db in the FastAPI Documentation.

    def __init__(self):
        self.db: Session = self.get_sess.__next__()

    @property
    def get_sess(self):
        db_sess: Session = SessionLocal()
        try:
            yield db_sess

        except:
            db_sess.rollback()
        finally:
            db_sess.close()
