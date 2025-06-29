import time
import datetime
import webbrowser
import pyautogui
import os

# Caminhos dos arquivos TXT
ARQUIVO_NOME = "nome_paciente.txt"
ARQUIVO_CONTATO = "contato_whatsapp.txt"
ARQUIVO_REMEDIOS = "remedios.txt"

# Mensagem a ser enviada (com variáveis)
MODELO_MENSAGEM = """Bom dia, {nome}! 💊
Está quase na hora do seu remédio: {medicamento}
✅ Tome {quantidade} às {hora}."""

# Tempo de espera (em segundos) para carregar elementos
TEMPO_ESPERA = 5


def ler_arquivo(nome_arquivo):
    with open(nome_arquivo, 'r', encoding='utf-8') as f:
        return f.read().strip()


def obter_lista_de_remedios():
    remedios = []
    linhas = ler_arquivo(ARQUIVO_REMEDIOS).splitlines()
    for linha in linhas:
        partes = linha.strip().split(" - ")
        if len(partes) == 3:
            hora, medicamento, quantidade = partes
            remedios.append({
                "hora": hora.strip(),
                "medicamento": medicamento.strip(),
                "quantidade": quantidade.strip()
            })
    return remedios


def abrir_whatsapp_web():
    webbrowser.open("https://web.whatsapp.com ")
    print("Abrindo WhatsApp Web... Aguarde alguns segundos.")
    time.sleep(TEMPO_ESPERA)


def enviar_mensagem_whatsapp(contato, mensagem):
    try:
        import pywhatkit
        pywhatkit.sendwhatmsg_instantly(contato, mensagem, wait_time=10, tab_close=True)
        print(f"Mensagem enviada para {contato}")
    except Exception as e:
        print(f"Erro ao enviar mensagem via WhatsApp: {e}")


def verificar_horarios_e_enviar(remedios, nome_paciente, contato_whatsapp):
    while True:
        agora = datetime.datetime.now().strftime("%H:%M")

        for remedio in remedios:
            hora_remedio = remedio["hora"]
            delta_minutos = (
                datetime.datetime.strptime(hora_remedio, "%H:%M") -
                datetime.datetime.strptime(agora, "%H:%M")
            ).seconds // 60

            # Enviar se estiver entre 0 e 10 minutos antes do horário
            if 0 <= delta_minutos <= 10:
                mensagem = MODELO_MENSAGEM.format(
                    nome=nome_paciente,
                    medicamento=remedio["medicamento"],
                    quantidade=remedio["quantidade"],
                    hora=hora_remedio
                )

                print(f"\nEnviando lembrete para {nome_paciente} às {agora}:")
                print(mensagem)
                enviar_mensagem_whatsapp(contato_whatsapp, mensagem)

                # Evita reenvio imediato
                time.sleep(60)

        # Espera 1 minuto antes da próxima verificação
        time.sleep(60)


def main():
    print("Sistema de Lembrete de Remédios iniciado...\n")

    # Ler dados dos arquivos
    try:
        nome_paciente = ler_arquivo(ARQUIVO_NOME)
        contato_whatsapp = ler_arquivo(ARQUIVO_CONTATO)
        remedios = obter_lista_de_remedios()

        print(f"Paciente: {nome_paciente}")
        print(f"Contato: {contato_whatsapp}")
        print(f"Remédios configurados: {len(remedios)}\n")

        # Abrir WhatsApp Web
        abrir_whatsapp_web()

        # Iniciar loop de verificação
        verificar_horarios_e_enviar(remedios, nome_paciente, contato_whatsapp)

    except FileNotFoundError as e:
        print(f"❌ Arquivo não encontrado: {e}")
    except Exception as e:
        print(f"❌ Ocorreu um erro: {e}")


if __name__ == "__main__":
    main()