from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
try:
    from backend.config import settings
except (ImportError, ModuleNotFoundError):
    from config import settings

# SQLite connection configuration with multithreading support
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """FastAPI dependency that provides a transactional database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
