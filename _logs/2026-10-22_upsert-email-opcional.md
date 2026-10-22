# Log — upsert aceita CPF existente sem e-mail

**Data:** 2026-10-22  
**Sessão:** apoio ao cadastro de funcionário do sistemaponto

---

## ✅ O que foi feito

- `POST /internal/people` aceita corpo sem e-mail quando o CPF já existe
- CPF novo sem e-mail responde 400 com "Informe o e-mail"
- CPF existente continua devolvendo o mesmo `person_id`, sem trocar e-mail nem senha

## 📁 Arquivos criados

- `_logs/2026-10-22_upsert-email-opcional.md` — este registro

## ✏️ Arquivos modificados

- `backend/app/schemas/auth.py` — `email` opcional em `InternalPersonIn`
- `backend/app/services/person_service.py` — recusa criação sem e-mail
- `backend/app/api/routes/internal.py` — descrição do upsert
- `backend/tests/test_auth_and_people.py` — CPF novo sem e-mail e CPF existente sem e-mail

## 🗑️ Arquivos removidos

- —

## 🔗 Dependências adicionadas

- —

## ⚠️ Decisões tomadas

- O e-mail segue obrigatório só na criação da pessoa, porque o convite precisa de destino. Pessoa já cadastrada não depende do e-mail enviado pelo sistema de negócio

## 🐛 Problemas encontrados e soluções

- —

## 📌 Pendências / próximos passos

- —
