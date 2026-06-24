import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from app.models import Job
from datetime import datetime



BASE_URL = "https://www.myjobmag.com/jobs-by-field/information-technology"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

def scrape_jobs(db: Session, max_pages: int = 5):
    jobs_added = 0

    for page in range(1, max_pages + 1):

        url = BASE_URL if page == 1 else f"{BASE_URL}/{page}"
        print(f"Scraping page {page}: {url}")

        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to fetch page {page}: {e}")
            break

        soup = BeautifulSoup(response.text, "html.parser")

        job_cards = soup.select("ul.job-list > li")

        if not job_cards:
            print(f"No job cards found on page {page} — stopping.")
            break

        for card in job_cards:

            try:
                # Title and URL
                title_tag = card.select_one("h2 a")
                if not title_tag:
                    continue

                title = title_tag.get_text(strip=True)
                job_url = title_tag["href"]

                if not job_url.startswith("http"):
                    job_url = "https://www.myjobmag.com" + job_url

                existing = db.query(Job).filter(Job.url == job_url).first()
                if existing:
                    continue


                company_tag = card.select_one("a[title]")
                company = company_tag["title"].replace(" logo", "").strip() if company_tag else "Unknown"


                location_tag = card.select_one("a[href*='jobs-location']")
                location = location_tag.get_text(strip=True) if location_tag else "Nigeria"


                date_tag = card.select_one("li.date-posted, span.date")
                if not date_tag:

                    meta = card.select_one("ul.job-meta, div.job-meta")
                    date_posted = meta.get_text(strip=True)[:20] if meta else "Not specified"
                else:
                    date_posted = date_tag.get_text(strip=True)


                desc_tag = card.select_one("p, div.job-desc")
                description = desc_tag.get_text(strip=True)[:300] if desc_tag else ""


                job = Job(
                    title=title,
                    company=company,
                    location=location,
                    job_type="Full Time",
                    date_posted=date_posted,
                    description=description,
                    url=job_url,
                    scraped_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                )
                db.add(job)
                db.commit()
                jobs_added += 1
                print(f"  Added: {title} — {company}")

            except Exception as e:
                print(f"Error parsing job card: {e}")
                db.rollback()
                continue

    print(f"Scraping complete. {jobs_added} new jobs added.")
    return jobs_added