from pydantic import BaseModel


class NewCategory(BaseModel):
    name: str
    parent_id: int | None = None
