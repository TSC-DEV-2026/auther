from fastapi import APIRouter, Depends, Query, Request

from app.api.dependencies.auth import get_current_admin
from app.api.dependencies.services import get_person_service
from app.api.responses import json_data
from app.core.fields import apply_fields
from app.core.limiter import limiter
from app.models.person import Person
from app.schemas.common import Envelope, Page
from app.schemas.person import PersonCreate, PersonOut, PersonUpdate
from app.services.person_service import PersonService

router = APIRouter(prefix="/people", tags=["people"])


def _dump(person: Person, fields: str | None) -> dict:
    payload = PersonOut.model_validate(person).model_dump()
    return apply_fields(payload, fields, PersonOut)


@router.get(
    "",
    response_model=Envelope[Page[PersonOut]],
    summary="Listar pessoas",
    description="Lista paginada. Filtros nomeados cpf e email. fields recorta o PersonOut depois do DTO.",
)
def list_people(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    cpf: str | None = Query(default=None, max_length=14),
    email: str | None = Query(default=None, max_length=255),
    fields: str | None = Query(default=None, max_length=500),
    _: Person = Depends(get_current_admin),
    service: PersonService = Depends(get_person_service),
):
    items, total = service.list_people(cpf=cpf, email=email, page=page, limit=limit)
    return json_data(
        {
            "items": [_dump(person, fields) for person in items],
            "total": total,
            "page": page,
            "limit": limit,
        }
    )


@router.get(
    "/{person_id}",
    response_model=Envelope[PersonOut],
    summary="Detalhe da pessoa",
    description="Um cadastro pelo id. fields recorta o PersonOut. Sem senha.",
)
def get_person(
    person_id: int,
    fields: str | None = Query(default=None, max_length=500),
    _: Person = Depends(get_current_admin),
    service: PersonService = Depends(get_person_service),
):
    person = service.get_person(person_id)
    return json_data(_dump(person, fields))


@router.post(
    "",
    response_model=Envelope[PersonOut],
    status_code=201,
    summary="Convidar pessoa",
    description="Cria a pessoa sem senha no body e envia o convite para ela definir a senha.",
)
@limiter.limit("10/minute")
def create_person(
    request: Request,
    body: PersonCreate,
    _: Person = Depends(get_current_admin),
    service: PersonService = Depends(get_person_service),
):
    person = service.create_person(body)
    return json_data(PersonOut.model_validate(person).model_dump(), status_code=201)


@router.put(
    "/{person_id}",
    response_model=Envelope[PersonOut],
    summary="Atualizar pessoa",
    description="Corrige CPF, e-mail ou nome, ou desativa a pessoa. Desativar sobe auth_version.",
)
def update_person(
    person_id: int,
    body: PersonUpdate,
    admin: Person = Depends(get_current_admin),
    service: PersonService = Depends(get_person_service),
):
    person = service.get_person(person_id)
    updated = service.update_person(person, body, actor_id=admin.id)
    return json_data(PersonOut.model_validate(updated).model_dump())


@router.delete(
    "/{person_id}",
    response_model=Envelope[None],
    summary="Excluir pessoa",
    description="Remove o cadastro. Resposta 200 com data nula.",
)
def delete_person(
    person_id: int,
    admin: Person = Depends(get_current_admin),
    service: PersonService = Depends(get_person_service),
):
    person = service.get_person(person_id)
    service.delete_person(person, actor_id=admin.id)
    return json_data(None)
