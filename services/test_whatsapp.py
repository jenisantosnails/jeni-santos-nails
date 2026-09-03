from services.whatsapp import send_whatsapp_message


print("=" * 50)
print(" TESTE DO SERVIÇO DE WHATSAPP")
print("=" * 50)

result = send_whatsapp_message(
    phone="5582999999999",
    message=(
        "Olá! Este é um teste do sistema "
        "Jeni Santos Nails."
    ),
)

print()
print("Resultado:")
print(result)

print()
print("=" * 50)
print(" TESTE CONCLUÍDO")
print("=" * 50)