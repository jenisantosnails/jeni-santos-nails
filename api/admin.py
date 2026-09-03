import hmac
import os
from datetime import datetime, timedelta
from pathlib import Path
from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database.database import SessionLocal
from models.appointment import Appointment
from models.client import Client
from models.service import Service

from api.appointments_manage import (
    confirm_appointment,
    complete_appointment,
    cancel_appointment,
    register_payment,
)


router = APIRouter(
    prefix="/admin",
    tags=["Painel Administrativo"],
)


BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


def get_db() -> Session:
    return SessionLocal()


def is_authenticated(request: Request) -> bool:
    return request.session.get(
        "admin_authenticated"
    ) is True


# ==========================================
# LOGIN
# ==========================================

@router.get("/login")
def admin_login_page(request: Request):
    if is_authenticated(request):
        return RedirectResponse(
            url="/admin",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="admin_login.html",
        context={
            "request": request,
            "error": None,
        },
    )


@router.post("/login")
def admin_login(
    request: Request,
    password: str = Form(...),
):
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_password:
        return templates.TemplateResponse(
            request=request,
            name="admin_login.html",
            context={
                "request": request,
                "error": (
                    "A senha administrativa "
                    "ainda não foi configurada."
                ),
            },
            status_code=500,
        )

    if not hmac.compare_digest(
        password,
        admin_password,
    ):
        return templates.TemplateResponse(
            request=request,
            name="admin_login.html",
            context={
                "request": request,
                "error": "Senha incorreta.",
            },
            status_code=401,
        )

    request.session[
        "admin_authenticated"
    ] = True

    return RedirectResponse(
        url="/admin",
        status_code=303,
    )


# ==========================================
# LOGOUT
# ==========================================

@router.get("/logout")
def admin_logout(request: Request):
    request.session.clear()

    return RedirectResponse(
        url="/admin/login",
        status_code=303,
    )


# ==========================================
# LISTAGEM DE AGENDAMENTOS
# ==========================================

@router.get("/appointments")
def admin_appointments(
    request: Request,
    appointment_date: str | None = None,
):
    if not is_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=303,
        )

    db = get_db()

    try:
        results = (
            db.query(
                Appointment,
                Client,
                Service,
            )
            .join(
                Client,
                Appointment.client_id == Client.id,
            )
            .join(
                Service,
                Appointment.service_id == Service.id,
            )
            .filter(
                Appointment.status != "cancelled"
            )
        )

        if appointment_date:
            results = results.filter(
                Appointment.start_at >= f"{appointment_date} 00:00:00",
                Appointment.start_at <= f"{appointment_date} 23:59:59",
            )

        results = (
            results
            .order_by(Appointment.start_at)
            .all()
        )

        appointments = [
            {
                "id": appointment.id,
                "client": {
                    "name": client.name,
                },
                "service": {
                    "name": service.name,
                },
                "start_at": appointment.start_at,
                "end_at": appointment.end_at,
                "status": appointment.status,
                "payment_method": appointment.payment_method,
                "payment_status": appointment.payment_status,
                "price": appointment.price,
                "notes": appointment.notes,
                "return_type": appointment.return_type,
                "return_date": appointment.return_date,
            }
            for appointment, client, service in results
        ]

        return templates.TemplateResponse(
            request=request,
            name="admin_appointments.html",
            context={
                "request": request,
                "appointments": appointments,
                "appointment_date": appointment_date,
            },
        )

    finally:
        db.close()


# ==========================================
# AÇÕES DOS AGENDAMENTOS
# ==========================================

@router.post("/appointments/{appointment_id}/confirm")
def admin_confirm_appointment(
    request: Request,
    appointment_id: int,
):
    if not is_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=303,
        )

    db = get_db()

    try:
        confirm_appointment(
            appointment_id=appointment_id,
            db=db,
        )

        return RedirectResponse(
            url="/admin/appointments",
            status_code=303,
        )

    finally:
        db.close()


@router.post("/appointments/{appointment_id}/complete")
def admin_complete_appointment(
    request: Request,
    appointment_id: int,
):
    if not is_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=303,
        )

    db = get_db()

    try:
        complete_appointment(
            appointment_id=appointment_id,
            db=db,
        )

        return RedirectResponse(
            url="/admin/appointments",
            status_code=303,
        )

    finally:
        db.close()


@router.post("/appointments/{appointment_id}/cancel")
def admin_cancel_appointment(
    request: Request,
    appointment_id: int,
):
    if not is_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=303,
        )

    db = get_db()

    try:
        cancel_appointment(
            appointment_id=appointment_id,
            db=db,
        )

        return RedirectResponse(
            url="/admin/appointments",
            status_code=303,
        )

    finally:
        db.close()


@router.post("/appointments/{appointment_id}/payment")
def admin_register_payment(
    request: Request,
    appointment_id: int,
    payment_method: str = Form(...),
):
    if not is_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=303,
        )

    db = get_db()

    try:
        register_payment(
            appointment_id=appointment_id,
            payment_method=payment_method,
            db=db,
        )

        return RedirectResponse(
            url="/admin/appointments",
            status_code=303,
        )

    finally:
        db.close()


# ==========================================
# EDITAR CLIENTE
# ==========================================

@router.get("/clients/{client_id}/edit")
def admin_edit_client_page(
    request: Request,
    client_id: int,
):
    if not is_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=303,
        )

    db = get_db()

    try:
        client = (
            db.query(Client)
            .filter(Client.id == client_id)
            .first()
        )

        if not client:
            return RedirectResponse(
                url="/admin/clients",
                status_code=303,
            )

        return templates.TemplateResponse(
            request=request,
            name="admin_client_edit.html",
            context={
                "request": request,
                "client": client,
                "error": None,
            },
        )

    finally:
        db.close()


@router.post("/clients/{client_id}/edit")
def admin_edit_client(
    request: Request,
    client_id: int,
    name: str = Form(...),
    phone: str = Form(...),
    email: str | None = Form(None),
    notes: str | None = Form(None),
):
    if not is_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=303,
        )

    db = get_db()

    try:
        client = (
            db.query(Client)
            .filter(Client.id == client_id)
            .first()
        )

        if not client:
            return RedirectResponse(
                url="/admin/clients",
                status_code=303,
            )

        normalized_name = name.strip()
        normalized_phone = phone.strip()
        normalized_email = email.strip() if email else None
        normalized_notes = notes.strip() if notes else None

        if not normalized_name:
            return templates.TemplateResponse(
                request=request,
                name="admin_client_edit.html",
                context={
                    "request": request,
                    "client": client,
                    "error": "O nome da cliente é obrigatório.",
                },
                status_code=400,
            )

        if not normalized_phone:
            return templates.TemplateResponse(
                request=request,
                name="admin_client_edit.html",
                context={
                    "request": request,
                    "client": client,
                    "error": "O telefone da cliente é obrigatório.",
                },
                status_code=400,
            )

        duplicate = (
            db.query(Client)
            .filter(
                Client.phone == normalized_phone,
                Client.id != client_id,
            )
            .first()
        )

        if duplicate:
            return templates.TemplateResponse(
                request=request,
                name="admin_client_edit.html",
                context={
                    "request": request,
                    "client": client,
                    "error": (
                        "Este telefone já está cadastrado "
                        "para outra cliente."
                    ),
                },
                status_code=409,
            )

        client.name = normalized_name
        client.phone = normalized_phone
        client.email = normalized_email
        client.notes = normalized_notes

        db.commit()

        return RedirectResponse(
            url="/admin/clients",
            status_code=303,
        )

    finally:
        db.close()


# ==========================================
# DESATIVAR CLIENTE
# ==========================================

@router.post("/clients/{client_id}/deactivate")
def admin_deactivate_client(
    request: Request,
    client_id: int,
):
    if not is_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=303,
        )

    db = get_db()

    try:
        client = (
            db.query(Client)
            .filter(Client.id == client_id)
            .first()
        )

        if not client:
            return RedirectResponse(
                url="/admin/clients",
                status_code=303,
            )

        client.active = False

        db.commit()

        return RedirectResponse(
            url="/admin/clients",
            status_code=303,
        )

    finally:
        db.close()


# ==========================================
# REATIVAR CLIENTE
# ==========================================

@router.post("/clients/{client_id}/activate")
def admin_activate_client(
    request: Request,
    client_id: int,
):
    if not is_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=303,
        )

    db = get_db()

    try:
        client = (
            db.query(Client)
            .filter(Client.id == client_id)
            .first()
        )

        if not client:
            return RedirectResponse(
                url="/admin/clients",
                status_code=303,
            )

        client.active = True

        db.commit()

        return RedirectResponse(
            url="/admin/clients",
            status_code=303,
        )

    finally:
        db.close()



# ==========================================
# CLIENTES
# ==========================================

@router.get("/clients")
def admin_clients(
    request: Request,
    search: str | None = None,
    active: str | None = None,
):
    if not is_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=303,
        )

    db = get_db()

    try:
        query = db.query(Client)

        if search:
            search_value = f"%{search}%"

            query = query.filter(
                (Client.name.ilike(search_value))
                | (Client.phone.ilike(search_value))
            )

        if active == "active":
            query = query.filter(
                Client.active == True
            )

        elif active == "inactive":
            query = query.filter(
                Client.active == False
            )

        clients = (
            query
            .order_by(Client.name)
            .all()
        )

        return templates.TemplateResponse(
            request=request,
            name="admin_clients.html",
            context={
                "request": request,
                "clients": clients,
                "search": search,
                "active": active,
            },
        )

    finally:
        db.close()


# ==========================================
# SERVIÇOS
# ==========================================

@router.get("/services")
def admin_services(
    request: Request,
    active: str | None = None,
):
    if not is_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=303,
        )

    db = get_db()

    try:
        query = db.query(Service)

        if active == "active":
            query = query.filter(
                Service.active == True
            )

        elif active == "inactive":
            query = query.filter(
                Service.active == False
            )

        services = (
            query
            .order_by(Service.name)
            .all()
        )

        return templates.TemplateResponse(
            request=request,
            name="admin_services.html",
            context={
                "request": request,
                "services": services,
                "active": active,
            },
        )

    finally:
        db.close()


# ==========================================
# EDITAR SERVIÇO
# ==========================================

@router.get("/services/{service_id}/edit")

# ==========================================
# DESATIVAR SERVI?O
# ==========================================

@router.post("/services/{service_id}/deactivate")
def admin_deactivate_service(
    request: Request,
    service_id: int,
):
    if not is_authenticated(request):
        return RedirectResponse(
            url="/admin/services",
            status_code=303,
        )

    db = get_db()

    try:
        service = (
            db.query(Service)
            .filter(Service.id == service_id)
            .first()
        )

        if not service:
            return RedirectResponse(
                url="/admin/services",
                status_code=303,
            )

        service.active = False
        db.commit()

        return RedirectResponse(
            url="/admin/services",
            status_code=303,
        )

    finally:
        db.close()


# ==========================================
# ATIVAR SERVI?O
# ==========================================

@router.post("/services/{service_id}/activate")
def admin_activate_service(
    request: Request,
    service_id: int,
):
    if not is_authenticated(request):
        return RedirectResponse(
            url="/admin/services",
            status_code=303,
        )

    db = get_db()

    try:
        service = (
            db.query(Service)
            .filter(Service.id == service_id)
            .first()
        )

        if not service:
            return RedirectResponse(
                url="/admin/services",
                status_code=303,
            )

        service.active = True
        db.commit()

        return RedirectResponse(
            url="/admin/services",
            status_code=303,
        )

    finally:
        db.close()



def admin_edit_service_page(
    request: Request,
    service_id: int,
):
    if not is_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=303,
        )

    db = get_db()

    try:
        service = (
            db.query(Service)
            .filter(Service.id == service_id)
            .first()
        )

        if not service:
            return RedirectResponse(
                url="/admin/services",
                status_code=303,
            )

        return templates.TemplateResponse(
            request=request,
            name="admin_service_edit.html",
            context={
                "request": request,
                "service": service,
                "error": None,
            },
        )

    finally:
        db.close()


@router.post("/services/{service_id}/edit")
def admin_edit_service(
    request: Request,
    service_id: int,
    name: str = Form(...),
    description: str | None = Form(None),
    price: str = Form(...),
    duration_minutes: str = Form(...),
    active: str | None = Form(None),
):
    if not is_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=303,
        )

    db = get_db()

    try:
        service = (
            db.query(Service)
            .filter(Service.id == service_id)
            .first()
        )

        if not service:
            return RedirectResponse(
                url="/admin/services",
                status_code=303,
            )

        normalized_name = name.strip()
        normalized_description = (
            description.strip()
            if description
            else None
        )

        if not normalized_name:
            return templates.TemplateResponse(
                request=request,
                name="admin_service_edit.html",
                context={
                    "request": request,
                    "service": service,
                    "error": "O nome do serviço é obrigatório.",
                },
                status_code=400,
            )

        try:
            normalized_price = Decimal(
                price.strip().replace(",", ".")
            )
        except (InvalidOperation, AttributeError):
            return templates.TemplateResponse(
                request=request,
                name="admin_service_edit.html",
                context={
                    "request": request,
                    "service": service,
                    "error": "Informe um preço válido.",
                },
                status_code=400,
            )

        if normalized_price < 0:
            return templates.TemplateResponse(
                request=request,
                name="admin_service_edit.html",
                context={
                    "request": request,
                    "service": service,
                    "error": "O preço não pode ser negativo.",
                },
                status_code=400,
            )

        try:
            normalized_duration = int(
                duration_minutes.strip()
            )
        except (ValueError, AttributeError):
            return templates.TemplateResponse(
                request=request,
                name="admin_service_edit.html",
                context={
                    "request": request,
                    "service": service,
                    "error": "Informe uma duração válida.",
                },
                status_code=400,
            )

        if normalized_duration <= 0:
            return templates.TemplateResponse(
                request=request,
                name="admin_service_edit.html",
                context={
                    "request": request,
                    "service": service,
                    "error": (
                        "A duração deve ser maior que zero."
                    ),
                },
                status_code=400,
            )

        service.name = normalized_name
        service.description = normalized_description
        service.price = normalized_price
        service.duration_minutes = normalized_duration
        service.active = active == "on"

        db.commit()

        return RedirectResponse(
            url="/admin/services",
            status_code=303,
        )

    finally:
        db.close()



# ==========================================
# FINANCEIRO
# ==========================================

@router.get("/finance")
def admin_finance(
    request: Request,
    period: str = "month",
    start_date: str | None = None,
    end_date: str | None = None,
):
    if not is_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=303,
        )

    db = get_db()

    try:
        now = datetime.now()

        # --------------------------------------
        # DEFINIR PERÍODO
        # --------------------------------------

        if period == "today":
            period_start = now.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
            period_end = period_start + timedelta(days=1)

        elif period == "week":
            period_start = (
                now.replace(
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0,
                )
                - timedelta(days=now.weekday())
            )
            period_end = period_start + timedelta(days=7)

        elif period == "custom":
            try:
                period_start = datetime.strptime(
                    start_date,
                    "%Y-%m-%d",
                )

                period_end = (
                    datetime.strptime(
                        end_date,
                        "%Y-%m-%d",
                    )
                    + timedelta(days=1)
                )

            except (TypeError, ValueError):
                period_start = now.replace(
                    day=1,
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0,
                )
                period_end = now + timedelta(days=1)

        else:
            period_start = now.replace(
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )

            if period_start.month == 12:
                period_end = period_start.replace(
                    year=period_start.year + 1,
                    month=1,
                )
            else:
                period_end = period_start.replace(
                    month=period_start.month + 1,
                )

            period = "month"

        # --------------------------------------
        # BUSCAR AGENDAMENTOS
        # --------------------------------------

        appointments = (
            db.query(Appointment)
            .filter(
                Appointment.start_at >= period_start,
                Appointment.start_at < period_end,
                Appointment.status != "cancelled",
            )
            .order_by(
                Appointment.start_at.desc()
            )
            .all()
        )

        # --------------------------------------
        # INICIALIZAR TOTAIS
        # --------------------------------------

        total_received = Decimal("0.00")
        total_pending = Decimal("0.00")
        total_billing = Decimal("0.00")
        paid_count = 0

        payment_totals = {
            "pix": Decimal("0.00"),
            "credit_card": Decimal("0.00"),
            "debit_card": Decimal("0.00"),
            "cash": Decimal("0.00"),
        }

        payment_counts = {
            "pix": 0,
            "credit_card": 0,
            "debit_card": 0,
            "cash": 0,
        }

        movements = []

        # --------------------------------------
        # CALCULAR FINANCEIRO
        # --------------------------------------

        for appointment in appointments:

            price = appointment.price or Decimal("0.00")

            total_billing += price

            if appointment.payment_status == "paid":

                total_received += price
                paid_count += 1

                method = appointment.payment_method

                if method in payment_totals:
                    payment_totals[method] += price
                    payment_counts[method] += 1

            else:
                total_pending += price

            movements.append(
                {
                    "appointment": appointment,
                    "client": appointment.client,
                    "service": appointment.service,
                }
            )

        return templates.TemplateResponse(
            request=request,
            name="admin_finance.html",
            context={
                "request": request,
                "period": period,
                "start_date": start_date or "",
                "end_date": end_date or "",
                "total_received": total_received,
                "total_pending": total_pending,
                "total_billing": total_billing,
                "paid_count": paid_count,
                "payment_totals": payment_totals,
                "payment_counts": payment_counts,
                "movements": movements,
            },
        )

    finally:
        db.close()


# ==========================================
# DASHBOARD
# ==========================================

@router.get("")
def admin_dashboard(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=303,
        )

    db = get_db()

    try:
        clients_count = (
            db.query(Client).count()
        )

        services_count = (
            db.query(Service)
            .filter(Service.active == True)
            .count()
        )

        appointments_count = (
            db.query(Appointment).count()
        )

        pending_count = (
            db.query(Appointment)
            .filter(
                Appointment.status == "pending"
            )
            .count()
        )

        return templates.TemplateResponse(
            request=request,
            name="admin_dashboard.html",
            context={
                "request": request,
                "clients_count": clients_count,
                "services_count": services_count,
                "appointments_count": appointments_count,
                "pending_count": pending_count,
            },
        )

    finally:
        db.close()