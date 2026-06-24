from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from contextlib import asynccontextmanager
import importlib

BackgroundScheduler = None
try:
    apscheduler = importlib.import_module("apscheduler.schedulers.background")
    BackgroundScheduler = apscheduler.BackgroundScheduler
except ImportError:
    BackgroundScheduler = None

from app.database import engine, get_db, Base
from app.models import Job
from app.schemas import JobResponse
from app import scraper


Base.metadata.create_all(bind=engine)


scheduler = BackgroundScheduler() if BackgroundScheduler is not None else None

def scheduled_scrape():

    from app.database import SessionLocal
    db = SessionLocal()
    try:
        print("Running scheduled scrape...")
        scraper.scrape_jobs(db)
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduled_scrape()

    if scheduler is not None:
        scheduler.add_job(scheduled_scrape, "interval", hours=24)
        scheduler.start()
        print("Scheduler started — scraping every 24 hours.")
    else:
        print("APScheduler unavailable; automatic scraping disabled.")

    yield

    if scheduler is not None:
        scheduler.shutdown()
        print("Scheduler stopped.")


app = FastAPI(
    title="Tech Jobs API",
    description= "Nigerian tech job listings scraped from MyJobMag Nigeria - A REST API that scrapes and serves real tech job listings from MyJobMag Nigeria that refreshes the database automatically every **24 Hours**",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
def root():
    return {
        "message": "Welcome to Tech Jobs API",
        "docs": "/docs",
        "endpoints": {
            "all jobs": "/api/jobs/",
            "filter by location": "/api/jobs/?location=lagos",
            "filter by role": "/api/jobs/?role=backend",
            "single job": "/api/jobs/{id}",
            "manual scrape": "POST /api/jobs/scrape/"
        }
    }

@app.get("/api/jobs/", response_model=List[JobResponse])
def get_jobs(
    location: Optional[str] = Query(None, description="Filter by location e.g. lagos, abuja"),
    role: Optional[str] = Query(None, description="Filter by role keyword e.g. backend, python"),
    limit: int = Query(20, description="Number of results to return"),
    skip: int = Query(0, description="Number of results to skip"),
    db: Session = Depends(get_db)
):
    query = db.query(Job)

    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))

    if role:
        query = query.filter(Job.title.ilike(f"%{role}%"))

    jobs = query.offset(skip).limit(limit).all()

    if not jobs:
        raise HTTPException(status_code=404, detail="No jobs found matching your filters")

    return jobs

@app.get("/api/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail=f"Job with id {job_id} not found")

    return job

@app.post("/api/jobs/scrape/")
def trigger_scrape(db: Session = Depends(get_db)):
    """Manually trigger a fresh scrape without waiting 24 hours."""
    jobs_added = scraper.scrape_jobs(db)
    return {
        "message": "Scrape complete",
        "new_jobs_added": jobs_added
    }