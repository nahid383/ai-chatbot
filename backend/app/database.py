"""
SQLAlchemy setup: the engine (connection to Postgres), session factory,
and the declarative Base that all models inherit from.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# pool_pre_ping=True: checks a connection is alive before using it.
# Prevents "server closed the connection unexpectedly" errors after
# the DB has been idle (common on free-tier hosted Postgres).

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency: gives each request its own DB session, and
    guarantees it's closed afterward - even if the request raises
    an exception. This pattern (yield, then cleanup) is standard
    across FastAPI dependencies that manage a resource.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
