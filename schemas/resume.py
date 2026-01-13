from pydantic import BaseModel, Field
from typing import List, Optional


class Resume(BaseModel):
    name: Optional[str] = None
    total_experience_years: Optional[float] = None

    roles: List[str] = Field(
        default_factory=list,
        description="Past or current job titles"
    )

    skills: List[str] = Field(
        default_factory=list
    )

    tools: List[str] = Field(
        default_factory=list
    )

    summary: Optional[str] = Field(
        default=None,
        description="Concise professional summary"
    )
