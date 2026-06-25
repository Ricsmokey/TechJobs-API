# TechJobs API

A REST API that scrapes and serves live Nigerian tech job listings from MyJobMag. Built with FastAPI, SQLAlchemy, and BeautifulSoup4. The database updates automatically every 24 hours. 

**Live API:** *https://techjobs-api-2.onrender.com/docs*

---

## Features

- Scrapes live tech job listings from MyJobMag across 5 pages
- Stores jobs in SQLite with deduplication — no duplicate entries on re-scrape
- Automatic daily scraping via APScheduler background job
- Filter jobs by location or role keyword
- Pagination support
- Manual scrape trigger endpoint
- Interactive API docs at `/docs`
- Tested with pytest

---

## Tech Stack

- Framework  - FastAPI
- Database   - SQLite via SQLAlchemy
- Scraping   - BeautifulSoup4, requests
- Testing    - pytest
- Deployment - Render

```
## Endpoints


| GET | `/`                             | Welcome message and endpoint list |
| GET | `/api/jobs/`                    | All jobs (paginated) |
| GET | `/api/jobs/?location=lagos`     | Filter by location |
| GET | `/api/jobs/?role=backend`       | Filter by role keyword |
| GET | `/api/jobs/{id}`                | Single job by ID |
| POST | `/api/jobs/scrape/`            | Manually trigger a fresh scrape |
```

## Run Locally

```bash
git clone https://github.com/Ricsmokey/techjobs-api.git
cd techjobs-api
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```
Then open http://127.0.0.1:8000/docs

## Run Tests

pytest tests/ -v


## Project Structure
```
techjobs-api/
│
├── app/
│ ├── main.py           # FastAPI app, routes, scheduler
│ ├── models.py         # SQLAlchemy Job model
│ ├── schemas.py        # Py​dantic response schemas
│ ├── database.py       # Database connection and session
│ └── scraper.py        # BeautifulSoup scraper logic
├── tests/
│ └── test_jobs.py      # pytest tests
├── requirements.txt
└── README.md
```
## Author

**Akorede Kareem** — [github.com/Ricsmokey](https://github.com/Ricsmokey)
