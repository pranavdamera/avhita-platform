import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from app.routers import patients, practitioners


def _run_migrations() -> None:
    from alembic import command
    from alembic.config import Config

    cfg = Config(str(Path(__file__).parent / "alembic.ini"))
    command.upgrade(cfg, "head")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run in a thread so asyncio.run() inside alembic's env.py gets its own loop
    await asyncio.to_thread(_run_migrations)
    yield


app = FastAPI(title="Avhita Clinic EHR", version="0.1.0", lifespan=lifespan)

app.include_router(patients.router, prefix="/patients")
app.include_router(practitioners.router, prefix="/practitioners")


@app.get("/health")
def health():
    return {"status": "ok", "service": "clinic-ehr"}
