from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.database import get_db
from models.appointment import Appointment
from models.client import Client
from models.service import Service
from services.availability import check_availability
from services.time import now_local

router = APIRouter(
    prefix="/appointments",
    tags=["Agendamentos"],
)


# ==========================================
# CONFIGURAÃ‡ÃƒO DOS RETORNOS
# ==========================================

RETURN_DAYS = {
    "15_days": 15,
    "21_days": 21,
    "25_days": 25,
    "30_days": 30,
}


# ==========================================
# DADOS PARA EDITAR AGENDAMENTO
# ==========================================

class AppointmentUpdate(BaseModel):
    client_name: str | None = None
    client_phone: str | None = None
    client_email: str | None = None
    service_id: int | None = None
    start_at: datetime | None = None
    payment_method: str | None = None
    payment_status: str | None = None
    notes: str | None = None

    return_type: str | None = None
    return_date: datetime | None = None


# ==========================================
# CONFIRMAR AGENDAMENTO
# ==========================================

@router.patch("/{appointment_id}/confirm")
def confirm_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
):
    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id)
        .first()
    )

    if appointment is None:
        raise HTTPException(
            status_code=404,
            detail="Agendamento nÃ£o encontrado.",
        )

    if appointment.status == "cancelled":
        raise HTTPException(
            status_code=409,
            detail="NÃ£o Ã© possÃ­vel confirmar um agendamento cancelado.",
        )

    if appointment.status == "completed":
        raise HTTPException(
            status_code=409,
            detail="Este agendamento jÃ¡ foi concluÃ­do.",
        )

    appointment.status = "confirmed"

    db.commit()
    db.refresh(appointment)

    return {
        "message": "Agendamento confirmado com sucesso.",
        "appointment": {
            "id": appointment.id,
            "status": appointment.status,
        },
    }


# ==========================================
# CONCLUIR AGENDAMENTO
# ==========================================

@router.patch("/{appointment_id}/complete")
def complete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
):
    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id)
        .first()
    )

    if appointment is None:
        raise HTTPException(
            status_code=404,
            detail="Agendamento nÃ£o encontrado.",
        )

    if appointment.status == "cancelled":
        raise HTTPException(
            status_code=409,
            detail="NÃ£o Ã© possÃ­vel concluir um agendamento cancelado.",
        )

    if appointment.status == "completed":
        raise HTTPException(
            status_code=409,
            detail="Este agendamento jÃ¡ estÃ¡ concluÃ­do.",
        )

    # --------------------------------------
    # 1. MARCAR COMO CONCLUÃDO
    # --------------------------------------

    completed_at = now_local()

    appointment.status = "completed"
    appointment.completed_at = completed_at

    # --------------------------------------
    # 2. CALCULAR RETORNO
    # --------------------------------------

    if appointment.return_type in RETURN_DAYS:
        days = RETURN_DAYS[appointment.return_type]

        appointment.return_date = completed_at + timedelta(
            days=days
        )

    elif appointment.return_type == "none":
        appointment.return_date = None

    elif appointment.return_type == "custom":
        # MantÃ©m a data personalizada jÃ¡ cadastrada.
        if appointment.return_date is None:
            raise HTTPException(
                status_code=422,
                detail=(
                    "O retorno estÃ¡ configurado como personalizado, "
                    "mas nenhuma data de retorno foi informada."
                ),
            )

    else:
        raise HTTPException(
            status_code=422,
            detail="Tipo de retorno invÃ¡lido no agendamento.",
        )

    # --------------------------------------
    # 3. SALVAR
    # --------------------------------------

    db.commit()
    db.refresh(appointment)

    # --------------------------------------
    # 4. RESPOSTA
    # --------------------------------------

    return {
        "message": "Agendamento concluÃ­do com sucesso.",
        "appointment": {
            "id": appointment.id,
            "status": appointment.status,
            "completed_at": appointment.completed_at,
            "return": {
                "type": appointment.return_type,
                "date": appointment.return_date,
            },
        },
    }


# ==========================================
# CANCELAR AGENDAMENTO
# ==========================================

@router.patch("/{appointment_id}/cancel")
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
):
    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id)
        .first()
    )

    if appointment is None:
        raise HTTPException(
            status_code=404,
            detail="Agendamento nÃ£o encontrado.",
        )

    if appointment.status == "cancelled":
        raise HTTPException(
            status_code=409,
            detail="Este agendamento jÃ¡ estÃ¡ cancelado.",
        )

    appointment.status = "cancelled"

    db.commit()
    db.refresh(appointment)

    return {
        "message": "Agendamento cancelado com sucesso.",
        "appointment": {
            "id": appointment.id,
            "status": appointment.status,
        },
    }


# ==========================================
# EDITAR / REAGENDAR AGENDAMENTO
# ==========================================

@router.patch("/{appointment_id}")
def update_appointment(
    appointment_id: int,
    data: AppointmentUpdate,
    db: Session = Depends(get_db),
):
    # --------------------------------------
    # 1. BUSCAR AGENDAMENTO
    # --------------------------------------

    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id)
        .first()
    )

    if appointment is None:
        raise HTTPException(
            status_code=404,
            detail="Agendamento nÃ£o encontrado.",
        )

    # --------------------------------------
    # 2. VERIFICAR STATUS
    # --------------------------------------

    if appointment.status == "cancelled":
        raise HTTPException(
            status_code=409,
            detail="NÃ£o Ã© possÃ­vel editar um agendamento cancelado.",
        )

    if appointment.status == "completed":
        raise HTTPException(
            status_code=409,
            detail="NÃ£o Ã© possÃ­vel editar um agendamento jÃ¡ concluÃ­do.",
        )

    # --------------------------------------
    # 3. DEFINIR SERVIÃ‡O
    # --------------------------------------

    service_id = (
        data.service_id
        if data.service_id is not None
        else appointment.service_id
    )

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
            detail="ServiÃ§o nÃ£o encontrado.",
        )

    # --------------------------------------
    # 4. DEFINIR NOVO HORÃRIO
    # --------------------------------------

    start_at = (
        data.start_at
        if data.start_at is not None
        else appointment.start_at
    )

    # --------------------------------------
    # 5. VERIFICAR DISPONIBILIDADE
    # --------------------------------------

    available, message, end_at = check_availability(
        db=db,
        start_at=start_at,
        duration_minutes=service.duration_minutes,
        exclude_appointment_id=appointment.id,
    )

    if not available:
        raise HTTPException(
            status_code=409,
            detail=message,
        )

    # --------------------------------------
    # 6. ATUALIZAR CLIENTE
    # --------------------------------------

    if data.client_name is not None:
        appointment.client.name = data.client_name

    if data.client_phone is not None:
        existing_client = (
            db.query(Client)
            .filter(
                Client.phone == data.client_phone,
                Client.id != appointment.client_id,
            )
            .first()
        )

        if existing_client is not None:
            raise HTTPException(
                status_code=409,
                detail="Este telefone jÃ¡ estÃ¡ cadastrado para outra cliente.",
            )

        appointment.client.phone = data.client_phone

    if data.client_email is not None:
        appointment.client.email = data.client_email

    # --------------------------------------
    # 7. ATUALIZAR AGENDAMENTO
    # --------------------------------------

    appointment.service_id = service.id
    appointment.start_at = start_at
    appointment.end_at = end_at
    appointment.price = service.price

    if data.payment_method is not None:
        appointment.payment_method = data.payment_method

    if data.payment_status is not None:
        appointment.payment_status = data.payment_status

    if data.notes is not None:
        appointment.notes = data.notes

    # --------------------------------------
    # 8. ATUALIZAR RETORNO
    # --------------------------------------

    if data.return_type is not None:
        valid_return_types = {
            "none",
            "15_days",
            "21_days",
            "25_days",
            "30_days",
            "custom",
        }

        if data.return_type not in valid_return_types:
            raise HTTPException(
                status_code=422,
                detail=(
                    "Tipo de retorno invÃ¡lido. "
                    "Use: none, 15_days, 21_days, "
                    "25_days, 30_days ou custom."
                ),
            )

        appointment.return_type = data.return_type

        if data.return_type == "none":
            appointment.return_date = None

        elif data.return_type == "custom":
            if data.return_date is None:
                raise HTTPException(
                    status_code=422,
                    detail=(
                        "Para um retorno personalizado, "
                        "Ã© necessÃ¡rio informar a data do retorno."
                    ),
                )

            if data.return_date.date() <= start_at.date():
                raise HTTPException(
                    status_code=422,
                    detail=(
                        "A data do retorno personalizado "
                        "deve ser posterior Ã  data do atendimento."
                    ),
                )

            appointment.return_date = data.return_date

        else:
            # Para retornos automÃ¡ticos, a data serÃ¡ calculada
            # quando o atendimento for concluÃ­do.
            appointment.return_date = None

    elif data.return_date is not None:
        raise HTTPException(
            status_code=422,
            detail=(
                "A data do retorno sÃ³ deve ser informada "
                "quando o tipo de retorno for 'custom'."
            ),
        )

    # --------------------------------------
    # 9. SALVAR
    # --------------------------------------

    db.commit()
    db.refresh(appointment)

    # --------------------------------------
    # 10. RESPOSTA
    # --------------------------------------

    return {
        "message": "Agendamento atualizado com sucesso.",
        "appointment": {
            "id": appointment.id,

            "client": {
                "id": appointment.client.id,
                "name": appointment.client.name,
                "phone": appointment.client.phone,
                "email": appointment.client.email,
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

            "notes": appointment.notes,

            "return": {
                "type": appointment.return_type,
                "date": appointment.return_date,
            },
        },
    }


# ==========================================
# REGISTRAR PAGAMENTO
# ==========================================

@router.patch("/{appointment_id}/payment")
def register_payment(
    appointment_id: int,
    payment_method: str,
    db: Session = Depends(get_db),
):
    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id)
        .first()
    )

    if appointment is None:
        raise HTTPException(
            status_code=404,
            detail="Agendamento nÃ£o encontrado.",
        )

    if appointment.status == "cancelled":
        raise HTTPException(
            status_code=409,
            detail="NÃ£o Ã© possÃ­vel registrar pagamento de um agendamento cancelado.",
        )

    appointment.payment_method = payment_method
    appointment.payment_status = "paid"

    db.commit()
    db.refresh(appointment)

    return {
        "message": "Pagamento registrado com sucesso.",
        "appointment": {
            "id": appointment.id,
            "payment_method": appointment.payment_method,
            "payment_status": appointment.payment_status,
            "price": appointment.price,
        },
    }
