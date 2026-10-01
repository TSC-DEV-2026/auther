import logging

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.cpf import normalize_cpf, normalize_email
from app.core.security import hash_password, validate_password
from app.models.person import Person
from app.repositories.person_repository import PersonRepository

logger = logging.getLogger("auther.seed")


def seed_platform_admin(db: Session) -> None:
    if not settings.SEED_ADMIN_EMAIL or not settings.SEED_ADMIN_CPF or not settings.SEED_ADMIN_PASSWORD:
        logger.info("seed do admin não configurado")
        return
    people = PersonRepository(db)
    if people.count_platform_admins() > 0:
        return
    validate_password(settings.SEED_ADMIN_PASSWORD)
    person = Person(
        cpf=normalize_cpf(settings.SEED_ADMIN_CPF),
        email=normalize_email(settings.SEED_ADMIN_EMAIL),
        full_name=(settings.SEED_ADMIN_FULL_NAME or "Admin").strip(),
        password_hash=hash_password(settings.SEED_ADMIN_PASSWORD),
        email_verified=True,
        is_active=True,
        is_platform_admin=True,
        auth_version=1,
    )
    people.save(person)
    db.commit()
    logger.info("admin da plataforma criado person_id=%s", person.id)
