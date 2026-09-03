from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import PlainTextResponse

router = APIRouter(
    prefix="/webhook",
    tags=["WhatsApp"]
)

VERIFY_TOKEN = "jeni_santos_nails_whatsapp_2026"


@router.get("")
async def verify_webhook(request: Request):
    params = request.query_params

    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(content=challenge)

    raise HTTPException(status_code=403, detail="Token de verificacao invalido")


@router.post("")
async def receive_webhook(request: Request):
    data = await request.json()

    print("WEBHOOK WHATSAPP RECEBIDO:")
    print(data)

    return {"status": "ok"}
