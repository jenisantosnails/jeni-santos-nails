from database.database import SessionLocal
from models.appointment import Appointment
from models.client import Client


TEST_CLIENT_PHONES = {
"71111111113",
}


def cleanup():
    db = SessionLocal()

    try:
        clients = (
            db.query(Client)
            .filter(Client.phone.in_(TEST_CLIENT_PHONES))
            .all()
        )

        if not clients:
            print("Nenhum dado de teste encontrado.")
            return

        removed_appointments = 0
        removed_clients = 0

        for client in clients:
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

        db.commit()

        print()
        print("========================================")
        print(" LIMPEZA DOS DADOS DE TESTE")
        print("========================================")
        print(f"Agendamentos removidos: {removed_appointments}")
        print(f"Clientes removidas: {removed_clients}")
        print("Serviços não foram alterados.")
        print("========================================")
        print("Limpeza concluída com sucesso!")
        print("========================================")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    cleanup()