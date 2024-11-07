from sqlalchemy import Column, Integer, String
from database import Base


class Trip(Base):
    __tablename__ = "trips"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128))
    description = Column(String(256))
    joiner_total_count = Column(Integer)
