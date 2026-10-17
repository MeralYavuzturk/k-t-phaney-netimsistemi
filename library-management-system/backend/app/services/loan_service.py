from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.models.book import Book
from app.models.loan import Loan, LoanStatus
from app.models.student import Student


def sync_overdue_status(db: Session) -> None:
    now = datetime.utcnow()
    active = db.query(Loan).filter(Loan.status == LoanStatus.ACTIVE, Loan.due_date < now).all()
    for loan in active:
        loan.status = LoanStatus.OVERDUE
    if active:
        db.commit()


def borrow_book(db: Session, student: Student, book_id: int) -> Loan:
    sync_overdue_status(db)
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kitap bulunamadı")
    if book.available_copies < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Kitap stokta yok")

    open_loans = (
        db.query(Loan)
        .filter(
            Loan.student_id == student.id,
            Loan.status.in_([LoanStatus.ACTIVE, LoanStatus.OVERDUE]),
        )
        .count()
    )
    if open_loans >= 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="En fazla 5 aktif ödünç alabilirsiniz")

    existing = (
        db.query(Loan)
        .filter(
            Loan.student_id == student.id,
            Loan.book_id == book_id,
            Loan.status.in_([LoanStatus.ACTIVE, LoanStatus.OVERDUE]),
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu kitabı zaten ödünç aldınız")

    due = datetime.utcnow() + timedelta(days=settings.loan_days_default)
    loan = Loan(student_id=student.id, book_id=book.id, due_date=due, status=LoanStatus.ACTIVE)
    book.available_copies -= 1
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


def return_book(db: Session, student: Student, loan_id: int) -> Loan:
    loan = db.get(Loan, loan_id)
    if not loan or loan.student_id != student.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ödünç kaydı bulunamadı")
    if loan.status == LoanStatus.RETURNED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Kitap zaten iade edilmiş")

    book = db.get(Book, loan.book_id)
    if book:
        book.available_copies = min(book.available_copies + 1, book.total_copies)

    loan.returned_at = datetime.utcnow()
    loan.status = LoanStatus.RETURNED
    db.commit()
    db.refresh(loan)
    return loan


def list_overdue(db: Session) -> list[dict]:
    sync_overdue_status(db)
    now = datetime.utcnow()
    rows = (
        db.query(Loan)
        .filter(Loan.status.in_([LoanStatus.ACTIVE, LoanStatus.OVERDUE]), Loan.due_date < now)
        .all()
    )
    result = []
    for loan in rows:
        loan.status = LoanStatus.OVERDUE
        days = (now - loan.due_date).days
        result.append(
            {
                "loan_id": loan.id,
                "student_number": loan.student.student_number,
                "student_name": loan.student.full_name,
                "student_email": loan.student.email,
                "book_title": loan.book.title,
                "isbn": loan.book.isbn,
                "due_date": loan.due_date,
                "days_overdue": max(days, 1),
            }
        )
    db.commit()
    return result
