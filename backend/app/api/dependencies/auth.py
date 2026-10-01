import secrets

from fastapi import Depends, Header, Request
from jose import JWTError
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db
from app.core.config import settings
from app.core.exceptions import AppError
from app.core.security import ACCESS_COOKIE, decode_access_token
from app.models.person import Person
from app.repositories.person_repository import PersonRepository


def get_current_admin(request: Request, db: Session = Depends(get_db)) -> Person:
    person = read_person(request, db)
    if person is None:
        raise AppError(401, "Não autenticado")
    if not person.is_active:
        raise AppError(403, "Pessoa inativa")
    if not person.is_platform_admin:
        raise AppError(403, "Sem permissão")
    return person


def read_person(request: Request, db: Session) -> Person | None:
    token = request.cookies.get(ACCESS_COOKIE)
    if not token:
        return None
    try:
        payload = decode_access_token(token)
        person_id = int(payload["sub"])
    except (JWTError, KeyError, TypeError, ValueError):
        return None
    return PersonRepository(db).get_by_id(person_id)


def require_api_key(x_api_key: str | None = Header(default=None, alias="X-Api-Key")) -> None:
    expected = settings.AUTHENTICATOR_API_KEY
    if not x_api_key or len(x_api_key) != len(expected) or not secrets.compare_digest(x_api_key, expected):
        raise AppError(401, "Não autenticado")
