from fastapi import FastAPI

app = FastAPI(title="Avhita RPM Bridge", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "rpm-bridge"}


# TODO: routers
# app.include_router(ingest.router, prefix="/ingest")   # receives RPM telemetry from avhita-ai
# app.include_router(alerts.router, prefix="/alerts")   # threshold breach → EHR observation
