# Log — sessão do admin

**Data:** 2026-10-01  
**Sessão:** correção

---

## ✅ O que foi feito

- O access token passa a ser aceito com `sub` numérico. A lista de pessoas deixava de responder 401 logo depois do login

## 📁 Arquivos criados

- `_logs/2026-10-01_sessao-admin.md` — este log

## ✏️ Arquivos modificados

- `backend/app/core/security.py` — decode do access ignora a exigência de `sub` texto
- `backend/tests/test_auth_and_people.py` — o login decodifica o access e confere o `sub`

## 🗑️ Arquivos removidos

- —

## 🔗 Dependências adicionadas

- —

## ⚠️ Decisões tomadas

- O `sub` continua número, como no contrato. A checagem da biblioteca é que foi desligada

## 🐛 Problemas encontrados e soluções

- Login gravava o cookie, mas `GET /people` e `GET /auth/me` respondiam 401. O `python-jose` recusava `sub` inteiro com "Subject must be a string."

## 📌 Pendências / próximos passos

- Entrar de novo em `http://localhost:5173` e confirmar a lista de pessoas
