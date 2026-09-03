from database.database import Base, engine
from database.seed import seed_services

from models.appointment import Appointment
from models.client import Client
from models.client_protocol import ClientProtocol
from models.service import Service


print("Criando tabelas do Jeni Santos Nails...")

Base.metadata.create_all(bind=engine)

print("Banco de dados atualizado com sucesso!")

seed_services()