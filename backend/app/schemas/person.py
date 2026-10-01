from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PersonCreate(BaseModel):
    cpf: str = Field(min_length=11, max_length=14)
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)


class PersonUpdate(BaseModel):
    cpf: str | None = Field(default=None, min_length=11, max_length=14)
    email: EmailStr | None = None
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    is_active: bool | None = None


class PersonOut(BaseModel):
    id: int
    cpf: str
    email: str
    full_name: str
    email_verified: bool
    is_active: bool
    is_platform_admin: bool

    model_config = ConfigDict(from_attributes=True)
