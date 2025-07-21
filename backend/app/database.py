# database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./receipts.db"

# create_engine is needed for SQLAlchemy to connect to the database.
# The `connect_args` are needed only for SQLite to allow multi-threaded interaction.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Each instance of the SessionLocal class will be a new database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our models to inherit from.
Base = declarative_base()

# Dependency to get a DB session for each request and close it afterward.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()