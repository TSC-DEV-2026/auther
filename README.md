# Auther

Autenticador global. Uma base de pessoas. Os sistemas de negócio validam CPF e senha aqui. O admin entra no site com e-mail e senha e consulta se a pessoa está cadastrada.

```
backend/     API
frontend/    site de administração
mobile/      vazia — este autenticador não tem aplicativo
```

## Desenvolvimento

PostgreSQL local. Não use Docker para desenvolver.

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn main:app --reload --port 8001
```

O `.env` precisa de `SEED_ADMIN_CPF`, `SEED_ADMIN_EMAIL`, `SEED_ADMIN_PASSWORD` e `SEED_ADMIN_FULL_NAME` para criar o admin na primeira subida. SMTP precisa estar preenchido para convite, verificação e esqueci a senha.

```bash
cd frontend
npm install
npm run dev
```

O site fica em `http://localhost:5173` e fala com a API pelo proxy `/api`.

## Produção

O `docker-compose.prod.yml` sobe a API e o nginx no mesmo host, com o site e `/api` juntos. Desenvolvimento continua na máquina.
