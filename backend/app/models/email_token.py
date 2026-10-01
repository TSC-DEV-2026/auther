from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String

from app.db.base import Base


class EmailToken(Base):
    __tablename__ = "email_tokens"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    person_id = Column(BigInteger, ForeignKey("people.id", ondelete="CASCADE"), nullable=False, index=True)
    purpose = Column(String(32), nullable=False)
    token_hash = Column(String(64), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    consumed = Column(Boolean, nullable=False, default=False)
