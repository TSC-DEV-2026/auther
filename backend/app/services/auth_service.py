import logging
from dataclasses import dataclass
from datetime import timedelta

from jose import JWTError

from app.core.cpf import normalize_cpf, normalize_email
from app.core.exceptions import AppError
from app.core.redirects import resolve_redirect
from app.core.security import (
    SET_PASSWORD_MINUTES,
    VERIFY_EMAIL_HOURS,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    hash_secret,
    new_secret,
    utcnow,
    validate_password,
    verify_password,
)
from app.models.person import Person
from app.repositories.email_token_repository import EmailTokenRepository
from app.repositories.person_repository import PersonRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.services.email_service import EmailService

logger = logging.getLogger("auther.auth")


@dataclass
class SessionTokens:
    access_token: str
    refresh_token: str
    csrf_token: str
    person: Person


class AuthService:
    def __init__(
        self,
        people: PersonRepository,
        refreshes: RefreshTokenRepository,
        tokens: EmailTokenRepository,
        email: EmailService,
    ) -> None:
        self.people = people
        self.refreshes = refreshes
        self.tokens = tokens
        self.email = email

    def login(self, email: str, password: str) -> SessionTokens:
        person = self.people.get_by_email(normalize_email(email))
        if person is None or not person.password_hash or not verify_password(password, person.password_hash):
            logger.info("login recusado")
            raise AppError(401, "E-mail ou senha inválidos")
        if not person.is_active:
            logger.info("login recusado person_id=%s inativa", person.id)
            raise AppError(403, "Pessoa inativa")
        if not person.is_platform_admin:
            logger.info("login recusado person_id=%s sem permissão de admin", person.id)
            raise AppError(403, "Sem permissão")
        logger.info("login aceito person_id=%s", person.id)
        return self.issue_session(person)

    def verify_for_system(self, cpf: str, password: str) -> Person:
        person = self.people.get_by_cpf(normalize_cpf(cpf))
        if person is None or not person.password_hash or not verify_password(password, person.password_hash):
            logger.info("verify recusado")
            raise AppError(401, "CPF ou senha inválidos")
        if not person.is_active:
            logger.info("verify recusado person_id=%s inativa", person.id)
            raise AppError(403, "Pessoa inativa")
        return person

    def refresh(self, raw_refresh: str) -> SessionTokens:
        try:
            payload = decode_refresh_token(raw_refresh)
            person_id = int(payload["sub"])
            token_auth_version = int(payload["auth_version"])
        except (JWTError, KeyError, TypeError, ValueError):
            raise AppError(401, "Não autenticado") from None
        row = self.refreshes.get_by_hash(hash_secret(raw_refresh))
        if (
            row is None
            or row.revoked
            or row.expires_at <= utcnow()
            or row.person_id != person_id
            or row.auth_version != token_auth_version
        ):
            raise AppError(401, "Não autenticado")
        person = self.people.get_by_id(row.person_id)
        if person is None or not person.is_active or person.auth_version != row.auth_version:
            self.refreshes.revoke(row)
            raise AppError(401, "Não autenticado")
        if not person.is_platform_admin:
            self.refreshes.revoke(row)
            raise AppError(403, "Sem permissão")
        self.refreshes.revoke(row)
        return self.issue_session(person)

    def logout(self, person: Person | None) -> None:
        if person is None:
            return
        self._cut_sessions(person)
        self.people.save(person)
        logger.info("logout person_id=%s", person.id)

    def forgot(self, email: str, redirect_url: str) -> None:
        origin = resolve_redirect(redirect_url)
        person = self.people.get_by_email(normalize_email(email))
        if person is None or not person.is_active:
            return
        raw = self._issue_token(person.id, "set_password", minutes=SET_PASSWORD_MINUTES)
        try:
            self.email.send_reset(person.email, f"{origin}/reset-password?token={raw}")
        except Exception:
            logger.exception("falha ao enviar e-mail de redefinição")

    def reset_password(self, token: str, new_password: str) -> None:
        validate_password(new_password)
        row = self.tokens.get_valid(hash_secret(token), "set_password")
        if row is None:
            raise AppError(400, "Token inválido")
        person = self.people.get_by_id(row.person_id)
        if person is None or not person.is_active:
            raise AppError(400, "Token inválido")
        had_password = bool(person.password_hash)
        person.password_hash = hash_password(new_password)
        if had_password:
            self._cut_sessions(person)
        self.people.save(person)
        self.tokens.consume(row)

    def change_password(self, person: Person, current_password: str, new_password: str) -> None:
        validate_password(new_password)
        if not person.password_hash or not verify_password(current_password, person.password_hash):
            raise AppError(400, "Senha atual inválida")
        person.password_hash = hash_password(new_password)
        self._cut_sessions(person)
        self.people.save(person)

    def change_for_system(self, person_id: int, current_password: str, new_password: str) -> None:
        person = self.people.get_by_id(person_id)
        if person is None:
            raise AppError(404, "Pessoa não encontrada")
        if not person.is_active:
            raise AppError(403, "Pessoa inativa")
        self.change_password(person, current_password, new_password)

    def verify_email(self, token: str) -> None:
        row = self.tokens.get_valid(hash_secret(token), "verify_email")
        if row is None:
            raise AppError(400, "Token inválido")
        person = self.people.get_by_id(row.person_id)
        if person is None:
            raise AppError(400, "Token inválido")
        person.email_verified = True
        self.people.save(person)
        self.tokens.consume(row)

    def resend_verification(self, email: str, redirect_url: str) -> None:
        origin = resolve_redirect(redirect_url)
        person = self.people.get_by_email(normalize_email(email))
        if person is None or person.email_verified or not person.is_active:
            return
        raw = self._issue_token(person.id, "verify_email", minutes=VERIFY_EMAIL_HOURS * 60)
        try:
            self.email.send_verification(person.email, f"{origin}/verify-email/confirm?token={raw}")
        except Exception:
            logger.exception("falha ao reenviar verificação")

    def issue_session(self, person: Person) -> SessionTokens:
        access = create_access_token(person.id, person.auth_version)
        raw_refresh, expires_at = create_refresh_token(person.id, person.auth_version)
        self.refreshes.save(
            person_id=person.id,
            token_hash=hash_secret(raw_refresh),
            expires_at=expires_at,
            auth_version=person.auth_version,
        )
        return SessionTokens(
            access_token=access,
            refresh_token=raw_refresh,
            csrf_token=new_secret(),
            person=person,
        )

    def _cut_sessions(self, person: Person) -> None:
        person.auth_version += 1
        self.refreshes.revoke_all(person.id)

    def _issue_token(self, person_id: int, purpose: str, *, minutes: int) -> str:
        raw = new_secret()
        self.tokens.create(
            person_id=person_id,
            purpose=purpose,
            token_hash=hash_secret(raw),
            expires_at=utcnow() + timedelta(minutes=minutes),
        )
        return raw
