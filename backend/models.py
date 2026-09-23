# backend/models.py
# Like a Sequelize model — defines the users table

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    full_name       = Column(String(100), nullable=False)
    email           = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    risk_profile    = Column(String(20), default="moderate")   # conservative / moderate / aggressive
    watchlist       = Column(Text, default="")                  # comma-separated: "RELIANCE,TCS"
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
