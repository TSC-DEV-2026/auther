# Log — docker de produção

**Data:** 2026-11-27  
**Sessão:** compose do auther na rede do Caddy

---

## ✅ O que foi feito

- O compose de produção deixa de publicar a porta 80 no host.
- API e site entram na rede `zioncor-prod_zioncor`, com os nomes `auther-api` e `auther-web`.
- O nginx encaminha `/api` para `auther-api` e repassa o HTTPS que o Caddy já terminou.
- O `deploy.sh` atualiza só este repositório. O bloco do Caddy fica em `deploy/auther.caddy` e não é recarregado pelo script.

## 📁 Arquivos criados

- `backend/.dockerignore`
- `frontend/.dockerignore`
- `deploy/auther.caddy`
- `deploy.sh`
- `_logs/2026-11-27_docker-de-producao.md`

## ✏️ Arquivos modificados

- `docker-compose.prod.yml`
- `frontend/nginx.conf`

## 🗑️ Arquivos removidos

- —

## 🔗 Dependências adicionadas

- —

## ⚠️ Decisões tomadas

- Desenvolvimento local continua no Vite e no uvicorn. Estes arquivos são só de produção.
- O `.env` de produção não entra no Git.

## 🐛 Problemas encontrados e soluções

- —

## 📌 Pendências / próximos passos

- No servidor, trocar o compose avulso pelo `docker-compose.prod.yml` desta branch depois do merge.
