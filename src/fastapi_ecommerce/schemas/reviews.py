from pydantic import BaseModel, Field


class NewReview(BaseModel):
    comment: str
    grade: int = Field(..., gt=0, le=5)


class UpdateReview(BaseModel):
    comment: str | None
    grade: int | None = Field(..., gt=0, le=5)
