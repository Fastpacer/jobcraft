from pydantic import BaseModel, Field
from typing import Optional, List


class Job(BaseModel):
    job_id: Optional[str] = Field(
        default=None,
        description="Unique identifier from the job source"
    )

    title: str
    company: str

    location: Optional[str] = None
    employment_type: Optional[str] = None  # full-time, intern, contract

    description: str

    skills: List[str] = Field(
        default_factory=list,
        description="Extracted or inferred skills from job description"
    )

    source: Optional[str] = Field(
        default=None,
        description="LinkedIn, Indeed, Company Site, etc."
    )

    url: Optional[str] = None
