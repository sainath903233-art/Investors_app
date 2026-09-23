# backend/database.py
# Like db.js in Node — connects to PostgreSQL

import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load .env that sits in the SAME folder as this file (backend/)
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        f"\n\nDATABASE_URL is None!\n"
        f"   Looking for .env at: {env_path}\n"
        f"   Make sure that file exists and has:\n"
        f"   DATABASE_URL=postgresql://investuser:mypassword123@localhost:5432/investsmart\n"
    )

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    # Opens a DB connection per request, closes it after (like middleware)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
