from datetime import datetime, time

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.database import get_db
from models.appointment import Appointment
from models.client import Client
from models.client_protocol import ClientProtocol
from models.service import Service
from services.availability import check_availability
from services.time import now_local


router = APIRouter(
    prefix="/appointments",
    tags=["Agendamentos"],
)


VALID_RETURN_TYPES = {
    "none",
    "15_days",
    "21_days",
    "25_days",
    "30_days",
    "custom",
}


class ClientProtocolData(BaseModel):
    has_allergy_or_sensitivity: bool = False
    allergy_or_sensitivity_details: str | None = None

    has_current_issue: bool = False
    current_issue_details: str | None = None

    has_previous_reaction: bool = False
    previous_reaction_details: str | None = None

    has_diabetes: bool = False

    observations: str | None = None


class AppointmentCreate(BaseModel):
    client_name: str
    client_phone: str
    client_email: str | None = None

    service_id: int
    start_at: datetime

    payment_method: str | None = None
    notes: str | None = None

    return_type: str = "none"
    return_date: datetime | None = None

    policies_accepted: bool = False

    protocol: ClientProtocolData | None = None


@router.post("/")
def create_appointment(
    data: AppointmentCreate,
    db: Session = Depends(get_db),
):
    if not data.policies_accepted:
        raise HTTPException(
            status_code=422,
            detail=(
                "É necessário aceitar as políticas "
                "de atendimento para realizar o agendamento."
            ),
        )

    if data.return_type not in VALID_RETURN_TYPES:
        raise HTTPException(
            status_code=422,
            detail=(
                "Tipo de retorno inválido. "
                "Use: none, 15_days, 21_days, "
                "25_days, 30_days ou custom."
            ),
        )

    if data.return_type == "custom":
        if data.return_date is None:
            raise HTTPException(
                status_code=422,
                detail=(
                    "Para um retorno personalizado, "
                    "é necessário informar a data do retorno."
                ),
            )

        if data.return_date.date() <= data.start_at.date():
            raise HTTPException(
                status_code=422,
                detail=(
                    "A data do retorno personalizado "
                    "deve ser posterior à data do atendimento."
                ),
            )

    elif data.return_date is not None:
        raise HTTPException(
            status_code=422,
            detail=(
                "A data do retorno só deve ser informada "
                "quando o tipo de retorno for 'custom'."
            ),
        )

    service = (
        db.query(Service)
        .filter(
            Service.id == data.service_id,
            Service.active == True,
        )
        .first()
    )

    if service is None:
        raise HTTPException(
            status_code=404,
            detail="Serviço não encontrado.",
        )

    public_start = time(9, 0)
    public_end = time(20, 0)

    available, message, end_at = check_availability(
        db=db,
        start_at=data.start_at,
        duration_minutes=service.duration_minutes,
    )

    if data.start_at.weekday() < 5:
        if data.start_at.time() < public_start:
            raise HTTPException(
                status_code=409,
                detail="A agenda pública começa às 09:00.",
            )

        if data.start_at.time() >= public_end:
            raise HTTPException(
                status_code=409,
                detail="A agenda pública está disponível até 20:00.",
            )

        if end_at.time() > public_end or end_at.date() != data.start_at.date():
            raise HTTPException(
                status_code=409,
                detail="O serviço ultrapassa o limite da agenda pública, que termina às 20:00.",
            )

    if not available:
        raise HTTPException(
            status_code=409,
            detail=message,
        )

    client = (
        db.query(Client)
        .filter(Client.phone == data.client_phone)
        .first()
    )

    if client is None:
        client = Client(
            name=data.client_name,
            phone=data.client_phone,
            email=data.client_email,
        )

        db.add(client)
        db.flush()

    else:
        if not client.active:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Esta cliente está inativa e não pode "
                    "realizar um novo agendamento."
                ),
            )

        client.name = data.client_name

        if data.client_email:
            client.email = data.client_email

    policies_accepted_at = now_local()

    appointment_return_date = None

    if data.return_type == "custom":
        appointment_return_date = data.return_date

    protocol = None

    if data.protocol is not None:
        protocol = (
            db.query(ClientProtocol)
            .filter(
                ClientProtocol.client_id == client.id
            )
            .first()
        )

        if protocol is None:
            protocol = ClientProtocol(
                client_id=client.id,

                has_allergy_or_sensitivity=(
                    data.protocol.has_allergy_or_sensitivity
                ),
                allergy_or_sensitivity_details=(
                    data.protocol.allergy_or_sensitivity_details
                ),

                has_current_issue=(
                    data.protocol.has_current_issue
                ),
                current_issue_details=(
                    data.protocol.current_issue_details
                ),

                has_previous_reaction=(
                    data.protocol.has_previous_reaction
                ),
                previous_reaction_details=(
                    data.protocol.previous_reaction_details
                ),

                has_diabetes=data.protocol.has_diabetes,

                observations=data.protocol.observations,
            )

            db.add(protocol)

        else:
            protocol.has_allergy_or_sensitivity = (
                data.protocol.has_allergy_or_sensitivity
            )

            protocol.allergy_or_sensitivity_details = (
                data.protocol.allergy_or_sensitivity_details
            )

            protocol.has_current_issue = (
                data.protocol.has_current_issue
            )

            protocol.current_issue_details = (
                data.protocol.current_issue_details
            )

            protocol.has_previous_reaction = (
                data.protocol.has_previous_reaction
            )

            protocol.previous_reaction_details = (
                data.protocol.previous_reaction_details
            )

            protocol.has_diabetes = (
                data.protocol.has_diabetes
            )

            protocol.observations = (
                data.protocol.observations
            )

    appointment = Appointment(
        client_id=client.id,
        service_id=service.id,
        start_at=data.start_at,
        end_at=end_at,
        status="pending",
        payment_method=data.payment_method,
        payment_status="pending",
        price=service.price,
        notes=data.notes,
        return_type=data.return_type,
        return_date=appointment_return_date,
        policies_accepted=True,
        policies_accepted_at=policies_accepted_at,
    )

    db.add(appointment)

    db.commit()
    db.refresh(appointment)

    if protocol is not None:
        db.refresh(protocol)

    return {
        "message": "Agendamento criado com sucesso.",
        "appointment": {
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
            "payment_method": appointment.payment_method,
            "payment_status": appointment.payment_status,

            "policies": {
                "accepted": appointment.policies_accepted,
                "accepted_at": appointment.policies_accepted_at,
            },

            "protocol": {
                "id": protocol.id if protocol else None,
                "saved": protocol is not None,
            },

            "return": {
                "type": appointment.return_type,
                "date": appointment.return_date,
            },
        },
    }