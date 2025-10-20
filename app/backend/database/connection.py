from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

from app.backend.config import get_settings

# Resolve default SQLite database path relative to backend directory
BACKEND_DIR = Path(__file__).parent.parent
DEFAULT_DATABASE_PATH = BACKEND_DIR / "hedge_fund.db"

settings = get_settings()

# Allow overriding database via environment variable
DATABASE_URL = settings.database_url or f"sqlite:///{DEFAULT_DATABASE_PATH}"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 