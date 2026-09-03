from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database.database import get_db
from models.service import Service
from services.schedule import generate_available_times


router = APIRouter(
    prefix="/availability",
    tags=["Disponibilidade"],
)


@router.get("/")
def get_available_times(
    appointment_date: date = Query(
        ...,
        description="Data desejada no formato AAAA-MM-DD",
    ),
    service_id: int = Query(
        ...,
        description="ID do serviço desejado",
    ),
    db: Session = Depends(get_db),
):
    """
    Retorna os horários disponíveis para um serviço
    em uma determinada data.
    """

    service = (
        db.query(Service)
        .filter(
            Service.id == service_id,
            Service.active == True,
        )
        .first()
    )

    if service is None:
        raise HTTPException(
            status_code=404,
            detail="Serviço não encontrado.",
        )

    available_times = generate_available_times(
        db=db,
        appointment_date=appointment_date,
        service=service,
    )

    return {
        "date": appointment_date.isoformat(),
        "service": {
            "id": service.id,
            "name": service.name,
            "price": service.price,
            "duration_minutes": service.duration_minutes,
        },
        "available_times": available_times,
        "total": len(available_times),
    }