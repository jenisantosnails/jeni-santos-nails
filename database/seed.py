from decimal import Decimal

from database.database import SessionLocal
from models.service import Service


SERVICES = [
    {
        "name": "Manicure tradicional",
        "description": "Manicure tradicional.",
        "price": Decimal("25.00"),
        "duration_minutes": 50,
    },
    {
        "name": "Pedicure tradicional",
        "description": "Pedicure tradicional.",
        "price": Decimal("30.00"),
        "duration_minutes": 90,
    },
    {
        "name": "Esmaltação em gel nos pés",
        "description": "Esmaltação em gel nos pés.",
        "price": Decimal("70.00"),
        "duration_minutes": 90,
    },
    {
        "name": "Esmaltação em gel nas mãos",
        "description": "Esmaltação em gel nas mãos.",
        "price": Decimal("50.00"),
        "duration_minutes": 90,
    },
    {
        "name": "Banho em gel",
        "description": "Banho em gel.",
        "price": Decimal("100.00"),
        "duration_minutes": 160,
    },
    {
        "name": "Molde F1",
        "description": "Alongamento com molde F1.",
        "price": Decimal("120.00"),
        "duration_minutes": 180,
    },
    {
        "name": "Fibra",
        "description": "Alongamento em fibra.",
        "price": Decimal("120.00"),
        "duration_minutes": 180,
    },
    {
        "name": "Soft Gel",
        "description": "Alongamento em Soft Gel.",
        "price": Decimal("100.00"),
        "duration_minutes": 120,
    },
    {
        "name": "Manutenção",
        "description": "Manutenção das unhas.",
        "price": Decimal("90.00"),
        "duration_minutes": 180,
    },
]


def seed_services():
    db = SessionLocal()

    try:
        added = 0
        existing = 0

        for service_data in SERVICES:
            service = (
                db.query(Service)
                .filter(Service.name == service_data["name"])
                .first()
            )

            if service:
                existing += 1
                continue

            service = Service(**service_data)
            db.add(service)
            added += 1

        db.commit()

        print()
        print("========================================")
        print(" Jeni Santos Nails - Serviços")
        print("========================================")
        print(f"Serviços adicionados: {added}")
        print(f"Serviços já existentes: {existing}")
        print("Cadastro concluído com sucesso!")
        print("========================================")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_services()