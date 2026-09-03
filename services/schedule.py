from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from models.service import Service
from services.availability import (
    WEEKDAY_START,
    AUTO_BOOKING_END,
    get_working_hours,
    check_availability,
)


def generate_available_times(
    db: Session,
    appointment_date: date,
    service: Service,
):
    """
    Gera os horários disponíveis para um serviço
    em uma determinada data.

    Segunda a sexta:
        Agenda normal: 08:00 às 19:00
        Exceções automáticas: até 20:00

    Sábados e domingos:
        Somente encaixe pelo painel administrativo.
    """

    opening_time, closing_time = get_working_hours(
        appointment_date
    )

    # ------------------------------------------
    # Fim de semana
    # ------------------------------------------

    if opening_time is None:
        return []

    # ------------------------------------------
    # Limite da agenda automática
    # ------------------------------------------

    opening = datetime.combine(
        appointment_date,
        opening_time
    )

    auto_booking_end = datetime.combine(
        appointment_date,
        AUTO_BOOKING_END
    )

    # ------------------------------------------
    # Criar lista de horários
    # ------------------------------------------

    available_times = []

    current_time = opening

    while current_time < auto_booking_end:

        available, _, end_at = check_availability(
            db=db,
            start_at=current_time,
            duration_minutes=service.duration_minutes,
        )

        # --------------------------------------
        # O atendimento pode passar das 19h,
        # mas não pode ultrapassar 20h
        # na agenda automática.
        # --------------------------------------

        if available and end_at <= auto_booking_end:
            available_times.append(
                {
                    "start": current_time.strftime("%H:%M"),
                    "end": end_at.strftime("%H:%M"),
                }
            )

        # --------------------------------------
        # Próximo horário
        #
        # Intervalos de 30 minutos.
        # --------------------------------------

        current_time += timedelta(minutes=30)

    return available_times