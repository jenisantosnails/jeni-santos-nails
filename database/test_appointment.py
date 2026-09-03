from datetime import datetime, timedelta
from decimal import Decimal

from database.database import SessionLocal
from models.appointment import Appointment
from models.client import Client
from models.service import Service


def test_appointment():
    db = SessionLocal()

    try:
        # -----------------------------------------
        # 1. Criar ou localizar cliente de teste
        # -----------------------------------------
        client = (
            db.query(Client)
            .filter(Client.phone == "99999999999")
            .first()
        )

        if not client:
            client = Client(
                name="Cliente Teste",
                phone="99999999999",
                email="teste@exemplo.com",
                notes="Cliente criada apenas para teste.",
            )

            db.add(client)
            db.commit()
            db.refresh(client)

        # -----------------------------------------
        # 2. Localizar o serviço Banho em gel
        # -----------------------------------------
        service = (
            db.query(Service)
            .filter(Service.name == "Banho em gel")
            .first()
        )

        if not service:
            print("ERRO: serviço Banho em gel não encontrado.")
            return

        # -----------------------------------------
        # 3. Definir início do agendamento
        # -----------------------------------------
        start_at = datetime(2026, 8, 18, 14, 0)

        # -----------------------------------------
        # 4. Calcular término automaticamente
        # -----------------------------------------
        end_at = start_at + timedelta(
            minutes=service.duration_minutes
        )

        # -----------------------------------------
        # 5. Criar agendamento
        # -----------------------------------------
        appointment = Appointment(
            client_id=client.id,
            service_id=service.id,
            start_at=start_at,
            end_at=end_at,
            status="pending",
            payment_method=None,
            payment_status="pending",
            price=Decimal(str(service.price)),
            notes="Agendamento criado durante o teste.",
        )

        db.add(appointment)
        db.commit()
        db.refresh(appointment)

        print()
        print("========================================")
        print(" AGENDAMENTO DE TESTE")
        print("========================================")
        print(f"Cliente: {client.name}")
        print(f"Serviço: {service.name}")
        print(f"Valor: R$ {appointment.price}")
        print(f"Início: {appointment.start_at}")
        print(f"Término: {appointment.end_at}")
        print(f"Status: {appointment.status}")
        print("========================================")
        print("Agendamento salvo com sucesso!")
        print("========================================")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    test_appointment()