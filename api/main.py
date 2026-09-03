from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os
from pathlib import Path

from api.services import router as services_router
from api.availability import router as availability_router
from api.appointments import router as appointments_router
from api.appointments_list import router as appointments_list_router
from api.appointments_manage import router as appointments_manage_router
from api.clients import router as clients_router
from api.returns import router as returns_router
from routes.whatsapp import router as whatsapp_router
from api.public import router as public_router
from api.client_protocol import router as client_protocol_router
from api.admin import router as admin_router


BASE_DIR = Path(__file__).resolve().parent.parent


app = FastAPI(
    title="Jeni Santos Nails",
    description="API do sistema de agendamento da Jeni Santos Nails",
    version="1.0.0",
)


app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ["ADMIN_SECRET_KEY"],
    same_site="lax",
)


app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static",
)


app.include_router(services_router)
app.include_router(availability_router)
app.include_router(appointments_router)
app.include_router(appointments_list_router)
app.include_router(appointments_manage_router)
app.include_router(clients_router)
app.include_router(returns_router)
app.include_router(whatsapp_router)
app.include_router(public_router)
app.include_router(client_protocol_router)
app.include_router(admin_router)


@app.get("/")
def home():
    return {
        "message": "Jeni Santos Nails API funcionando!",
        "status": "online",
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }
