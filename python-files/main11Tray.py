 

# import requests
# import win32print
# import win32ui
# import base64
# from io import BytesIO
# import qrcode
# from PIL import Image, ImageWin

import requests
import win32print
import win32ui
import base64
import qrcode
from PIL import Image, ImageWin
from io import BytesIO
import threading
import time
import pystray
from pystray import MenuItem as item
from PIL import Image as PILImage
import sys

# Caminho do arquivo de configuração
parametros_path = "C:\\CCSTecno\\parametros_impressao.txt"

INTERVALO_PADRAO  = 10  # EM SEGUNDOS

def ler_parametros():
    """
    Lê os parâmetros do arquivo e retorna a URL e o ID da impressora.
    """
    parametros = {}
    try:
        with open(parametros_path, "r", encoding="utf-8") as file:
            for line in file:
                if "=" in line:
                    chave, valor = line.strip().split("=")
                    parametros[chave] = valor
        
        url = parametros.get("url", "").strip()
        id_impressora = parametros.get("id_impressora", "").strip()
        intervalo = int(parametros.get("intervalo", INTERVALO_PADRAO))  # Lê o intervalo ou usa o padrão

        if not url or not id_impressora:
            raise ValueError("Arquivo de parâmetros incompleto ou inválido.")
        
        return url, id_impressora, intervalo
    except Exception as e:
        print(f"❌ Erro ao ler o arquivo de parâmetros: {e}")
        return None, None, INTERVALO_PADRAO

# Lendo os parâmetros do arquivo
#url, id_impressora = ler_parametros()

# if not url or not id_impressora:
#     exit("❌ Não foi possível carregar os parâmetros de configuração.")

# Parâmetros para requisição
# data = {
#     "PROCEDURE": "CCS_P_IMPRESSAO_ETQ",
#     "pID_IMPRESSORA": id_impressora  
# }

def my_barcode_128(code_str: str) -> str:
    """
    Converte uma string para o formato correto de Code 128 para ser usada com a fonte Code 128.
    """
    if not code_str:
        return ""

    charsetB = True
    my_barcode_128 = ""
    
    # Verificar caracteres válidos
    for char in code_str:
        if not (32 <= ord(char) <= 126 or ord(char) == 203):
            return ""

    i = 0
    while i < len(code_str):
        if charsetB:
            mini = 4 if i == 0 or (i + 3) == len(code_str) else 6

            if (i + mini) <= len(code_str):
                for j in range(mini):
                    if not (48 <= ord(code_str[i + j]) <= 57):
                        break
                else:
                    # Troca para Code C
                    my_barcode_128 += chr(210) if i == 0 else chr(204)
                    charsetB = False

            if charsetB:
                if i == 0:
                    my_barcode_128 = chr(209)  # START-B
        if not charsetB:
            mini = 2
            if (i + mini) <= len(code_str):
                for j in range(mini):
                    if not (48 <= ord(code_str[i + j]) <= 57):
                        break
                else:
                    dummy = int(code_str[i:i+2])
                    dummy = dummy + 32 if dummy < 95 else dummy + 105
                    my_barcode_128 += chr(dummy)
                    i += 2
                    continue
            
            my_barcode_128 += chr(205)
            charsetB = True

        if charsetB:
            my_barcode_128 += code_str[i]
            i += 1

    # Cálculo do checksum
    checksum = ord(my_barcode_128[0]) - (32 if ord(my_barcode_128[0]) < 127 else 105)
    for i, char in enumerate(my_barcode_128[1:], start=1):
        dummy = ord(char) - (32 if ord(char) < 127 else 105)
        checksum = (checksum + (i * dummy)) % 103

    checksum = checksum + 32 if checksum < 95 else checksum + 105
    my_barcode_128 += chr(checksum) + chr(211)  # Adiciona checksum e STOP

    return my_barcode_128

def imprimir_imagem_base64(pdc, x, y, base64_str, largura=200, altura=100):
    """ 
    Decodifica uma string Base64, redimensiona e imprime a imagem na posição especificada 
    """
    try:
        if not base64_str:
            print("❌ Nenhum dado de imagem Base64 fornecido!")
            return
        
        img_data = base64.b64decode(base64_str)
        img = Image.open(BytesIO(img_data))
        
        # Redimensiona a imagem
        img = img.resize((largura, altura), Image.LANCZOS)

        # Converte para modo compatível com impressão
        img = img.convert("RGB")

        # Obtém o contexto da impressora e imprime
        dib = ImageWin.Dib(img)
        x2 = x + largura
        y2 = y + altura
        dib.draw(pdc.GetHandleOutput(), (x, y, x2, y2))
        print(f"🖼️ Imagem (Base64) impressa em ({x}, {y}), tamanho {largura}x{altura}")
    except Exception as e:
        print(f"❌ Erro ao processar imagem Base64: {e}")

def imprimir_qrcode(pdc, x, y, tamanho, texto):
    """
    Gera um QRCode a partir do texto e imprime na posição especificada
    """
    try:
        qr = qrcode.QRCode(box_size=10, border=2)
        qr.add_data(texto)
        qr.make(fit=True)
        img = qr.make_image(fill="black", back_color="white")
        img = img.resize((tamanho, tamanho), Image.LANCZOS)
        dib = ImageWin.Dib(img.convert("RGB"))
        x2 = x + tamanho
        y2 = y + tamanho
        dib.draw(pdc.GetHandleOutput(), (x, y, x2, y2))
        print(f"📲 QRCode impresso em ({x}, {y}), tamanho {tamanho}x{tamanho}")
    except Exception as e:
        print(f"❌ Erro ao gerar/imprimir QRCode: {e}")

def imprimir_texto(etiqueta, nome_impressora, copias):
    """
    Processa as linhas do texto recebido e imprime na impressora correta, incluindo múltiplas imagens Base64 e QRCode, com alinhamento.
    """
    for copia in range(copias):
        print(f"🖨 Imprimindo cópia {copia + 1} de {copias} na impressora {nome_impressora}...")
        
        hprinter = win32print.OpenPrinter(nome_impressora)
        pdc = win32ui.CreateDC()
        pdc.CreatePrinterDC(nome_impressora)
        pdc.StartDoc(f"Etiqueta {copia + 1} de {copias}")
        pdc.StartPage()

        for linha in etiqueta.strip().split("\n"):
            try:
                valores = linha.split("; ")

                if valores[0] == "LINE":
                    espessura, x1, y1, x2, y2 = map(int, valores[1:])
                    pen = win32ui.CreatePen(0, espessura, 0)  
                    old_pen = pdc.SelectObject(pen)  
                    pdc.MoveTo(x1, y1) 
                    pdc.LineTo(x2, y2)
                    pdc.SelectObject(old_pen)

                elif valores[0] == "LOGO":
                    if len(valores) >= 6:
                        x, y, largura, altura = map(int, valores[1:5])
                        base64_str = valores[5]  # Captura a string Base64
                        imprimir_imagem_base64(pdc, x, y, base64_str, largura, altura)
                    else:
                        print(f"❌ Erro ao processar linha de LOGO: {linha}")
                
                elif valores[0] == "QRCODE":
                    if len(valores) >= 4:
                        x, y, tamanho, texto = int(valores[1]), int(valores[2]), int(valores[3]), valores[4]
                        imprimir_qrcode(pdc, x, y, tamanho, texto)
                    else:
                        print(f"❌ Erro ao processar linha de QRCODE: {linha}")

                else:
                    fonte, altura, peso, pos_x, pos_y, texto = valores[:6]
                    altura, peso, pos_x, pos_y = map(int, [altura, peso, pos_x, pos_y])
                    modo_negativo = valores[6] if len(valores) > 6 else ""
                    alinhamento = valores[7] if len(valores) > 7 else "ESQ"  # Default para esquerda

                    fonte_atual = win32ui.CreateFont({"name": fonte, "height": altura, "weight": peso})
                    pdc.SelectObject(fonte_atual)

                     # Se for um código de barras, converter
                    if fonte.lower().startswith("code") and "ean13" not in fonte.lower():
                        texto = my_barcode_128(texto)

                    text_size = pdc.GetTextExtent(texto)[0]
                    
                    if alinhamento == "DIR":
                        pos_x = pos_x - text_size if pos_x >= text_size else 0  # Evita posição negativa
                    elif alinhamento == "CENTRO":
                        pos_x = max(0, pos_x - text_size // 2)  # Centraliza garantindo posição válida
                    

                    if modo_negativo == "NEG":
                        pdc.SetBkMode(0)
                        pdc.SetTextColor(0xFFFFFF)
                        text_size = pdc.GetTextExtent(texto)
                        largura_fundo = text_size[0] + 10
                        altura_fundo = text_size[1] + 5
                        pdc.FillSolidRect((pos_x, pos_y, pos_x + largura_fundo, pos_y + altura_fundo), 0x000000)
                    else:
                        pdc.SetBkMode(1)
                        pdc.SetTextColor(0x000000)

                    pdc.TextOut(pos_x, pos_y, texto)

            except Exception as e:
                print(f"❌ Erro ao processar linha: {linha} - {e}")

        pdc.EndPage()
        pdc.EndDoc()
        pdc.DeleteDC()

    print(f"✅ Impressão concluída com sucesso ({copias} cópias) na impressora: {nome_impressora}")


# Função que faz a requisição e imprime
def verificar_e_imprimir():
    global timer
    print("🔍 Verificando API...")

    url, id_impressora, intervalo = ler_parametros()
    if not url or not id_impressora:
        print("❌ Parâmetros inválidos.")
        return
    
    data = {
        "PROCEDURE": "CCS_P_IMPRESSAO_ETQ",
        "pID_IMPRESSORA": id_impressora  
    }

    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            json_response = response.json()
            if isinstance(json_response, list) and len(json_response) > 0:
                for item in json_response:
                    etiqueta = item.get("etiqueta", "").strip()
                    nome_impressora = item.get("nome_impressora", "").strip()
                    copias = int(item.get("copias", 1))  

                    if etiqueta and nome_impressora:
                        imprimir_texto(etiqueta, nome_impressora, copias)
        else:
            print(f"❌ Erro ao chamar API: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro ao conectar à API: {e}")

    # Agendar próxima execução
    timer = threading.Timer(intervalo , verificar_e_imprimir)
    timer.start()

# Função para fechar o programa
def fechar_programa(icon, item):
    print("🛑 Fechando o programa...")
    timer.cancel()  # Para o timer
    icon.stop()     # Fecha o ícone da bandeja
    sys.exit()

# Criar ícone na bandeja
def criar_tray_icon():
    image = PILImage.new("RGB", (64, 64), (0, 0, 255))  # Ícone azul
    menu = (item("Sair", fechar_programa),)
    icon = pystray.Icon("Impressão Automática", image, "Impressora", menu)
    icon.run()

# Iniciar execução
if __name__ == "__main__":
    print("🚀 Serviço iniciado!")
    _, _, intervalo = ler_parametros()
    timer = threading.Timer(1, verificar_e_imprimir)
    timer.start()
    criar_tray_icon()