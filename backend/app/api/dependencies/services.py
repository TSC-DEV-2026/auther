from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db
from app.repositories.email_token_repository import EmailTokenRepository
from app.repositories.person_repository import PersonRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.services.person_service import PersonService


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(
        PersonRepository(db),
        RefreshTokenRepository(db),
        EmailTokenRepository(db),
        EmailService(),
    )


def get_person_service(db: Session = Depends(get_db)) -> PersonService:
    return PersonService(
        PersonRepository(db),
        EmailTokenRepository(db),
        RefreshTokenRepository(db),
        EmailService(),
    )
