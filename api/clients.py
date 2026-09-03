from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.database import get_db
from models.client import Client


router = APIRouter(
    prefix="/clients",
    tags=["Clientes"],
)


# ==========================================
# SCHEMAS
# ==========================================

class ClientCreate(BaseModel):
    name: str
    phone: str
    email: str | None = None
    notes: str | None = None


class ClientUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    notes: str | None = None
    active: bool | None = None


# ==========================================
# CADASTRAR CLIENTE
# ==========================================

@router.post("/")
def create_client(
    data: ClientCreate,
    db: Session = Depends(get_db),
):
    existing_client = (
        db.query(Client)
        .filter(Client.phone == data.phone)
        .first()
    )

    if existing_client is not None:
        raise HTTPException(
            status_code=409,
            detail="Este telefone já está cadastrado para outra cliente.",
        )

    client = Client(
        name=data.name,
        phone=data.phone,
        email=data.email,
        notes=data.notes,
        active=True,
    )

    db.add(client)
    db.commit()
    db.refresh(client)

    return {
        "message": "Cliente cadastrada com sucesso.",
        "client": {
            "id": client.id,
            "name": client.name,
            "phone": client.phone,
            "email": client.email,
            "notes": client.notes,
            "active": client.active,
            "created_at": client.created_at,
        },
    }


# ==========================================
# LISTAR CLIENTES
# ==========================================

@router.get("/")
def list_clients(
    db: Session = Depends(get_db),
    search: str | None = Query(
        default=None,
        description="Busca por nome ou telefone",
    ),
    active: bool | None = Query(
        default=None,
        description="Filtrar por status ativo ou inativo",
    ),
):
    query = db.query(Client)

    if active is True:
        query = query.filter(Client.active == True)

    elif active is False:
        query = query.filter(Client.active == False)

    if search:
        search_value = f"%{search}%"

        query = query.filter(
            (Client.name.ilike(search_value))
            | (Client.phone.ilike(search_value))
        )

    clients = (
        query
        .order_by(Client.name)
        .all()
    )

    return [
        {
            "id": client.id,
            "name": client.name,
            "phone": client.phone,
            "email": client.email,
            "notes": client.notes,
            "active": client.active,
            "created_at": client.created_at,
        }
        for client in clients
    ]


# ==========================================
# VISUALIZAR CLIENTE
# ==========================================

@router.get("/{client_id}")
def get_client(
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
            detail="Cliente não encontrado.",
        )

    return {
        "id": client.id,
        "name": client.name,
        "phone": client.phone,
        "email": client.email,
        "notes": client.notes,
        "active": client.active,
        "created_at": client.created_at,
    }


# ==========================================
# EDITAR CLIENTE
# ==========================================

@router.patch("/{client_id}")
def update_client(
    client_id: int,
    data: ClientUpdate,
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
            detail="Cliente não encontrado.",
        )

    if data.phone and data.phone != client.phone:
        existing_client = (
            db.query(Client)
            .filter(
                Client.phone == data.phone,
                Client.id != client_id,
            )
            .first()
        )

        if existing_client is not None:
            raise HTTPException(
                status_code=409,
                detail="Este telefone já está cadastrado para outra cliente.",
            )

    if data.name is not None:
        client.name = data.name

    if data.phone is not None:
        client.phone = data.phone

    if data.email is not None:
        client.email = data.email

    if data.notes is not None:
        client.notes = data.notes

    if data.active is not None:
        client.active = data.active

    db.commit()
    db.refresh(client)

    return {
        "message": "Cliente atualizado com sucesso.",
        "client": {
            "id": client.id,
            "name": client.name,
            "phone": client.phone,
            "email": client.email,
            "notes": client.notes,
            "active": client.active,
        },
    }


# ==========================================
# DESATIVAR CLIENTE
# ==========================================

@router.delete("/{client_id}")
def deactivate_client(
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

    if not client.active:
        raise HTTPException(
            status_code=409,
            detail="Esta cliente já está desativada.",
        )

    client.active = False

    db.commit()
    db.refresh(client)

    return {
        "message": "Cliente desativada com sucesso.",
        "client": {
            "id": client.id,
            "name": client.name,
            "active": client.active,
        },
    }