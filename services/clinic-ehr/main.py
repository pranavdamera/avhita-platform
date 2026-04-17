from fastapi import FastAPI

app = FastAPI(title="Avhita Clinic EHR", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "clinic-ehr"}


# TODO: routers
# app.include_router(patients.router, prefix="/patients")
# app.include_router(encounters.router, prefix="/encounters")
# app.include_router(prescriptions.router, prefix="/prescriptions")
# app.include_router(fhir.router, prefix="/fhir/r4")
