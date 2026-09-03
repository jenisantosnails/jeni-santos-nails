from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base
from services.time import now_local


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id"),
        nullable=False,
        index=True
    )

    service_id: Mapped[int] = mapped_column(
        ForeignKey("services.id"),
        nullable=False,
        index=True
    )

    start_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True
    )

    end_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
        index=True
    )

    payment_method: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    payment_status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False
    )

    # ==========================================
    # ACEITE DAS POLÍTICAS
    # ==========================================

    policies_accepted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    policies_accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    # ==========================================
    # VALOR DO AGENDAMENTO
    # ==========================================

    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # ==========================================
    # RETORNO DA CLIENTE
    # ==========================================

    return_type: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    return_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    # ==========================================
    # LEMBRETE DE RETORNO
    # ==========================================

    # Fica preenchido quando o lembrete for enviado.
    # Enquanto estiver vazio, o sistema ainda pode
    # considerar o atendimento elegível para lembrete.

    reminder_sent_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    # ==========================================
    # CONTROLE DO REGISTRO
    # ==========================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=now_local,
        nullable=False
    )

    # ==========================================
    # RELACIONAMENTOS
    # ==========================================

    client = relationship(
        "Client",
        backref="appointments"
    )

    service = relationship(
        "Service",
        backref="appointments"
    )