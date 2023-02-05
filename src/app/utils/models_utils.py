from sqlalchemy import TIMESTAMP, Column, Integer, text

from src.app.database import Base


class AbstractModel(Base):
    __abstract__ = True

    id = Column(Integer, nullable=False, primary_key=True)
    date_created = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"))
    date_updated = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"))
