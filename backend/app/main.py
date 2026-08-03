from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers import health, auth, chat, admin

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SWE23 AI Assistant API",
    version="0.1.0",
)

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]

print("CORS Origins:", origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/cors-test")
def cors_test():
    return {"status": "ok"}

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(admin.router)