from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Create the database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,           # Logs SQL queries in debug mode
    pool_pre_ping=True,            # Checks connection health before using
    pool_size=10,                  # Number of connections in pool
    max_overflow=20                # Extra connections allowed beyond pool_size
)

# Session factory — used to create database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all SQLAlchemy models
Base = declarative_base()


def get_db():
    """
    Dependency function that provides a database session per request.
    Automatically closes the session when the request is done.
    Used via FastAPI's Depends() system.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()