# SWE23 AI Assistant

RAG-based AI assistant for the SUST Software Engineering 2023 batch.
Admin (CR) uploads documents (notices, routines, resources); students
ask questions in natural language and get answers grounded in those
documents, with source citations.

## Architecture

```
Next.js (frontend) --HTTP/JWT--> FastAPI (backend) --SQL--> PostgreSQL
                                        |
                                        +--> ChromaDB (embedded, on-disk)
                                        |
                                        +--> Gemini API (chat + embeddings)
```

- **Postgres** = system of record: users, document metadata, chat history, unknown questions.
- **ChromaDB** = derived, searchable knowledge: chunked + embedded document text.
- See the backend `app/services/` folder for the RAG pipeline itself (ingestion + retrieval).

## Project structure

```
swe23-ai-assistant/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app entrypoint
│   │   ├── config.py        # env-based settings
│   │   ├── database.py      # SQLAlchemy engine/session
│   │   ├── seed.py          # creates the first admin account
│   │   ├── models/          # SQLAlchemy tables
│   │   ├── schemas/         # Pydantic request/response shapes
│   │   ├── core/            # security (JWT, hashing) + auth dependencies
│   │   ├── services/        # chunking, embeddings, vector store, RAG, ingestion
│   │   └── routers/         # API endpoints: /auth, /chat, /admin, /health
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── app/                 # Next.js App Router pages (login, chat)
│   ├── lib/api.ts           # fetch wrapper with JWT attached
│   ├── package.json
│   ├── Dockerfile
│   └── .env.local.example
└── docker-compose.yml        # runs postgres + backend + frontend together, locally
```

## Running locally

### 1. Configure environment variables

```bash
cd backend
cp .env.example .env
# edit .env: paste your real GEMINI_API_KEY, and set JWT_SECRET_KEY to
# a long random string, e.g. generate one with:
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

```bash
cd ../frontend
cp .env.local.example .env.local
```

### 2. Start everything with Docker Compose

From the project root:

```bash
docker compose up --build
```

This starts Postgres (port 5432), the backend (port 8000), and the frontend (port 3000).

### 3. Create your admin account

The first admin has to be created manually (there's no signup flow, by design). With the containers running, in a new terminal:

```bash
docker compose exec backend python -m app.seed
```

Follow the prompts (email, name, password). This is the account you'll use to log in and upload documents.

### 4. Try it out

Everything is now driven from the frontend — no Swagger needed for day-to-day use.

- **http://localhost:3000** — log in with the admin account you just created. Admins are routed automatically to **/admin**; students are routed to **/chat**.
- In the **Admin dashboard**:
  - **Upload Documents** tab: pick a `.pdf`, `.docx`, `.txt`, or `.md` file, optionally set a course code, upload. You'll see its status (`processing` → `processed`/`failed`) and any error message right in the list.
  - **Create Students** tab: create accounts for your batch (student ID, name, email, temporary password) — this is the only way students get access, by design.
  - **Unanswered Questions** tab: shows questions the AI couldn't confidently answer, so you know what to add to the knowledge base next.
- Click **"Go to chat"** in the admin header to test the chat yourself, or create a student account and log in as them in a private/incognito window.

API docs at **http://localhost:8000/docs** still exist and are useful for debugging or scripting, but aren't required for normal use anymore.

## Running without Docker (plain venv, for debugging)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# You'll need a local Postgres running, or point DATABASE_URL at one.
uvicorn app.main:app --reload --port 8000
```

```bash
cd frontend
npm install
npm run dev
```

## Deployment

### Backend -> Railway

1. Push this repo to GitHub.
2. In Railway: New Project -> Deploy from GitHub repo -> select this repo, set **root directory to `backend`**.
3. Add a PostgreSQL plugin in Railway (it auto-injects `DATABASE_URL` — but note our var is named `DATABASE_URL` too, so just confirm it matches; Railway's Postgres plugin sets this automatically in most templates, otherwise copy its connection string into your service's `DATABASE_URL` variable).
4. Add environment variables in Railway's dashboard: `GEMINI_API_KEY`, `JWT_SECRET_KEY`, `CORS_ORIGINS` (set this to your Vercel frontend URL once you have it).
5. Railway builds from the `Dockerfile` automatically. It sets `$PORT` itself — our Dockerfile's CMD already respects that.
6. **Important**: Railway's filesystem is ephemeral on redeploy unless you attach a **Volume**. Attach a volume mounted at `/app/chroma_data` and another at `/app/uploads` in the Railway service settings, or your knowledge base will vanish on every redeploy.
7. Once deployed, run the seed script via Railway's shell (Settings -> the "..." menu -> shell, or `railway run python -m app.seed` via the Railway CLI).

### Frontend -> Vercel

1. In Vercel: New Project -> import this repo, set **root directory to `frontend`**.
2. Add environment variable: `NEXT_PUBLIC_API_URL` = your Railway backend's public URL.
3. Deploy. Vercel handles Next.js builds natively — no Dockerfile needed here.
4. Go back to Railway and set `CORS_ORIGINS` to your new Vercel URL (e.g. `https://swe23-ai.vercel.app`), redeploy the backend.

## What's built vs. what's next

**Built (this milestone):** auth (JWT, admin creates students, role-based redirect), a full admin dashboard (upload documents with live status, create student accounts, review unanswered questions), the full RAG ingestion pipeline (extract -> chunk -> embed -> store), and chat with retrieval + grounding + source citation + sliding-window memory + unknown-question logging.

**Deliberately not built yet** (from your original feature list — next milestones, one at a time):
- OCR for image/screenshot uploads
- Attendance/CGPA calculators, assignment tracker
- AI note/quiz/flashcard generators
- Notification center, broadcast announcements
- Background task queue for ingestion (currently synchronous — fine for small files, will feel slow for large PDFs)
- Alembic migrations (currently `create_all` — fine until you need to change existing table columns)
- Automated tests, CI/CD, logging/monitoring, rate limiting

We'll build these incrementally, same theory-first process as everything so far.
