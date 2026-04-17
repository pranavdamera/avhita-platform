from fastapi import FastAPI

from app.routers import patients

app = FastAPI(title="Avhita Clinic EHR", version="0.1.0")

app.include_router(patients.router, prefix="/patients")


@app.get("/health")
def health():
    return {"status": "ok", "service": "clinic-ehr"}
