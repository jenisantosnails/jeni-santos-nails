from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.database import get_db
from models.appointment import Appointment
from models.client import Client
from models.service import Service


router = APIRouter(
    prefix="/appointments",
    tags=["Agendamentos"],
)


@router.get("/")
def list_appointments(
    db: Session = Depends(get_db),
    appointment_date: str | None = Query(
        default=None,
        description="Data no formato YYYY-MM-DD",
    ),
):
    query = (
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
            Appointment.status != "cancelled"
        )
    )

    # ==========================================
    # FILTRAR POR DATA
    # ==========================================

    if appointment_date:
        query = query.filter(
            Appointment.start_at >= f"{appointment_date} 00:00:00",
            Appointment.start_at <= f"{appointment_date} 23:59:59",
        )

    results = (
        query
        .order_by(Appointment.start_at)
        .all()
    )

    # ==========================================
    # MONTAR RESPOSTA
    # ==========================================

    return [
        {
            "id": appointment.id,

            "client": {
                "id": client.id,
                "name": client.name,
                "phone": client.phone,
                "email": client.email,
            },

            "service": {
                "id": service.id,
                "name": service.name,
                "price": service.price,
                "duration_minutes": service.duration_minutes,
            },

            "start_at": appointment.start_at,
            "end_at": appointment.end_at,

            "status": appointment.status,

            "payment": {
                "method": appointment.payment_method,
                "status": appointment.payment_status,
            },

            "return": {
                "type": appointment.return_type,
                "date": appointment.return_date,
            },

            "completed_at": appointment.completed_at,

            "notes": appointment.notes,
        }

        for appointment, client, service in results
    ]