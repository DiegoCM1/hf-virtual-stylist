"""Database configuration for SQLAlchemy sessions and models."""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings


SQLALCHEMY_DATABASE_URL = settings.database_url

# Create the SQLAlchemy engine that will be used for interacting with the database.
engine = create_engine(SQLALCHEMY_DATABASE_URL, future=True)

# Configure a session factory that will generate new Session objects for each request.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

# Base class for all ORM models within the project.
Base = declarative_base()
