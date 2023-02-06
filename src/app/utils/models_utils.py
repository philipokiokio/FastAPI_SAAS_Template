# 3rd party import
from sqlalchemy import TIMESTAMP, Column, Integer, text

# application imports
from src.app.database import Base


class AbstractModel(Base):
    """Base Models

    Args:
        Base (_type_): Inherits Base from SQLAlchemy and specifies columns for inheritance.
    """

    __abstract__ = True

    id = Column(Integer, nullable=False, primary_key=True)
    date_created = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"))
    date_updated = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"))
