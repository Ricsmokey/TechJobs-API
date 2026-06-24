from sqlalchemy import Column, Integer, String
from app.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, nullable=False)
    job_type = Column(String)
    description = Column(String)
    tags = Column(String)
    url = Column(String, unique=True, nullable=False)
    date_posted = Column(String)
    date_posted = Column(String)
    scraped_at = Column(String)