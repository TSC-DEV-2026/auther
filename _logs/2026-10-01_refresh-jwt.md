# Log — refresh JWT

**Data:** 2026-10-01  
**Sessão:** feature

---

## ✅ O que foi feito

- O refresh da sessão passou a ser JWT, com `typ` e `jti`. O banco continua gravando só o hash

## 📁 Arquivos criados

- `_logs/2026-10-01_refresh-jwt.md` — este log

## ✏️ Arquivos modificados

- `backend/app/core/security.py` — emite e lê access e refresh como JWT
- `backend/app/services/auth_service.py` — a renovação valida o JWT e o hash
- `backend/app/api/routes/auth.py` — a descrição da rota de refresh
- `backend/tests/test_auth_and_people.py` — o login confere os dois JWT e o access não renova sessão

## 🗑️ Arquivos removidos

- —

## 🔗 Dependências adicionadas

- —

## ⚠️ Decisões tomadas

- `typ` separa access e refresh. O hash do JWT no banco segue sendo o que revoga e rotaciona
- Token de e-mail continua opaco

## 🐛 Problemas encontrados e soluções

- —

## 📌 Pendências / próximos passos

- Entrar de novo no site. O refresh antigo, opaco, deixa de valer
