from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String

from app.db.base import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    person_id = Column(BigInteger, ForeignKey("people.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(64), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, nullable=False, default=False)
    auth_version = Column(Integer, nullable=False)
