from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base
from services.time import now_local


class ClientProtocol(Base):
    __tablename__ = "client_protocols"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id"),
        nullable=False,
        unique=True,
        index=True
    )

    has_allergy_or_sensitivity: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    allergy_or_sensitivity_details: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    has_current_issue: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    current_issue_details: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    has_previous_reaction: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    previous_reaction_details: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    has_diabetes: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    observations: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=now_local,
        onupdate=now_local,
        nullable=False
    )

    client = relationship(
        "Client",
        backref="protocol",
        uselist=False
    )