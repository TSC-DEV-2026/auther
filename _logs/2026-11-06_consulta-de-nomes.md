# Log — consulta de nomes

**Data:** 2026-11-06  
**Sessão:** nomes da lista de acessos numa consulta

---

## ✅ O que foi feito

- `POST /internal/people/lookup` devolve `person_id` e `full_name` das pessoas encontradas.
- Identificador repetido entra uma vez. Lista vazia não consulta o banco. Acima de 100 identificadores responde 400.
- `GET /internal/people/{id}` permanece com o estado completo.

## 📁 Arquivos criados

- `_logs/2026-11-06_consulta-de-nomes.md` — registro desta sessão.

## ✏️ Arquivos modificados

- `backend/app/api/routes/internal.py` — rota da consulta.
- `backend/app/schemas/auth.py` — corpo e resposta.
- `backend/app/services/person_service.py` — teto, repetidos e lista vazia.
- `backend/app/repositories/person_repository.py` — uma consulta pelos ids.
- `backend/tests/fakes.py` — consulta em memória.
- `backend/tests/test_auth_and_people.py` — nomes, vazio e teto.

## 🗑️ Arquivos removidos

- —

## 🔗 Dependências adicionadas

- —

## ⚠️ Decisões tomadas

- Quem não existe fica de fora da resposta. A rota não devolve senha, e-mail, CPF nem `auth_version`.

## 🧪 Como testar

1. No Swagger `http://127.0.0.1:8001/docs`, chamar `POST /api/v1/internal/people/lookup` com `X-Api-Key`.
2. Corpo `{ "person_ids": [1, 1, 999999] }`: a pessoa 1 uma vez, o id ausente de fora, só `person_id` e `full_name`.
3. Corpo vazio devolve lista vazia. Com 101 ids, a resposta é 400.
4. `GET /api/v1/internal/people/1` continua com nome, e-mail, CPF e `auth_version`.

## ❗ Problemas encontrados

- —
