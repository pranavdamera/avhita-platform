from fastapi import FastAPI

from app.routers import rpm

app = FastAPI(title="Avhita RPM Bridge", version="0.1.0")

app.include_router(rpm.router, prefix="/rpm-bridge")


@app.get("/health")
def health():
    return {"status": "ok", "service": "rpm-bridge"}
