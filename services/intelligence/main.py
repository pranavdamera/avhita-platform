from fastapi import FastAPI

app = FastAPI(title="Avhita Intelligence", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "intelligence"}


# TODO: routers
# app.include_router(soap.router, prefix="/soap")           # generate SOAP note from encounter
# app.include_router(risk.router, prefix="/risk")           # patient risk scoring
# app.include_router(differential.router, prefix="/ddx")    # differential diagnosis suggestions
