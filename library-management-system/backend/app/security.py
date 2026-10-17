from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.admin import Admin
from app.models.student import Student

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(subject: str, role: str, user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "role": role, "uid": user_id, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz veya süresi dolmuş oturum") from exc


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: Annotated[Session, Depends(get_db)],
) -> Student | Admin:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Oturum gerekli")
    data = decode_token(credentials.credentials)
    role = data.get("role")
    uid = data.get("uid")
    if role == "student":
        user = db.get(Student, uid)
    elif role == "admin":
        user = db.get(Admin, uid)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz rol")
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Kullanıcı bulunamadı")
    return user


def require_student(user: Annotated[Student | Admin, Depends(get_current_user)]) -> Student:
    if not isinstance(user, Student):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Öğrenci hesabı gerekli")
    return user


def require_admin(user: Annotated[Student | Admin, Depends(get_current_user)]) -> Admin:
    if not isinstance(user, Admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Yönetici hesabı gerekli")
    return user
