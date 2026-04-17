from fastapi import FastAPI

app = FastAPI(title="Avhita ABDM Gateway", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "abdm-gateway"}


# TODO: routers
# app.include_router(abha.router, prefix="/abha")           # ABHA ID creation & verification
# app.include_router(hip.router, prefix="/hip")             # Health Information Provider flows
# app.include_router(hiu.router, prefix="/hiu")             # Health Information User flows
# app.include_router(consent.router, prefix="/consent")     # consent artifact management
