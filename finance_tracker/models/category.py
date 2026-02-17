from pydantic import BaseModel
from typing import Literal


class CategoryCreate(BaseModel):
    name: str
    type: Literal["income", "expense", "both"]
    description: str = ""


class CategoryUpdate(BaseModel):
    type: str | None = None
    description: str | None = None
