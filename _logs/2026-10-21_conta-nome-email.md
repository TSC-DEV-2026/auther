# Log — nome e e-mail pela conta do sistema

**Data:** 2026-10-21  
**Sessão:** apoio ao ponto 21 do sistema ponto

---

## ✅ O que foi feito

- O estado interno da pessoa passa a devolver o CPF
- `PUT /api/v1/internal/people/{id}` grava nome e e-mail
- O CPF não muda nessa rota
- Troca de e-mail marca a verificação como pendente e reenvia o link

## 📁 Arquivos criados

- —

## ✏️ Arquivos modificados

- `backend/app/schemas/auth.py` — CPF no estado e corpo da atualização
- `backend/app/api/routes/internal.py` — leitura do CPF e atualização
- `backend/app/services/person_service.py` — grava nome e e-mail sem mexer no CPF
- `backend/tests/test_auth_and_people.py` — nome, e-mail e CPF intacto

## 🗑️ Arquivos removidos

- —

## 🔗 Dependências adicionadas

- —

## ⚠️ Decisões tomadas

- A rota interna não aceita CPF nem desativação

## 🐛 Problemas encontrados

- —

## 📌 Pendências

- —
