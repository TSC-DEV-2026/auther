import pytest
from jose import JWTError

from app.core.exceptions import AppError
from app.core.security import decode_access_token, decode_refresh_token, hash_password, verify_password
from app.models.person import Person
from app.schemas.auth import InternalPersonIn
from app.schemas.person import PersonCreate, PersonUpdate
from app.services.auth_service import AuthService
from app.services.person_service import PersonService
from tests.fakes import MemoryEmail, MemoryPeople, MemoryRefresh, MemoryTokens


def make_person(**overrides) -> Person:
    data = {
        "cpf": "12345678900",
        "email": "ana@x.com",
        "full_name": "Ana",
        "password_hash": hash_password("senha-certa"),
        "email_verified": False,
        "is_active": True,
        "is_platform_admin": False,
        "auth_version": 1,
    }
    data.update(overrides)
    return Person(**data)


def services():
    people = MemoryPeople()
    refreshes = MemoryRefresh()
    tokens = MemoryTokens()
    email = MemoryEmail()
    auth = AuthService(people, refreshes, tokens, email)
    person_service = PersonService(people, tokens, refreshes, email)
    return people, refreshes, tokens, email, auth, person_service


def test_verify_aceita_email_nao_verificado():
    people, _, _, _, auth, _ = services()
    person = people.save(make_person(email_verified=False))
    found = auth.verify_for_system("123.456.789-00", "senha-certa")
    assert found.id == person.id
    assert found.email_verified is False


def test_verify_senha_errada_e_cpf_inexistente_sao_401():
    people, _, _, _, auth, _ = services()
    people.save(make_person())
    with pytest.raises(AppError) as wrong:
        auth.verify_for_system("12345678900", "outra-senha")
    assert wrong.value.status_code == 401
    with pytest.raises(AppError) as missing:
        auth.verify_for_system("00000000000", "senha-certa")
    assert missing.value.status_code == 401


def test_verify_pessoa_inativa_e_403():
    people, _, _, _, auth, _ = services()
    people.save(make_person(is_active=False))
    with pytest.raises(AppError) as caught:
        auth.verify_for_system("12345678900", "senha-certa")
    assert caught.value.status_code == 403


def test_login_so_admin_da_plataforma():
    people, refreshes, _, _, auth, _ = services()
    people.save(make_person())
    with pytest.raises(AppError) as denied:
        auth.login("ana@x.com", "senha-certa")
    assert denied.value.status_code == 403
    admin = people.save(make_person(cpf="98765432100", email="luiz@x.com", is_platform_admin=True))
    session = auth.login("luiz@x.com", "senha-certa")
    assert session.person.id == admin.id
    assert session.access_token
    payload = decode_access_token(session.access_token)
    assert payload["sub"] == admin.id
    assert payload["typ"] == "access"
    refresh_payload = decode_refresh_token(session.refresh_token)
    assert refresh_payload["sub"] == admin.id
    assert refresh_payload["typ"] == "refresh"
    assert refresh_payload["jti"]
    assert len(refreshes.rows) == 1


def test_troca_de_senha_e_logout_sobem_auth_version():
    people, refreshes, _, _, auth, _ = services()
    admin = people.save(make_person(email="luiz@x.com", is_platform_admin=True))
    auth.issue_session(admin)
    auth.change_password(admin, "senha-certa", "senha-nova1")
    assert admin.auth_version == 2
    assert refreshes.rows[0].revoked is True
    auth.logout(admin)
    assert admin.auth_version == 3


def test_access_nao_serve_de_refresh():
    people, _, _, _, auth, _ = services()
    people.save(make_person(email="luiz@x.com", is_platform_admin=True))
    session = auth.login("luiz@x.com", "senha-certa")
    with pytest.raises(JWTError):
        decode_access_token(session.refresh_token)
    with pytest.raises(AppError) as caught:
        auth.refresh(session.access_token)
    assert caught.value.status_code == 401


def test_refresh_recusa_auth_version_antiga():
    people, _, _, _, auth, _ = services()
    admin = people.save(make_person(email="luiz@x.com", is_platform_admin=True))
    session = auth.issue_session(admin)
    admin.auth_version = 9
    with pytest.raises(AppError) as caught:
        auth.refresh(session.refresh_token)
    assert caught.value.status_code == 401


def test_forgot_responde_igual_exista_ou_nao():
    people, _, _, email, auth, _ = services()
    people.save(make_person())
    auth.forgot("nao-existe@x.com", "http://localhost:5173")
    auth.forgot("ana@x.com", "http://localhost:5173")
    assert len(email.sent) == 1
    assert email.sent[0][0] == "reset"


def test_reset_grava_senha_sem_vazar_hash_no_out():
    people, _, tokens, email, auth, _ = services()
    person = people.save(make_person(password_hash=None))
    auth.forgot("ana@x.com", "http://localhost:5173")
    link = email.sent[0][2]
    token = link.split("token=")[1]
    auth.reset_password(token, "senha-nova1")
    assert verify_password("senha-nova1", person.password_hash)
    assert tokens.rows[0].consumed is True


def test_cpf_existente_nao_troca_senha_nem_email():
    people, _, _, email, _, person_service = services()
    person = people.save(make_person())
    original_hash = person.password_hash
    person_id, created = person_service.upsert_from_system(
        InternalPersonIn(
            cpf="12345678900",
            email="outra@x.com",
            full_name="Outra",
            password="senha-nova1",
            redirect_url="http://localhost:5174",
        )
    )
    assert created is False
    assert person_id == person.id
    assert person.email == "ana@x.com"
    assert person.password_hash == original_hash
    assert email.sent == []


def test_convite_sem_senha_e_cadastro_com_senha():
    _, _, _, email, _, person_service = services()
    person_id, created = person_service.upsert_from_system(
        InternalPersonIn(
            cpf="12345678900",
            email="ana@x.com",
            full_name="Ana",
            redirect_url="http://localhost:5174",
        )
    )
    assert created is True
    person = person_service.get_person(person_id)
    assert person.password_hash is None
    assert email.sent[0][0] == "invite"

    person_id, created = person_service.upsert_from_system(
        InternalPersonIn(
            cpf="98765432100",
            email="bia@x.com",
            full_name="Bia",
            password="senha-certa",
            redirect_url="http://localhost:5174",
        )
    )
    assert created is True
    created_person = person_service.get_person(person_id)
    assert created_person.password_hash
    assert verify_password("senha-certa", created_person.password_hash)
    assert all(item[0] != "invite" or item[1] != "bia@x.com" for item in email.sent)
    assert any(item[0] == "verify" and item[1] == "bia@x.com" for item in email.sent)


def test_desativar_sobe_auth_version():
    people, _, _, _, auth, person_service = services()
    admin = people.save(make_person(cpf="98765432100", email="luiz@x.com", is_platform_admin=True))
    person = people.save(make_person())
    auth.issue_session(admin)
    person_service.update_person(person, PersonUpdate(is_active=False), actor_id=admin.id)
    assert person.is_active is False
    assert person.auth_version == 2


def test_admin_nao_desativa_a_si_mesmo():
    people, _, _, _, _, person_service = services()
    admin = people.save(make_person(email="luiz@x.com", is_platform_admin=True))
    with pytest.raises(AppError) as caught:
        person_service.update_person(admin, PersonUpdate(is_active=False), actor_id=admin.id)
    assert caught.value.status_code == 400
    assert admin.is_active is True


def test_convite_do_admin_nao_grava_senha():
    people, _, _, email, _, person_service = services()
    people.save(make_person(cpf="98765432100", email="luiz@x.com", is_platform_admin=True))
    person = person_service.create_person(
        PersonCreate(cpf="12345678900", email="ana@x.com", full_name="Ana")
    )
    assert person.password_hash is None
    assert email.sent[0][0] == "invite"
