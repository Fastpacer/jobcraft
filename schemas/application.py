from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Application(BaseModel):
    job_id: Optional[str]
    job_title: str
    company: str

    fit_score: Optional[int] = Field(
        default=None,
        ge=0,
        le=100
    )

    status: str = Field(
        default="discovered",
        description="discovered | applied | rejected | interview"
    )

    outreach_message: Optional[str] = None

    applied_at: Optional[datetime] = None
    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )
