from datetime import datetime
from zoneinfo import ZoneInfo


TIMEZONE = ZoneInfo("America/Maceio")


def now_local() -> datetime:
    """
    Retorna a data e hora atual no fuso oficial
    do sistema Jeni Santos Nails.
    """
    return datetime.now(TIMEZONE)