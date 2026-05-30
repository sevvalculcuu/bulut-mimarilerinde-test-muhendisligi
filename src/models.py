import datetime
from sqlalchemy import Column, Integer, String, DateTime
from src.database import Base


class QRCodeModel(Base):
    __tablename__ = "qrcodes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, index=True, nullable=False)
    target_url = Column(String, nullable=False)
    s3_key = Column(String, unique=True, nullable=False)
    s3_url = Column(String, nullable=False)
    scan_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
