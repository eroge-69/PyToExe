import requests

# Token do seu bot
TOKEN = '7607277018:AAFja9LUglDJ5r1_Qddng-3LEWwvK_QLaMA'

# Chat ID do grupo
chat_id = -4967494011

# Mensagem que deseja enviar
mensagem = "Olá, grupo! Esta é uma mensagem enviada via bot 🤖"

# URL da API do Telegram
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

# Parâmetros da requisição
payload = {
    "chat_id": chat_id,
    "text": mensagem
}

# Enviar requisição POST
response = requests.post(url, data=payload)

# Verificação de sucesso
if response.status_code == 200:
    print("✅ Mensagem enviada com sucesso!")
else:
    print("❌ Erro ao enviar mensagem:", response.text)
