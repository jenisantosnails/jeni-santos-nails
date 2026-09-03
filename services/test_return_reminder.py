from database.database import SessionLocal
from services.return_reminder import prepare_return_reminders


def test_return_reminders():
    db = SessionLocal()

    try:
        reminders = prepare_return_reminders(db)

        print()
        print("=" * 50)
        print(" TESTE DO MOTOR DE LEMBRETES")
        print("=" * 50)
        print(f"Retornos encontrados: {len(reminders)}")
        print()

        for reminder in reminders:
            print(f"ID agendamento: {reminder['appointment_id']}")
            print(f"Cliente: {reminder['client_name']}")
            print(f"Telefone: {reminder['phone']}")
            print(f"Serviço: {reminder['service']}")
            print("Retorno:", reminder["return_date"])
            print()
            print("MENSAGEM:")
            print("-" * 50)
            print(reminder["message"])
            print("-" * 50)
            print()

        print("=" * 50)
        print(" TESTE CONCLUÍDO")
        print("=" * 50)

    finally:
        db.close()


if __name__ == "__main__":
    test_return_reminders()