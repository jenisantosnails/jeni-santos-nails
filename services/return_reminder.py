from datetime import datetime
from sqlalchemy.orm import Session

from models.appointment import Appointment
from models.client import Client
from models.service import Service
from services.time import now_local


REMINDER_WINDOW_DAYS = 5


def get_pending_return_reminders(
    db: Session,
    days_ahead: int = REMINDER_WINDOW_DAYS,
):
    """
    Busca clientes que possuem retorno próximo
    e ainda não receberam o lembrete.

    O envio do WhatsApp NÃO acontece aqui.
    Esta função apenas identifica quem precisa receber.
    """

    now = now_local().replace(tzinfo=None)

    end_date = now.replace(
        hour=23,
        minute=59,
        second=59,
        microsecond=999999,
    )

    end_date = end_date.fromordinal(
        end_date.toordinal() + days_ahead
    )

    appointments = (
        db.query(Appointment)
        .join(
            Client,
            Appointment.client_id == Client.id,
        )
        .join(
            Service,
            Appointment.service_id == Service.id,
        )
        .filter(
            Appointment.status == "completed",
            Appointment.return_date.is_not(None),
            Appointment.return_date >= now,
            Appointment.return_date <= end_date,
            Appointment.reminder_sent_at.is_(None),
            Client.active == True,
        )
        .order_by(
            Appointment.return_date.asc()
        )
        .all()
    )

    return appointments


def build_return_reminder_message(
    appointment: Appointment,
):
    """
    Monta a mensagem que futuramente será enviada
    pelo WhatsApp.
    """

    client = appointment.client
    service = appointment.service

    return_date = appointment.return_date.strftime(
        "%d/%m/%Y"
    )

    message = (
        f"Olá, {client.name}! 💅\n\n"
        f"Passando para lembrar que seu retorno para "
        f"{service.name} está previsto para {return_date}.\n\n"
        "Se quiser agendar seu horário, é só falar comigo. "
        "Vou ficar feliz em te atender novamente! 💕"
    )

    return message


def prepare_return_reminders(
    db: Session,
    days_ahead: int = REMINDER_WINDOW_DAYS,
):
    """
    Busca os retornos pendentes e prepara as informações
    necessárias para o envio.

    Importante:
    Esta função NÃO marca o lembrete como enviado.

    O reminder_sent_at só deve ser preenchido depois
    que o WhatsApp confirmar que a mensagem foi enviada.
    """

    appointments = get_pending_return_reminders(
        db=db,
        days_ahead=days_ahead,
    )

    reminders = []

    for appointment in appointments:
        client = appointment.client

        reminders.append(
            {
                "appointment_id": appointment.id,
                "client_id": client.id,
                "client_name": client.name,
                "phone": client.phone,
                "return_date": appointment.return_date,
                "service": appointment.service.name,
                "message": build_return_reminder_message(
                    appointment
                ),
            }
        )

    return reminders