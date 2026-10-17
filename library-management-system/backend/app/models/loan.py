import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.book import Book
    from app.models.student import Student


class LoanStatus(str, enum.Enum):
    ACTIVE = "active"
    RETURNED = "returned"
    OVERDUE = "overdue"


class Loan(Base):
    """Ödünç işlemi — Öğrenci ile Kitap arasındaki ilişkiyi somutlaştırır."""

    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), index=True)
    borrowed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    due_date: Mapped[datetime] = mapped_column(DateTime)
    returned_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[LoanStatus] = mapped_column(Enum(LoanStatus), default=LoanStatus.ACTIVE)
    renewal_count: Mapped[int] = mapped_column(Integer, default=0)

    student: Mapped["Student"] = relationship("Student", back_populates="loans")
    book: Mapped["Book"] = relationship("Book", back_populates="loans")
