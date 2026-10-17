from pydantic import BaseModel, EmailStr, Field


class RegisterStudentRequest(BaseModel):
    student_number: str = Field(min_length=3, max_length=32)
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)
    department: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    as_admin: bool = False


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    display_name: str
