import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import AppError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_COOKIE = "access_token"
REFRESH_COOKIE = "refresh_token"
CSRF_COOKIE = "csrf_token"
SET_PASSWORD_MINUTES = 60
VERIFY_EMAIL_HOURS = 24
PASSWORD_MIN = 8
PASSWORD_MAX = 72


def validate_password(password: str) -> None:
    if len(password) < PASSWORD_MIN or len(password) > PASSWORD_MAX:
        raise AppError(400, "A senha deve ter entre 8 e 72 caracteres")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def new_secret() -> str:
    return secrets.token_urlsafe(48)


def hash_secret(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _encode(payload: dict) -> str:
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def _decode(token: str) -> dict:
    # sub fica numérico, como no contrato. python-jose recusa isso com verify_sub ligado.
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        options={"verify_sub": False},
    )


def create_access_token(person_id: int, auth_version: int) -> str:
    now = utcnow()
    return _encode(
        {
            "sub": person_id,
            "auth_version": auth_version,
            "typ": "access",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
        }
    )


def decode_access_token(token: str) -> dict:
    payload = _decode(token)
    if payload.get("typ") != "access":
        raise JWTError("typ inválido")
    return payload


def create_refresh_token(person_id: int, auth_version: int) -> tuple[str, datetime]:
    now = utcnow()
    expires = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    token = _encode(
        {
            "sub": person_id,
            "auth_version": auth_version,
            "typ": "refresh",
            "jti": new_secret(),
            "iat": int(now.timestamp()),
            "exp": int(expires.timestamp()),
        }
    )
    return token, expires


def decode_refresh_token(token: str) -> dict:
    payload = _decode(token)
    if payload.get("typ") != "refresh" or not payload.get("jti"):
        raise JWTError("typ inválido")
    return payload


__all__ = ["JWTError"]
