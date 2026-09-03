from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.database import get_db
from models.client import Client
from models.client_protocol import ClientProtocol


router = APIRouter(
    prefix="/client-protocols",
    tags=["Protocolos de Clientes"],
)


class ClientProtocolCreate(BaseModel):
    has_allergy_or_sensitivity: bool = False
    allergy_or_sensitivity_details: str | None = None

    has_current_issue: bool = False
    current_issue_details: str | None = None

    has_previous_reaction: bool = False
    previous_reaction_details: str | None = None

    has_diabetes: bool = False

    observations: str | None = None


class ClientProtocolUpdate(BaseModel):
    has_allergy_or_sensitivity: bool | None = None
    allergy_or_sensitivity_details: str | None = None

    has_current_issue: bool | None = None
    current_issue_details: str | None = None

    has_previous_reaction: bool | None = None
    previous_reaction_details: str | None = None

    has_diabetes: bool | None = None

    observations: str | None = None


def protocol_to_dict(protocol: ClientProtocol):
    return {
        "id": protocol.id,
        "client_id": protocol.client_id,

        "has_allergy_or_sensitivity": (
            protocol.has_allergy_or_sensitivity
        ),
        "allergy_or_sensitivity_details": (
            protocol.allergy_or_sensitivity_details
        ),

        "has_current_issue": (
            protocol.has_current_issue
        ),
        "current_issue_details": (
            protocol.current_issue_details
        ),

        "has_previous_reaction": (
            protocol.has_previous_reaction
        ),
        "previous_reaction_details": (
            protocol.previous_reaction_details
        ),

        "has_diabetes": protocol.has_diabetes,

        "observations": protocol.observations,

        "updated_at": protocol.updated_at,
    }


@router.get("/{client_id}")
def get_client_protocol(
    client_id: int,
    db: Session = Depends(get_db),
):
    client = (
        db.query(Client)
        .filter(Client.id == client_id)
        .first()
    )

    if client is None:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrada.",
        )

    protocol = (
        db.query(ClientProtocol)
        .filter(ClientProtocol.client_id == client_id)
        .first()
    )

    if protocol is None:
        return {
            "exists": False,
            "client_id": client_id,
            "protocol": None,
        }

    return {
        "exists": True,
        "client_id": client_id,
        "protocol": protocol_to_dict(protocol),
    }


@router.post("/{client_id}")
def create_client_protocol(
    client_id: int,
    data: ClientProtocolCreate,
    db: Session = Depends(get_db),
):
    client = (
        db.query(Client)
        .filter(Client.id == client_id)
        .first()
    )

    if client is None:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrada.",
        )

    existing_protocol = (
        db.query(ClientProtocol)
        .filter(ClientProtocol.client_id == client_id)
        .first()
    )

    if existing_protocol is not None:
        raise HTTPException(
            status_code=409,
            detail="Esta cliente já possui um protocolo cadastrado.",
        )

    protocol = ClientProtocol(
        client_id=client.id,

        has_allergy_or_sensitivity=(
            data.has_allergy_or_sensitivity
        ),
        allergy_or_sensitivity_details=(
            data.allergy_or_sensitivity_details
        ),

        has_current_issue=(
            data.has_current_issue
        ),
        current_issue_details=(
            data.current_issue_details
        ),

        has_previous_reaction=(
            data.has_previous_reaction
        ),
        previous_reaction_details=(
            data.previous_reaction_details
        ),

        has_diabetes=data.has_diabetes,

        observations=data.observations,
    )

    db.add(protocol)
    db.commit()
    db.refresh(protocol)

    return {
        "message": "Protocolo cadastrado com sucesso.",
        "protocol": protocol_to_dict(protocol),
    }


@router.patch("/{client_id}")
def update_client_protocol(
    client_id: int,
    data: ClientProtocolUpdate,
    db: Session = Depends(get_db),
):
    client = (
        db.query(Client)
        .filter(Client.id == client_id)
        .first()
    )

    if client is None:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrada.",
        )

    protocol = (
        db.query(ClientProtocol)
        .filter(ClientProtocol.client_id == client_id)
        .first()
    )

    if protocol is None:
        raise HTTPException(
            status_code=404,
            detail="Protocolo da cliente não encontrado.",
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(protocol, field, value)

    db.commit()
    db.refresh(protocol)

    return {
        "message": "Protocolo atualizado com sucesso.",
        "protocol": protocol_to_dict(protocol),
    }