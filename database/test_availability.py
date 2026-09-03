from datetime import datetime

from database.database import SessionLocal
from models.appointment import Appointment
from models.client import Client
from models.service import Service
from services.availability import check_availability


def run_tests():
    db = SessionLocal()

    try:
        # ==========================================
        # TESTE 1
        # Manicure às 09:00
        # ==========================================

        service = (
            db.query(Service)
            .filter(Service.name == "Manicure tradicional")
            .first()
        )

        available, message, end_at = check_availability(
            db=db,
            start_at=datetime(2026, 8, 17, 9, 0),
            duration_minutes=service.duration_minutes,
        )

        print()
        print("TESTE 1 - Manicure às 09:00")
        print(f"Disponível: {available}")
        print(f"Mensagem: {message}")
        print(f"Término: {end_at}")

        # ==========================================
        # TESTE 2
        # Banho em gel às 17:00
        # ==========================================

        service = (
            db.query(Service)
            .filter(Service.name == "Banho em gel")
            .first()
        )

        available, message, end_at = check_availability(
            db=db,
            start_at=datetime(2026, 8, 17, 17, 0),
            duration_minutes=service.duration_minutes,
        )

        print()
        print("TESTE 2 - Banho em gel às 17:00")
        print(f"Disponível: {available}")
        print(f"Mensagem: {message}")
        print(f"Término: {end_at}")

        # ==========================================
        # TESTE 3
        # Conflito com agendamento existente
        # ==========================================

        client = Client(
            name="Cliente Teste Disponibilidade",
            phone="98888888888",
            email="teste-disponibilidade@exemplo.com",
        )

        db.add(client)
        db.commit()
        db.refresh(client)

        service = (
            db.query(Service)
            .filter(Service.name == "Banho em gel")
            .first()
        )

        existing_start = datetime(
            2026, 8, 18, 14, 0
        )

        existing_end = datetime(
            2026, 8, 18, 16, 40
        )

        appointment = Appointment(
            client_id=client.id,
            service_id=service.id,
            start_at=existing_start,
            end_at=existing_end,
            status="confirmed",
            payment_method=None,
            payment_status="pending",
            price=service.price,
        )

        db.add(appointment)
        db.commit()

        available, message, end_at = check_availability(
            db=db,
            start_at=datetime(2026, 8, 18, 15, 0),
            duration_minutes=90,
        )

        print()
        print("TESTE 3 - Conflito às 15:00")
        print(f"Disponível: {available}")
        print(f"Mensagem: {message}")
        print(f"Término: {end_at}")

        # ==========================================
        # TESTE 4
        # Sábado
        # ==========================================

        service = (
            db.query(Service)
            .filter(Service.name == "Manicure tradicional")
            .first()
        )

        available, message, end_at = check_availability(
            db=db,
            start_at=datetime(2026, 8, 22, 10, 0),
            duration_minutes=service.duration_minutes,
        )

        print()
        print("TESTE 4 - Sábado às 10:00")
        print(f"Disponível: {available}")
        print(f"Mensagem: {message}")
        print(f"Término: {end_at}")

    finally:
        db.rollback()

        # Remove qualquer dado criado pelo teste
        client = (
            db.query(Client)
            .filter(
                Client.phone == "98888888888"
            )
            .first()
        )

        if client:
            appointments = (
                db.query(Appointment)
                .filter(
                    Appointment.client_id == client.id
                )
                .all()
            )

            for appointment in appointments:
                db.delete(appointment)

            db.delete(client)

        db.commit()
        db.close()


if __name__ == "__main__":
    run_tests()