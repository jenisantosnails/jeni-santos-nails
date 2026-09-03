from datetime import datetime, timedelta

from database.database import SessionLocal
from models.appointment import Appointment
from models.client import Client
from models.service import Service
from services.availability import check_availability


def run_test():
    db = SessionLocal()

    client = None
    created_appointments = []

    try:
        print()
        print("========================================")
        print(" TESTE DO LIMITE DE 6 CLIENTES")
        print("========================================")

        service = (
            db.query(Service)
            .filter(Service.name == "Manicure tradicional")
            .first()
        )

        if service is None:
            print("Serviço não encontrado.")
            return

        # Telefone diferente a cada execução
        test_phone = "99999" + datetime.now().strftime("%H%M%S")

        client = Client(
            name="Cliente Teste Limite",
            phone=test_phone,
            email=f"teste{test_phone}@teste.com"
        )

        db.add(client)
        db.commit()
        db.refresh(client)

        base_time = datetime(2026, 8, 19, 8, 0)

        # --------------------------------------
        # Criar 6 agendamentos
        # --------------------------------------

        for number in range(1, 7):

            start_at = base_time + timedelta(
                hours=(number - 1)
            )

            appointment = Appointment(
                client_id=client.id,
                service_id=service.id,
                start_at=start_at,
                end_at=start_at + timedelta(
                    minutes=service.duration_minutes
                ),
                status="pending",
                payment_status="pending",
                price=service.price
            )

            db.add(appointment)
            created_appointments.append(appointment)

        db.commit()

        print()
        print("6 clientes/agendamentos de teste criados.")
        print(f"Serviço: {service.name}")
        print(f"Valor: R$ {service.price:.2f}")

        # --------------------------------------
        # Testar 7º cliente
        # --------------------------------------

        test_start = datetime(2026, 8, 19, 15, 0)

        available, message, end_at = check_availability(
            db=db,
            start_at=test_start,
            duration_minutes=service.duration_minutes
        )

        print()
        print("TESTE DO 7º CLIENTE")
        print(f"Disponível: {available}")
        print(f"Mensagem: {message}")
        print(f"Término: {end_at}")

        print()
        print("========================================")

    except Exception:
        db.rollback()
        raise

    finally:
        # --------------------------------------
        # Limpar agendamentos de teste
        # --------------------------------------

        for appointment in created_appointments:
            if appointment.id is not None:
                db.delete(appointment)

        db.commit()

        # --------------------------------------
        # Limpar cliente de teste
        # --------------------------------------

        if client is not None and client.id is not None:
            db.delete(client)
            db.commit()

        db.close()


if __name__ == "__main__":
    run_test()