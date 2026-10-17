from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.admin import Admin
from app.models.student import Student
from app.schemas.auth import LoginRequest, RegisterStudentRequest, TokenResponse
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Kimlik Doğrulama"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_student(body: RegisterStudentRequest, db: Session = Depends(get_db)):
    if db.query(Student).filter(Student.email == body.email).first():
        raise HTTPException(status_code=400, detail="E-posta zaten kayıtlı")
    if db.query(Student).filter(Student.student_number == body.student_number).first():
        raise HTTPException(status_code=400, detail="Öğrenci numarası zaten kayıtlı")

    student = Student(
        student_number=body.student_number,
        full_name=body.full_name,
        email=body.email,
        password_hash=hash_password(body.password),
        department=body.department,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    token = create_access_token(student.email, "student", student.id)
    return TokenResponse(access_token=token, role="student", display_name=student.full_name)


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    if body.as_admin:
        admin = db.query(Admin).filter(Admin.email == body.email).first()
        if not admin or not verify_password(body.password, admin.password_hash):
            raise HTTPException(status_code=401, detail="Yönetici girişi başarısız")
        token = create_access_token(admin.username, "admin", admin.id)
        return TokenResponse(access_token=token, role="admin", display_name=admin.full_name)

    student = db.query(Student).filter(Student.email == body.email).first()
    if not student or not verify_password(body.password, student.password_hash):
        raise HTTPException(status_code=401, detail="Öğrenci girişi başarısız")
    token = create_access_token(student.email, "student", student.id)
    return TokenResponse(access_token=token, role="student", display_name=student.full_name)
