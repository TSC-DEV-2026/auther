# Log — setup inicial

**Data:** 2026-09-30  
**Sessão:** setup inicial

---

## ✅ O que foi feito

- Recriado o Auther com a raiz em `backend/`, `frontend/` e `mobile/`
- API de pessoas, sessão do admin (e-mail e senha, só `is_platform_admin`) e rotas `/internal/*` para os sistemas de negócio
- Site de administração com login, consulta de pessoas, convite, esqueci a senha, definição de senha, verificação de e-mail e troca de senha
- `mobile/` vazia, só com `.gitkeep`
- Testes pytest sem banco real (21 passaram) e build de produção do site

## 📁 Arquivos criados

- `README.md` — como subir a API e o site
- `.gitignore` — Python, Node e segredos; `_logs/` continua versionado
- `docker-compose.prod.yml` — API e nginx só para produção
- `mobile/.gitkeep` — a pasta existe e não tem aplicativo
- `backend/` — FastAPI, Alembic, modelos de pessoa, refresh e token de e-mail, services, rotas `/api/v1` e testes
- `frontend/` — Vite, login do admin e telas de pessoas
- `_logs/2026-09-30_setup-inicial.md` — este log

## ✏️ Arquivos modificados

- —

## 🗑️ Arquivos removidos

- —

## 🔗 Dependências adicionadas

- API: FastAPI, SQLAlchemy, PostgreSQL (psycopg), Alembic, Pydantic, python-jose, passlib/bcrypt, slowapi, pytest
- Site: React, Vite, TypeScript, Tailwind, Radix (button/label), Axios, Zustand, Lucide

## ⚠️ Decisões tomadas

- Senha com 8 a 72 caracteres
- Token de definir senha vale 60 minutos; token de verificar e-mail vale 24 horas
- Rate limit de 10 por minuto em login, refresh, forgot, reset, change, verify, reenvio e convite
- Troca de e-mail zera `email_verified` e dispara uma verificação nova
- `auth_version` é conferido no refresh. O access já emitido vale até expirar
- A primeira senha do convite não sobe `auth_version`. Redefinir uma senha que já existia sobe
- O admin da sessão não desativa nem exclui a si mesmo, e o último admin da plataforma não é excluído
- E-mail não verificado não impede o login nem o `verify`
- `mobile/` fica vazia de propósito

## 🐛 Problemas encontrados e soluções

- O primeiro `npm install` falhou com a pasta `node_modules` travada. A reinstalação concluiu e o `npm run build` gerou o site
- O site não foi percorrido no browser: a API precisa de PostgreSQL e de um `.env` preenchido

## 📌 Pendências / próximos passos

- Criar o banco `auther`, copiar `backend/.env.example` para `backend/.env` e preencher seed e SMTP
- Rodar `alembic upgrade head` dentro de `backend/`
- Subir a API na porta 8001 e o site na 5173 e percorrer login, busca de pessoas, convite e esqueci a senha
