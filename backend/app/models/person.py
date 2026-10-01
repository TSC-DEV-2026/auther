from sqlalchemy import BigInteger, Boolean, Column, Integer, String

from app.db.base import Base


class Person(Base):
    __tablename__ = "people"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    cpf = Column(String(11), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=False)
    email_verified = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    is_platform_admin = Column(Boolean, nullable=False, default=False)
    auth_version = Column(Integer, nullable=False, default=1)
