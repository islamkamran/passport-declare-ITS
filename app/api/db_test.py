from fastapi import FastAPI, HTTPException, APIRouter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create the database engine
SQL_DATABASE_URI = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@indus-digital-projects.cfu6suc24hx8.ap-south-1.rds.amazonaws.com/passportdeclare"
engine = create_engine(SQL_DATABASE_URI)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

router = APIRouter()

# Test database connection endpoint
@router.get("/test-db-connection")
def test_db_connection():
    try:
        # Attempt to connect to the database
        connection = engine.connect()
        connection.close()
        return {"message": "Database connection successful!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")