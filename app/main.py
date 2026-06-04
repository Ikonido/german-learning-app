from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, vocab
from app.core.config import get_settings
from app.db.session import Base, engine
from app.models import *  # noqa: F401, F403  - ensure all models are registered

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend for learning German language. Optimized schema for nouns (gender + plural) and verbs (3 principal forms + auxiliary).",
)

# CORS - adjust for your frontend later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(vocab.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": settings.PROJECT_NAME}


# Optional: create tables on startup (useful for dev, use Alembic in prod)
@app.on_event("startup")
def on_startup():
    # For initial development only. In real projects run `alembic upgrade head`
    # Base.metadata.create_all(bind=engine)
    pass
