from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.cookies import clear_auth_cookies, set_auth_cookies
from app.api.dependencies.auth import get_current_admin, read_person
from app.api.dependencies.database import get_db
from app.api.dependencies.services import get_auth_service
from app.api.responses import json_data
from app.core.config import settings
from app.core.exceptions import AppError
from app.core.limiter import limiter
from app.core.security import REFRESH_COOKIE
from app.schemas.auth import ChangePasswordIn, ForgotIn, LoginIn, ResendIn, ResetIn
from app.schemas.common import Envelope, MessageOut
from app.schemas.person import PersonOut
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

FORGOT_MESSAGE = "Se o e-mail existir, enviaremos as instruções."


@router.post(
    "/login",
    response_model=Envelope[PersonOut],
    summary="Login do admin",
    description="E-mail e senha. Só is_platform_admin. Grava cookies HttpOnly e devolve a pessoa, sem JWT no JSON.",
)
@limiter.limit("10/minute")
def login(request: Request, body: LoginIn, service: AuthService = Depends(get_auth_service)):
    session = service.login(str(body.email), body.password)
    response = json_data(PersonOut.model_validate(session.person).model_dump())
    set_auth_cookies(response, session)
    return response


@router.post(
    "/refresh",
    response_model=Envelope[PersonOut],
    summary="Renovar sessão",
    description="Rotaciona o refresh JWT. O access anterior vale até expirar. A resposta não traz JWT.",
)
@limiter.limit("10/minute")
def refresh_session(request: Request, service: AuthService = Depends(get_auth_service)):
    raw = request.cookies.get(REFRESH_COOKIE)
    if not raw:
        raise AppError(401, "Não autenticado")
    session = service.refresh(raw)
    response = json_data(PersonOut.model_validate(session.person).model_dump())
    set_auth_cookies(response, session)
    return response


@router.post(
    "/logout",
    response_model=Envelope[None],
    summary="Encerrar sessão",
    description="Sobe auth_version, revoga os refresh deste autenticador e apaga os cookies. O access já emitido vale até o exp.",
)
def logout(
    request: Request,
    db: Session = Depends(get_db),
    service: AuthService = Depends(get_auth_service),
):
    service.logout(read_person(request, db))
    response = json_data(None)
    clear_auth_cookies(response)
    return response


@router.get(
    "/me",
    response_model=Envelope[PersonOut],
    summary="Pessoa da sessão",
    description="Devolve o admin autenticado pelo cookie de access.",
)
def me(request: Request, db: Session = Depends(get_db)):
    person = get_current_admin(request, db)
    return json_data(PersonOut.model_validate(person).model_dump())


@router.post(
    "/forgot-password",
    response_model=Envelope[MessageOut],
    summary="Esqueci a senha",
    description="Resposta igual exista ou não o e-mail.",
)
@limiter.limit("10/minute")
def forgot_password(request: Request, body: ForgotIn, service: AuthService = Depends(get_auth_service)):
    service.forgot(str(body.email), settings.PUBLIC_APP_URL)
    return json_data(MessageOut(message=FORGOT_MESSAGE).model_dump())


@router.post(
    "/reset-password",
    response_model=Envelope[None],
    summary="Definir senha com token",
    description="Consome o token de convite ou de redefinição e grava a senha nova.",
)
@limiter.limit("10/minute")
def reset_password(request: Request, body: ResetIn, service: AuthService = Depends(get_auth_service)):
    service.reset_password(body.token, body.new_password)
    return json_data(None)


@router.post(
    "/change-password",
    response_model=Envelope[None],
    summary="Trocar senha",
    description="Sessão ativa. Senha atual e senha nova. Sobe auth_version e revoga os refresh.",
)
@limiter.limit("10/minute")
def change_password(
    request: Request,
    body: ChangePasswordIn,
    db: Session = Depends(get_db),
    service: AuthService = Depends(get_auth_service),
):
    person = get_current_admin(request, db)
    service.change_password(person, body.current_password, body.new_password)
    return json_data(None)


@router.get(
    "/verify-email",
    response_model=Envelope[None],
    summary="Confirmar e-mail",
    description="Consome o token do link. E-mail não verificado não impede o login.",
)
def verify_email(
    token: str = Query(min_length=10, max_length=200),
    service: AuthService = Depends(get_auth_service),
):
    service.verify_email(token)
    return json_data(None)


@router.post(
    "/resend-verification",
    response_model=Envelope[MessageOut],
    summary="Reenviar verificação",
    description="Resposta igual exista ou não o e-mail.",
)
@limiter.limit("10/minute")
def resend_verification(request: Request, body: ResendIn, service: AuthService = Depends(get_auth_service)):
    service.resend_verification(str(body.email), settings.PUBLIC_APP_URL)
    return json_data(MessageOut(message=FORGOT_MESSAGE).model_dump())
