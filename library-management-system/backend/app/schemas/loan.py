from datetime import datetime

from pydantic import BaseModel

from app.models.loan import LoanStatus


class LoanCreate(BaseModel):
    book_id: int


class LoanRead(BaseModel):
    id: int
    student_id: int
    book_id: int
    borrowed_at: datetime
    due_date: datetime
    returned_at: datetime | None
    status: LoanStatus
    renewal_count: int
    book_title: str | None = None
    student_name: str | None = None

    model_config = {"from_attributes": True}


class OverdueReportItem(BaseModel):
    loan_id: int
    student_number: str
    student_name: str
    student_email: str
    book_title: str
    isbn: str
    due_date: datetime
    days_overdue: int
