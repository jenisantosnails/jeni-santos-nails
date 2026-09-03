from datetime import date, datetime, time, timedelta

from sqlalchemy.orm import Session

from models.appointment import Appointment


# ==========================================
# CONFIGURAÇÕES DA AGENDA
# ==========================================

WEEKDAY_START = time(9, 0)
WEEKDAY_END = time(19, 0)
AUTO_BOOKING_END = time(20, 0)

LUNCH_START = time(13, 0)
LUNCH_END = time(14, 0)

# Quantidade ideal de clientes por dia.
# Não bloqueia a agenda.
IDEAL_APPOINTMENTS_PER_DAY = 3

# Limite absoluto de clientes por dia.
MAX_APPOINTMENTS_PER_DAY = 6


# ==========================================
# HORÁRIO DE FUNCIONAMENTO
# ==========================================

def get_working_hours(day: date):
    """
    Retorna o horário de funcionamento para uma determinada data.

    Segunda a sexta:
        08:00 às 19:00

    Sábado e domingo:
        Somente por encaixe.
    """

    if day.weekday() < 5:
        return WEEKDAY_START, WEEKDAY_END

    return None, None


# ==========================================
# CONTAGEM DE CLIENTES NO DIA
# ==========================================

def count_appointments_on_day(
    db: Session,
    appointment_date: date
) -> int:
    """
    Conta os agendamentos ativos de um determinado dia.

    Cancelamentos não entram na contagem.
    """

    start_of_day = datetime.combine(
        appointment_date,
        time.min
    )

    end_of_day = datetime.combine(
        appointment_date,
        time.max
    )

    return (
        db.query(Appointment)
        .filter(
            Appointment.start_at >= start_of_day,
            Appointment.start_at <= end_of_day,
            Appointment.status != "cancelled"
        )
        .count()
    )


# ==========================================
# VERIFICAÇÃO DE CONFLITO
# ==========================================

def has_time_conflict(
    db: Session,
    start_at: datetime,
    end_at: datetime,
    exclude_appointment_id: int | None = None,
) -> bool:
    """
    Verifica se o novo horário entra em conflito
    com algum agendamento existente.

    Quando exclude_appointment_id é informado,
    esse agendamento é ignorado na verificação.

    Isso permite editar ou reagendar um agendamento
    sem que ele entre em conflito consigo mesmo.
    """

    query = (
        db.query(Appointment)
        .filter(
            Appointment.status != "cancelled",
            Appointment.start_at < end_at,
            Appointment.end_at > start_at,
        )
    )

    if exclude_appointment_id is not None:
        query = query.filter(
            Appointment.id != exclude_appointment_id
        )

    conflict = query.first()

    return conflict is not None


# ==========================================
# VERIFICAÇÃO COMPLETA
# ==========================================

def check_availability(
    db: Session,
    start_at: datetime,
    duration_minutes: int,
    exclude_appointment_id: int | None = None,
) -> tuple[bool, str, datetime]:
    """
    Verifica se um atendimento pode ser agendado.

    Regras:
        - Segunda a sexta: agenda normal.
        - 08:00 é o início da agenda.
        - 13:00 às 14:00 é o almoço.
        - Atendimento pode ultrapassar 19:00.
        - Agenda automática pode ir até 20:00.
        - 3 clientes é a capacidade ideal.
        - 6 clientes é o limite absoluto.
        - Sábado e domingo são somente encaixe.
        - Um agendamento pode ser ignorado quando
          estiver sendo editado.

    Retorna:
        disponível: bool
        mensagem: str
        horário_final: datetime
    """

    end_at = start_at + timedelta(
        minutes=duration_minutes
    )

    appointment_date = start_at.date()

    # --------------------------------------
    # 1. Verificar horário de funcionamento
    # --------------------------------------

    opening_time, closing_time = get_working_hours(
        appointment_date
    )

    # Sábado e domingo
    if opening_time is None:
        return (
            False,
            "Sábados e domingos são atendidos somente por encaixe.",
            end_at
        )

    opening = datetime.combine(
        appointment_date,
        opening_time
    )

    closing = datetime.combine(
        appointment_date,
        closing_time
    )

    # Atendimento antes da abertura
    if start_at < opening:
        return (
            False,
            "O horário escolhido é antes do início do atendimento.",
            end_at
        )

    # --------------------------------------
    # 2. Verificar intervalo de almoço
    # --------------------------------------

    lunch_start = datetime.combine(
        appointment_date,
        LUNCH_START
    )

    lunch_end = datetime.combine(
        appointment_date,
        LUNCH_END
    )

    # O atendimento não pode atravessar o almoço.
    if start_at < lunch_end and end_at > lunch_start:
        return (
            False,
            "O horário escolhido entra no intervalo de almoço.",
            end_at
        )

    # --------------------------------------
    # 3. Limite absoluto de 6 clientes
    # --------------------------------------

    appointments_today = count_appointments_on_day(
        db,
        appointment_date
    )

    # Quando estamos editando um agendamento,
    # ele próprio já está contabilizado.
    # Por isso, não devemos bloquear a edição
    # apenas porque ele é um dos 6 agendamentos.
    if exclude_appointment_id is not None:
        excluded_appointment = (
            db.query(Appointment)
            .filter(
                Appointment.id == exclude_appointment_id,
                Appointment.status != "cancelled",
            )
            .first()
        )

        if excluded_appointment is not None:
            appointments_today -= 1

    if appointments_today >= MAX_APPOINTMENTS_PER_DAY:
        return (
            False,
            "Não há mais vagas disponíveis para este dia.",
            end_at
        )

    # --------------------------------------
    # 4. Verificar conflito de horário
    # --------------------------------------

    if has_time_conflict(
        db,
        start_at,
        end_at,
        exclude_appointment_id=exclude_appointment_id,
    ):
        return (
            False,
            "O horário escolhido entra em conflito com outro atendimento.",
            end_at
        )

    # --------------------------------------
    # 5. Tudo certo
    # --------------------------------------

    return (
        True,
        "Horário disponível.",
        end_at
    )