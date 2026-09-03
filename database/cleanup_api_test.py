from database.database import SessionLocal
from models.appointment import Appointment
from models.client import Client


TEST_PHONE = "99999999991"


def cleanup():
    db = SessionLocal()

    try:
        client = (
            db.query(Client)
            .filter(Client.phone == TEST_PHONE)
            .first()
        )

        if client is None:
            print("Cliente de teste não encontrado.")
            return

        appointments = (
            db.query(Appointment)
            .filter(Appointment.client_id == client.id)
            .all()
        )

        for appointment in appointments:
            db.delete(appointment)

        db.delete(client)
        db.commit()

        print("========================================")
        print(" LIMPEZA DO TESTE DA API")
        print("========================================")
        print()
        print(f"Agendamentos removidos: {len(appointments)}")
        print(f"Cliente removido: {TEST_PHONE}")
        print()
        print("Limpeza concluída com sucesso.")
        print("========================================")

    except Exception as error:
        db.rollback()
        print("Erro durante a limpeza:")
        print(error)

    finally:
        db.close()


if __name__ == "__main__":
    cleanup()