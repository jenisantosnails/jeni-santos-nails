import os

import requests


WHATSAPP_API_URL = os.getenv(
    "WHATSAPP_API_URL",
    ""
)

WHATSAPP_ACCESS_TOKEN = os.getenv(
    "WHATSAPP_ACCESS_TOKEN",
    ""
)


def send_whatsapp_message(
    phone: str,
    message: str,
) -> dict:

    if not WHATSAPP_API_URL:
        return {
            "success": False,
            "sent": False,
            "error": "WHATSAPP_API_URL não configurada.",
        }

    if not WHATSAPP_ACCESS_TOKEN:
        return {
            "success": False,
            "sent": False,
            "error": "WHATSAPP_ACCESS_TOKEN não configurado.",
        }

    phone = "".join(
        character
        for character in phone
        if character.isdigit()
    )

    if not phone:
        return {
            "success": False,
            "sent": False,
            "error": "Número de telefone inválido.",
        }

    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {
            "body": message,
        },
    }

    try:
        response = requests.post(
            WHATSAPP_API_URL,
            headers=headers,
            json=payload,
            timeout=30,
        )

        if response.ok:
            return {
                "success": True,
                "sent": True,
                "response": response.json(),
            }

        return {
            "success": False,
            "sent": False,
            "status_code": response.status_code,
            "error": response.text,
        }

    except requests.RequestException as error:
        return {
            "success": False,
            "sent": False,
            "error": str(error),
        }