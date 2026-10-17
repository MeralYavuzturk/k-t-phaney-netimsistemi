from datetime import datetime

from pydantic import BaseModel, Field


class BookBase(BaseModel):
    isbn: str = Field(min_length=10, max_length=20)
    title: str
    author: str
    category: str | None = None
    description: str | None = None
    total_copies: int = Field(ge=1, default=1)


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    category: str | None = None
    description: str | None = None
    total_copies: int | None = Field(default=None, ge=0)


class BookRead(BookBase):
    id: int
    available_copies: int
    created_at: datetime

    model_config = {"from_attributes": True}
