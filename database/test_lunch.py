from datetime import datetime

from database.database import SessionLocal
from services.availability import check_availability


def run_test():
    db = SessionLocal()

    try:
        print()
        print("========================================")
        print(" TESTE DO INTERVALO DE ALMOÇO")
        print("========================================")

        tests = [
            (
                "12:00",
                datetime(2026, 8, 17, 12, 0),
                50
            ),
            (
                "12:30",
                datetime(2026, 8, 17, 12, 30),
                50
            ),
            (
                "13:00",
                datetime(2026, 8, 17, 13, 0),
                50
            ),
            (
                "13:30",
                datetime(2026, 8, 17, 13, 30),
                50
            ),
            (
                "14:00",
                datetime(2026, 8, 17, 14, 0),
                50
            ),
        ]

        for name, start_at, duration in tests:

            available, message, end_at = check_availability(
                db=db,
                start_at=start_at,
                duration_minutes=duration
            )

            print()
            print(f"Teste: {name}")
            print(f"Disponível: {available}")
            print(f"Mensagem: {message}")
            print(f"Término: {end_at}")

        print()
        print("========================================")

    finally:
        db.close()


if __name__ == "__main__":
    run_test()