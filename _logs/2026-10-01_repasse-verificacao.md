# Log — repasse de verificação

**Data:** 2026-10-01  
**Sessão:** feature

---

## ✅ O que foi feito

- `GET /internal/people/{id}` passa a devolver também `full_name` e `email`, para a sessão do sistema de negócio
- Rotas internal de confirmação de e-mail e de reenvio, com `redirect_url` allowlisted
- Allowlist local passou a incluir `http://localhost:5174`, origem do sistema base

## 📁 Arquivos criados

- —

## ✏️ Arquivos modificados

- `backend/app/schemas/auth.py` — estado da pessoa e corpos de verify/resend
- `backend/app/api/routes/internal.py` — as duas rotas e os campos novos no estado
- `backend/.env.example` — allowlist com a origem do sistema base
- `backend/.env` — a mesma allowlist no ambiente local, fora do git

## 🗑️ Arquivos removidos

- —

## 🔗 Dependências adicionadas

- —

## ⚠️ Decisões tomadas

- O estado internal ganhou nome e e-mail porque o sistema de negócio não grava esses campos e o `/auth/me` precisa mostrá-los
- Verify e resend internal seguem o mesmo repasse já usado em esqueci a senha e troca de senha

## 🐛 Problemas encontrados e soluções

- —

## 📌 Pendências / próximos passos

- —
