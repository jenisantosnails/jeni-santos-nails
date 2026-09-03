from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.database import get_db
from models.service import Service


router = APIRouter(
    prefix="/services",
    tags=["Serviços"],
)


# ==========================================
# LISTAR SERVIÇOS
# ==========================================

@router.get("/")
def list_services(
    db: Session = Depends(get_db),
    active: bool | None = Query(
        default=None,
        description="Filtrar por status do serviço",
    ),
):
    query = db.query(Service)

    # --------------------------------------
    # FILTRO DE STATUS
    # --------------------------------------

    if active is not None:
        query = query.filter(
            Service.active == active
        )

    # --------------------------------------
    # BUSCAR SERVIÇOS
    # --------------------------------------

    services = (
        query
        .order_by(Service.name)
        .all()
    )

    # --------------------------------------
    # RESPOSTA
    # --------------------------------------

    return [
        {
            "id": service.id,
            "name": service.name,
            "price": service.price,
            "duration_minutes": service.duration_minutes,
            "active": service.active,
        }
        for service in services
    ]