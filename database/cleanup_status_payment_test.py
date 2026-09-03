from database.database import SessionLocal
from models.client import Client
from models.appointment import Appointment


TEST_PHONES = [
    "99999999993",
    "99999999994",
]


def cleanup():
    db = SessionLocal()

    try:
        print("=" * 40)
        print(" LIMPEZA DOS TESTES DE STATUS/PAGAMENTO")
        print("=" * 40)

        removed_appointments = 0
        removed_clients = 0

        for phone in TEST_PHONES:
            client = (
                db.query(Client)
                .filter(Client.phone == phone)
                .first()
            )

            if client is None:
                print(f"Cliente de teste não encontrado: {phone}")
                continue

            appointments = (
                db.query(Appointment)
                .filter(Appointment.client_id == client.id)
                .all()
            )

            for appointment in appointments:
                db.delete(appointment)
                removed_appointments += 1

            db.delete(client)
            removed_clients += 1

            print(f"Cliente removido: {phone}")

        db.commit()

        print()
        print(f"Agendamentos removidos: {removed_appointments}")
        print(f"Clientes removidos: {removed_clients}")
        print()
        print("Limpeza concluída com sucesso.")
        print("=" * 40)

    finally:
        db.close()


if __name__ == "__main__":
    cleanup()