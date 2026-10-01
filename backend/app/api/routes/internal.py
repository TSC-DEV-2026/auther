from fastapi import APIRouter, Depends, Request

from app.api.dependencies.auth import require_api_key
from app.api.dependencies.services import get_auth_service, get_person_service
from app.api.responses import json_data
from app.core.limiter import limiter
from app.schemas.auth import (
    InternalChangeIn,
    InternalForgotIn,
    InternalPersonIn,
    InternalPersonOut,
    InternalPersonStateOut,
    InternalResendIn,
    InternalVerifyEmailIn,
    ResetIn,
    VerifyIn,
    VerifyOut,
)
from app.schemas.common import Envelope, MessageOut
from app.services.auth_service import AuthService
from app.services.person_service import PersonService

router = APIRouter(prefix="/internal", tags=["internal"], dependencies=[Depends(require_api_key)])

FORGOT_MESSAGE = "Se o e-mail existir, enviaremos as instruções."


@router.post(
    "/auth/verify",
    response_model=Envelope[VerifyOut],
    summary="Validar CPF e senha",
    description="Uso dos sistemas de negócio. Senha errada: 401. Pessoa inativa: 403. E-mail não verificado não recusa.",
)
@limiter.limit("10/minute")
def verify(request: Request, body: VerifyIn, service: AuthService = Depends(get_auth_service)):
    person = service.verify_for_system(body.cpf, body.password)
    payload = VerifyOut(
        person_id=person.id,
        cpf=person.cpf,
        email=person.email,
        full_name=person.full_name,
        email_verified=person.email_verified,
        is_active=person.is_active,
        auth_version=person.auth_version,
    )
    return json_data(payload.model_dump())


@router.post(
    "/people",
    response_model=Envelope[InternalPersonOut],
    summary="Achar ou criar pessoa",
    description="CPF existente devolve o mesmo person_id, sem trocar senha nem e-mail. Sem senha, dispara o convite.",
)
def upsert_person(body: InternalPersonIn, service: PersonService = Depends(get_person_service)):
    person_id, created = service.upsert_from_system(body)
    status_code = 201 if created else 200
    return json_data(InternalPersonOut(person_id=person_id, created=created).model_dump(), status_code=status_code)


@router.get(
    "/people/{person_id}",
    response_model=Envelope[InternalPersonStateOut],
    summary="Estado da pessoa",
    description="Devolve is_active, email_verified e auth_version para o refresh do sistema de negócio.",
)
def person_state(person_id: int, service: PersonService = Depends(get_person_service)):
    person = service.get_person(person_id)
    payload = InternalPersonStateOut(
        full_name=person.full_name,
        email=person.email,
        is_active=person.is_active,
        email_verified=person.email_verified,
        auth_version=person.auth_version,
    )
    return json_data(payload.model_dump())


@router.post(
    "/auth/forgot-password",
    response_model=Envelope[MessageOut],
    summary="Repasse de esqueci a senha",
    description="O sistema de negócio envia o e-mail e a redirect_url allowlisted. A resposta não revela se o e-mail existe.",
)
@limiter.limit("10/minute")
def forgot_password(request: Request, body: InternalForgotIn, service: AuthService = Depends(get_auth_service)):
    service.forgot(str(body.email), body.redirect_url)
    return json_data(MessageOut(message=FORGOT_MESSAGE).model_dump())


@router.post(
    "/auth/reset-password",
    response_model=Envelope[None],
    summary="Repasse de redefinição de senha",
    description="O sistema de negócio envia o token e a senha nova. O hash fica só aqui.",
)
@limiter.limit("10/minute")
def reset_password(request: Request, body: ResetIn, service: AuthService = Depends(get_auth_service)):
    service.reset_password(body.token, body.new_password)
    return json_data(None)


@router.post(
    "/auth/change-password",
    response_model=Envelope[None],
    summary="Repasse de troca de senha",
    description="O sistema de negócio envia person_id, senha atual e senha nova.",
)
@limiter.limit("10/minute")
def change_password(request: Request, body: InternalChangeIn, service: AuthService = Depends(get_auth_service)):
    service.change_for_system(body.person_id, body.current_password, body.new_password)
    return json_data(None)


@router.post(
    "/auth/verify-email",
    response_model=Envelope[None],
    summary="Repasse de confirmação de e-mail",
    description="O sistema de negócio envia o token do link. O hash do token fica só aqui.",
)
def verify_email(body: InternalVerifyEmailIn, service: AuthService = Depends(get_auth_service)):
    service.verify_email(body.token)
    return json_data(None)


@router.post(
    "/auth/resend-verification",
    response_model=Envelope[MessageOut],
    summary="Repasse de reenvio de verificação",
    description="O sistema de negócio envia o e-mail e a redirect_url allowlisted. A resposta não revela se o e-mail existe.",
)
@limiter.limit("10/minute")
def resend_verification(request: Request, body: InternalResendIn, service: AuthService = Depends(get_auth_service)):
    service.resend_verification(str(body.email), body.redirect_url)
    return json_data(MessageOut(message=FORGOT_MESSAGE).model_dump())
