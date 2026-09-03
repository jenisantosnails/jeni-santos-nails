from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database.database import get_db
from models.appointment import Appointment
from models.client import Client
from models.service import Service
from services.time import now_local


router = APIRouter(
    prefix="/appointments",
    tags=["Retornos"],
)


# ==========================================
# CONFIGURAÇÃO
# ==========================================

DEFAULT_RETURN_REMINDER_DAYS = 5


# ==========================================
# RETORNOS PRÓXIMOS
# ==========================================

@router.get("/returns/upcoming")
def upcoming_returns(
    db: Session = Depends(get_db),
    days_ahead: int = Query(
        default=DEFAULT_RETURN_REMINDER_DAYS,
        ge=0,
        le=30,
        description="Quantidade de dias da janela de lembrete.",
    ),
):
    # SQLite armazena os horários sem timezone.
    # Mantemos o horário local de Maceió,
    # removendo somente a informação do timezone
    # para comparar corretamente com o banco.

    now = now_local().replace(tzinfo=None)

    start_date = now
    end_date = now + timedelta(days=days_ahead)

    # ==========================================
    # BUSCAR RETORNOS
    # ==========================================

    results = (
        db.query(
            Appointment,
            Client,
            Service,
        )
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
            Appointment.return_date >= start_date,
            Appointment.return_date <= end_date,
            Appointment.reminder_sent_at.is_(None),
            Client.active == True,
        )
        .order_by(
            Appointment.return_date
        )
        .all()
    )

    # ==========================================
    # MONTAR RESPOSTA
    # ==========================================

    response = []

    for appointment, client, service in results:

        remaining = (
            appointment.return_date - now
        )

        days_remaining = max(
            0,
            remaining.days
        )

        response.append(
            {
                "appointment_id": appointment.id,

                "client": {
                    "id": client.id,
                    "name": client.name,
                    "phone": client.phone,
                    "email": client.email,
                },

                "service": {
                    "id": service.id,
                    "name": service.name,
                },

                "completed_at": appointment.completed_at,

                "return": {
                    "type": appointment.return_type,
                    "date": appointment.return_date,
                    "days_remaining": days_remaining,
                },

                "reminder": {
                    "eligible": True,
                    "sent_at": appointment.reminder_sent_at,
                },
            }
        )

    return {
        "reminder_window_days": days_ahead,
        "count": len(response),
        "returns": response,
    }


# ==========================================
# MARCAR LEMBRETE COMO ENVIADO
# ==========================================

@router.patch("/{appointment_id}/return-reminder-sent")
def mark_return_reminder_sent(
    appointment_id: int,
    db: Session = Depends(get_db),
):
    # ==========================================
    # BUSCAR AGENDAMENTO
    # ==========================================

    appointment = (
        db.query(Appointment)
        .filter(
            Appointment.id == appointment_id
        )
        .first()
    )

    if appointment is None:
        raise HTTPException(
            status_code=404,
            detail="Agendamento não encontrado.",
        )

    # ==========================================
    # VERIFICAR RETORNO
    # ==========================================

    if appointment.return_date is None:
        raise HTTPException(
            status_code=409,
            detail="Este agendamento não possui retorno definido.",
        )

    # ==========================================
    # EVITAR DUPLICIDADE
    # ==========================================

    if appointment.reminder_sent_at is not None:
        return {
            "message": "O lembrete deste retorno já foi registrado como enviado.",
            "appointment": {
                "id": appointment.id,
                "reminder_sent_at": appointment.reminder_sent_at,
            },
        }

    # ==========================================
    # REGISTRAR ENVIO
    # ==========================================

    sent_at = now_local().replace(tzinfo=None)

    appointment.reminder_sent_at = sent_at

    db.commit()
    db.refresh(appointment)

    # ==========================================
    # RESPOSTA
    # ==========================================

    return {
        "message": "Lembrete de retorno registrado como enviado.",
        "appointment": {
            "id": appointment.id,
            "return_date": appointment.return_date,
            "reminder_sent_at": appointment.reminder_sent_at,
        },
    }