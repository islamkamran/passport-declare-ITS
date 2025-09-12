from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

# PG_DATABASE_URI = os.getenv("DATABASE_URL_PG")
SQL_DATABASE_URI = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@indus-digital-projects.cfu6suc24hx8.ap-south-1.rds.amazonaws.com/passportdeclare"
print(f"the URI: {SQL_DATABASE_URI}")
engine = create_engine(
    SQL_DATABASE_URI,
    # connect_args={"check_same_thread": True}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DBContext:
    def __init__(self):
        self.db = SessionLocal()

    def __enter__(self):
        return self.db

    def __exit__(self, et, ev, traceback):
        self.db.close()
