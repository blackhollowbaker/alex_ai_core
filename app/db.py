# app/db.py

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = "sqlite:///./qbo_tokens.db"  # For now, use SQLite

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()

class QBOToken(Base):
    __tablename__ = "qbo_tokens"
    id = Column(Integer, primary_key=True, index=True)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    realm_id = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)

Base.metadata.create_all(bind=engine)

def get_latest_credentials():
    # In production, you'd fetch this from a real database.
    return {
        "access_token": "YOUR_ACCESS_TOKEN",
        "realm_id": "YOUR_REALM_ID"
    }
