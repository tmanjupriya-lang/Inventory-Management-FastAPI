from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from app.models import Base    
from app import models

load_dotenv()

envuser = os.getenv("DB_USER")
envpassword = os.getenv("DB_PASSWORD")

if not envuser or not envpassword:
    raise Exception("Missing DB_USER or DB_PASSWORD in environment variables")

conn_string = f"postgresql://{envuser}:{envpassword}@localhost:5432/fastapi"

engine = create_engine(conn_string)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()