from fastapi import FastAPI

from routes.services import router as services_router
from routes.whatsapp import router as whatsapp_router


app = FastAPI(
    title="Jeni Santos Nails",
    description="Sistema de agendamento da Jeni Santos Nails",
    version="1.0.0"
)


app.include_router(services_router)
app.include_router(whatsapp_router)


@app.get("/")
def home():
    return {
        "message": "Jeni Santos Nails API funcionando!"
    }


@app.get("/teste")
def teste():
    return {
        "message": "Teste realizado com sucesso!"
    }
