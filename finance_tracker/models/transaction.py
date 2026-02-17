from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import List, Optional,Literal

class TransactionCreate(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    description: Optional[str] = Field(default="", max_length=500)
    amount: float = Field(gt=0)
    type: Literal["income", "expense"]
    category: str
    date: datetime
    tags: List[str] = []

    @field_validator("category")
    @classmethod
    def validate_category(cls, v):
        if not v.strip():
            raise ValueError("Category empty")
        return v.lower()

    @field_validator("date")
    @classmethod
    def validate_date(cls, v):
        if v > datetime.now(timezone.utc):
            raise ValueError("Future date not allowed")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v):
        if len(v) > 10:
            raise ValueError("Max 10 tags")
        for t in v:
            if len(t) > 30:
                raise ValueError("Tag too long")
        return v

class TransactionUpdate(BaseModel):
    class TransactionUpdate(BaseModel):
        title: Optional[str]
        description: Optional[str]
        amount: Optional[float]
        type: Optional[str]
        category: Optional[str]
        date: Optional[datetime]
        tags: Optional[List[str]]
