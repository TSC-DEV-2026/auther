from pydantic import BaseModel, EmailStr, Field


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class ForgotIn(BaseModel):
    email: EmailStr


class ResetIn(BaseModel):
    token: str = Field(min_length=10, max_length=200)
    new_password: str = Field(min_length=8, max_length=72)


class ChangePasswordIn(BaseModel):
    current_password: str = Field(min_length=1, max_length=72)
    new_password: str = Field(min_length=8, max_length=72)


class ResendIn(BaseModel):
    email: EmailStr


class VerifyIn(BaseModel):
    cpf: str = Field(min_length=11, max_length=14)
    password: str = Field(min_length=1, max_length=72)


class VerifyOut(BaseModel):
    person_id: int
    cpf: str
    email: str
    full_name: str
    email_verified: bool
    is_active: bool
    auth_version: int


class InternalPersonIn(BaseModel):
    cpf: str = Field(min_length=11, max_length=14)
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    password: str | None = Field(default=None, max_length=72)
    redirect_url: str | None = None


class InternalPersonOut(BaseModel):
    person_id: int
    created: bool


class InternalPersonStateOut(BaseModel):
    full_name: str
    email: str
    is_active: bool
    email_verified: bool
    auth_version: int


class InternalForgotIn(BaseModel):
    email: EmailStr
    redirect_url: str


class InternalVerifyEmailIn(BaseModel):
    token: str = Field(min_length=10, max_length=200)


class InternalResendIn(BaseModel):
    email: EmailStr
    redirect_url: str


class InternalChangeIn(BaseModel):
    person_id: int
    current_password: str = Field(min_length=1, max_length=72)
    new_password: str = Field(min_length=8, max_length=72)
