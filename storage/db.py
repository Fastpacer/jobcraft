from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    DateTime,
    Text
)
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

from config.settings import settings
from schemas.application import Application

# SQLAlchemy base
Base = declarative_base()


class ApplicationORM(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, autoincrement=True)

    job_id = Column(String, nullable=True)
    job_title = Column(String, nullable=False)
    company = Column(String, nullable=False)

    fit_score = Column(Integer, nullable=True)
    status = Column(String, default="discovered")

    outreach_message = Column(Text, nullable=True)

    applied_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Engine & session
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True
)


def init_db() -> None:
    """Create tables if they don't exist."""
    Base.metadata.create_all(bind=engine)


def save_application(app: Application) -> None:
    """Persist an Application schema to the database."""
    session = SessionLocal()
    try:
        orm_obj = ApplicationORM(
            job_id=app.job_id,
            job_title=app.job_title,
            company=app.company,
            fit_score=app.fit_score,
            status=app.status,
            outreach_message=app.outreach_message,
            applied_at=app.applied_at,
            created_at=app.created_at,
        )
        session.add(orm_obj)
        session.commit()
    finally:
        session.close()


def list_applications():
    """Return all stored applications."""
    session = SessionLocal()
    try:
        return session.query(ApplicationORM).all()
    finally:
        session.close()