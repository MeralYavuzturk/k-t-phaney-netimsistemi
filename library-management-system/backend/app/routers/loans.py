from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.admin import Admin
from app.models.loan import Loan
from app.models.student import Student
from app.schemas.loan import LoanCreate, LoanRead, OverdueReportItem
from app.security import require_admin, require_student
from app.services import loan_service

router = APIRouter(prefix="/loans", tags=["Ödünç İşlemleri"])


def _to_loan_read(loan: Loan) -> LoanRead:
    return LoanRead(
        id=loan.id,
        student_id=loan.student_id,
        book_id=loan.book_id,
        borrowed_at=loan.borrowed_at,
        due_date=loan.due_date,
        returned_at=loan.returned_at,
        status=loan.status,
        renewal_count=loan.renewal_count,
        book_title=loan.book.title if loan.book else None,
        student_name=loan.student.full_name if loan.student else None,
    )


@router.get("/me", response_model=list[LoanRead])
def my_loans(student: Student = Depends(require_student), db: Session = Depends(get_db)):
    loan_service.sync_overdue_status(db)
    loans = db.query(Loan).filter(Loan.student_id == student.id).order_by(Loan.borrowed_at.desc()).all()
    return [_to_loan_read(lo) for lo in loans]


@router.post("/borrow", response_model=LoanRead, status_code=201)
def borrow(body: LoanCreate, student: Student = Depends(require_student), db: Session = Depends(get_db)):
    loan = loan_service.borrow_book(db, student, body.book_id)
    return _to_loan_read(loan)


@router.post("/{loan_id}/return", response_model=LoanRead)
def return_loan(loan_id: int, student: Student = Depends(require_student), db: Session = Depends(get_db)):
    loan = loan_service.return_book(db, student, loan_id)
    return _to_loan_read(loan)


@router.get("/reports/overdue", response_model=list[OverdueReportItem])
def overdue_report(_: Admin = Depends(require_admin), db: Session = Depends(get_db)):
    rows = loan_service.list_overdue(db)
    return [OverdueReportItem(**r) for r in rows]
