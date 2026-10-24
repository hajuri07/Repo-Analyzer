from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker , declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL  = os.getenv("DATABASE_URL")

engine  =  create_engine(DATABASE_URL)
SessionLocal  = sessionmaker(bind = engine)
Base = declarative_base()
def get_db():
    db = SessionLocal ()
    try:
        yield db
    finally:
        db.close()


def ensure_review_columns():
    """Small forward-only migration for hackathon deployments without Alembic."""
    inspector = inspect(engine)
    if "reviews" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("reviews")}
    with engine.begin() as connection:
        if "metrics" not in columns:
            connection.execute(text("ALTER TABLE reviews ADD COLUMN metrics JSON"))
        if "roadmap" not in columns:
            connection.execute(text("ALTER TABLE reviews ADD COLUMN roadmap JSON"))
