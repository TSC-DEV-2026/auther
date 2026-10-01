from pydantic import BaseModel

from app.core.fields import apply_fields
from app.schemas.person import PersonOut


class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    number: int


class ShortOut(BaseModel):
    id: int
    name: str
    number: int


def test_sem_fields_devolve_chaves_do_schema():
    payload = {"id": 1, "name": "a", "description": "b", "number": 3, "extra": True}
    result = apply_fields(payload, None, ProductOut)
    assert set(result) == {"id", "name", "description", "number"}


def test_fields_recorta_intersecao():
    payload = {"id": 1, "name": "a", "description": "b", "number": 3}
    result = apply_fields(payload, "id,name,description", ProductOut)
    assert result == {"id": 1, "name": "a", "description": "b"}


def test_campo_fora_do_schema_some():
    payload = {"id": 1, "name": "a", "number": 3}
    result = apply_fields(payload, "id,name,description", ShortOut)
    assert result == {"id": 1, "name": "a"}


def test_password_hash_nao_aparece():
    payload = {
        "id": 1,
        "cpf": "12345678900",
        "email": "a@x.com",
        "full_name": "Ana",
        "email_verified": False,
        "is_active": True,
        "is_platform_admin": False,
    }
    result = apply_fields(payload, "id,password_hash", PersonOut)
    assert "password_hash" not in result
    assert result == {"id": 1}


def test_nomes_invalidos_sao_ignorados():
    payload = {"id": 1, "name": "a", "description": "b", "number": 3}
    result = apply_fields(payload, "id;drop,items.id, name ", ProductOut)
    assert result == {"name": "a"}


def test_person_out_nao_tem_hash():
    assert "password" not in PersonOut.model_fields
    assert "password_hash" not in PersonOut.model_fields
