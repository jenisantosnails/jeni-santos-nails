from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from models.service import Service


router = APIRouter(
    prefix="/services",
    tags=["Serviços"]
)


@router.get("/")
def list_services(
    db: Session = Depends(get_db)
):
    services = (
        db.query(Service)
        .filter(Service.active == True)
        .order_by(Service.name)
        .all()
    )

    return [
        {
            "id": service.id,
            "name": service.name,
            "price": float(service.price),
            "duration_minutes": service.duration_minutes,
        }
        for service in services
    ]