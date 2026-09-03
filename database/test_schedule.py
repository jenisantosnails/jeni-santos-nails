from datetime import date

from database.database import SessionLocal
from models.service import Service
from services.schedule import generate_available_times


def run_test():
    db = SessionLocal()

    try:
        service = (
            db.query(Service)
            .filter(Service.name == "Manicure tradicional")
            .first()
        )

        if not service:
            print("Serviço não encontrado.")
            return

        test_date = date(2026, 8, 17)

        times = generate_available_times(
            db=db,
            appointment_date=test_date,
            service=service,
        )

        print()
        print("========================================")
        print(" TESTE DE HORÁRIOS DISPONÍVEIS")
        print("========================================")
        print(f"Data: {test_date}")
        print(f"Serviço: {service.name}")
        print(
            f"Duração: {service.duration_minutes} minutos"
        )
        print()
        print("Horários encontrados:")
        print()

        for item in times:
            print(
                f"{item['start']} → {item['end']}"
            )

        print()
        print(
            f"Total de horários: {len(times)}"
        )
        print("========================================")

    finally:
        db.close()


if __name__ == "__main__":
    run_test()