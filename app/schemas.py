from pydantic import BaseModel
from typing import Optional


class jobBase(BaseModel):
    title: str
    company: str
    location: str
    job_type: Optional[str] = None
    date_posted: Optional[str] = None
    url: str


class JobResponse(jobBase):
    id: int
    scraped_at: Optional[str] = None

    class config:
        from_attributes = True
