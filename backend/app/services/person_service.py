import logging
from datetime import timedelta

from app.core.config import settings
from app.core.cpf import normalize_cpf, normalize_email
from app.core.exceptions import AppError
from app.core.redirects import resolve_redirect
from app.core.security import (
    SET_PASSWORD_MINUTES,
    VERIFY_EMAIL_HOURS,
    hash_password,
    hash_secret,
    new_secret,
    utcnow,
    validate_password,
)
from app.models.person import Person
from app.repositories.email_token_repository import EmailTokenRepository
from app.repositories.person_repository import PersonRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.schemas.auth import InternalPersonIn
from app.schemas.person import PersonCreate, PersonUpdate
from app.services.email_service import EmailService

logger = logging.getLogger("auther.people")


class PersonService:
    def __init__(
        self,
        people: PersonRepository,
        tokens: EmailTokenRepository,
        refreshes: RefreshTokenRepository,
        email: EmailService,
    ) -> None:
        self.people = people
        self.tokens = tokens
        self.refreshes = refreshes
        self.email = email

    def list_people(
        self,
        *,
        cpf: str | None,
        email: str | None,
        page: int,
        limit: int,
    ) -> tuple[list[Person], int]:
        normalized_cpf = normalize_cpf(cpf) if cpf and cpf.strip() else None
        normalized_email = normalize_email(email) if email and email.strip() else None
        return self.people.list_people(
            cpf=normalized_cpf,
            email=normalized_email,
            page=page,
            limit=limit,
        )

    def get_person(self, person_id: int) -> Person:
        person = self.people.get_by_id(person_id)
        if person is None:
            raise AppError(404, "Pessoa não encontrada")
        return person

    def create_person(self, data: PersonCreate) -> Person:
        person = self._insert(
            cpf=normalize_cpf(data.cpf),
            email=normalize_email(str(data.email)),
            full_name=data.full_name.strip(),
            password=None,
        )
        self._send_invite(person, settings.PUBLIC_APP_URL)
        return person

    def update_person(self, person: Person, data: PersonUpdate, *, actor_id: int) -> Person:
        changed_email = False
        if "cpf" in data.model_fields_set and data.cpf is not None:
            cpf = normalize_cpf(data.cpf)
            existing = self.people.get_by_cpf(cpf)
            if existing is not None and existing.id != person.id:
                raise AppError(400, "CPF já cadastrado")
            person.cpf = cpf
        if "email" in data.model_fields_set and data.email is not None:
            email = normalize_email(str(data.email))
            existing = self.people.get_by_email(email)
            if existing is not None and existing.id != person.id:
                raise AppError(400, "E-mail já cadastrado")
            if email != person.email:
                person.email = email
                person.email_verified = False
                changed_email = True
        if "full_name" in data.model_fields_set and data.full_name is not None:
            person.full_name = data.full_name.strip()
        if "is_active" in data.model_fields_set and data.is_active is not None:
            if data.is_active is False and person.is_active:
                if person.id == actor_id:
                    raise AppError(400, "O admin da sessão não pode desativar a si mesmo")
                person.is_active = False
                self._cut_sessions(person)
            elif data.is_active is True and not person.is_active:
                person.is_active = True
        self.people.save(person)
        if changed_email:
            self._send_verification(person, settings.PUBLIC_APP_URL)
        return person

    def delete_person(self, person: Person, *, actor_id: int) -> None:
        if person.id == actor_id:
            raise AppError(400, "O admin da sessão não pode excluir a si mesmo")
        if person.is_platform_admin and self.people.count_platform_admins() <= 1:
            raise AppError(400, "Não é possível excluir o último admin da plataforma")
        self.people.delete(person)

    def upsert_from_system(self, data: InternalPersonIn) -> tuple[int, bool]:
        cpf = normalize_cpf(data.cpf)
        existing = self.people.get_by_cpf(cpf)
        if existing is not None:
            return existing.id, False
        password = data.password or None
        person = self._insert(
            cpf=cpf,
            email=normalize_email(str(data.email)),
            full_name=data.full_name.strip(),
            password=password,
        )
        if password:
            if data.redirect_url:
                self._send_verification(person, data.redirect_url)
        else:
            if not data.redirect_url:
                raise AppError(400, "redirect_url é obrigatória para o convite")
            self._send_invite(person, data.redirect_url)
        return person.id, True

    def _insert(self, *, cpf: str, email: str, full_name: str, password: str | None) -> Person:
        if self.people.get_by_cpf(cpf) is not None:
            raise AppError(400, "CPF já cadastrado")
        if self.people.get_by_email(email) is not None:
            raise AppError(400, "E-mail já cadastrado")
        password_hash = None
        if password:
            validate_password(password)
            password_hash = hash_password(password)
        person = Person(
            cpf=cpf,
            email=email,
            full_name=full_name,
            password_hash=password_hash,
            email_verified=False,
            is_active=True,
            is_platform_admin=False,
            auth_version=1,
        )
        return self.people.save(person)

    def _cut_sessions(self, person: Person) -> None:
        person.auth_version += 1
        self.refreshes.revoke_all(person.id)
        logger.info("sessões revogadas person_id=%s", person.id)

    def _send_invite(self, person: Person, redirect_url: str) -> None:
        origin = resolve_redirect(redirect_url)
        raw = self._issue_token(person.id, "set_password", minutes=SET_PASSWORD_MINUTES)
        self.email.send_invite(person.email, f"{origin}/reset-password?token={raw}")

    def _send_verification(self, person: Person, redirect_url: str) -> None:
        origin = resolve_redirect(redirect_url)
        raw = self._issue_token(person.id, "verify_email", minutes=VERIFY_EMAIL_HOURS * 60)
        self.email.send_verification(person.email, f"{origin}/verify-email/confirm?token={raw}")

    def _issue_token(self, person_id: int, purpose: str, *, minutes: int) -> str:
        raw = new_secret()
        self.tokens.create(
            person_id=person_id,
            purpose=purpose,
            token_hash=hash_secret(raw),
            expires_at=utcnow() + timedelta(minutes=minutes),
        )
        return raw
