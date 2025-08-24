# gerar_plaquinha_pix.py
# -*- coding: utf-8 -*-

import qrcode
from PIL import Image, ImageDraw, ImageFont
import unicodedata
import os

# ========= PAR�METROS DO USU�RIO =========
PIX_KEY = "14291459947"             # chave (CPF, telefone, e-mail ou EVP)
BENEFICIARIO = "Carlos Eduardo"     # at� 25 chars (ser� truncado)
CIDADE = "S�o Paulo"                # at� 15 chars (ser� truncado)
VALOR = None                        # ex.: "50.00" ou None para sem valor fixo
TXID = "***"                        # "***" em est�tico sem controle; at� 25 chars

# caminho do logo (PNG com fundo transparente preferencialmente)
LOGO_PATH = "pix-banco-central-brasil-logo.png"  # mude para o nome do seu arquivo local
GERAR_A4 = True                     # tamb�m gerar vers�o A4

# ========= FUN��ES AUXILIARES =========
def _strip_accents(s: str) -> str:
    """Remove acentos e normaliza para ASCII."""
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))

def _emv_tag(tag: str, value: str) -> str:
    """Monta campo EMV: TTLLVV..."""
    length = f"{len(value):02}"
    return f"{tag}{length}{value}"

def _crc16(payload: str) -> str:
    """
    Calcula CRC16/CCITT-FALSE conforme BR Code.
    Polin�mio 0x1021, inicial 0xFFFF, sem refinamentos.
    Retorna 4 hex mai�sculos.
    """
    data = payload.encode("utf-8")
    crc = 0xFFFF
    poly = 0x1021
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if (crc & 0x8000) != 0:
                crc = (crc << 1) ^ poly
            else:
                crc <<= 1
            crc &= 0xFFFF
    return f"{crc:04X}"

def montar_payload_pix(chave: str, nome: str, cidade: str, valor: str | None, txid: str = "***") -> str:
    """
    Monta o payload BR Code PIX est�tico.
    Campos relevantes:
      00 - Payload Format Indicator: "01"
      26 - Merchant Account Info (GUI + chave)
      52 - MCC: "0000"
      53 - Moeda: "986"
      54 - Valor (opcional)
      58 - Pa�s: "BR"
      59 - Nome (max 25)
      60 - Cidade (max 15)
      62 - Additional Data (txid)
      63 - CRC (calculado no final)
    """
    nome_norm = _strip_accents(nome).upper()[:25]
    cidade_norm = _strip_accents(cidade).upper()[:15]

    gui = _emv_tag("00", "BR.GOV.BCB.PIX")
    chave_tlv = _emv_tag("01", chave)
    # 26 = template com GUI + chave
    merchant_account_info = _emv_tag("26", gui + chave_tlv)

    # Campos fixos
    pfi = _emv_tag("00", "01")
    mcc = _emv_tag("52", "0000")
    moeda = _emv_tag("53", "986")
    pais = _emv_tag("58", "BR")
    nome_tlv = _emv_tag("59", nome_norm)
    cidade_tlv = _emv_tag("60", cidade_norm)

    # Valor (opcional)
    valor_tlv = _emv_tag("54", f"{float(valor):.2f}") if valor else ""

    # Additional Data Field Template (62): 05 = txid
    txid_tlv = _emv_tag("05", txid[:25] if txid else "***")
    addl = _emv_tag("62", txid_tlv)

    # 63 (CRC) entra como "6304" + CRC no fim (CRC calculado com "6304" + "0000" placeholder)
    sem_crc = pfi + merchant_account_info + mcc + moeda + valor_tlv + pais + nome_tlv + cidade_tlv + addl + "6304"
    crc = _crc16(sem_crc + "0000")
    payload = sem_crc + crc
    return payload

def gerar_qrcode(payload: str, caminho_saida: str = "pix_qrcode.png", box_size: int = 10, border: int = 4) -> str:
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=box_size, border=border)
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(caminho_saida)
    return caminho_saida

def carregar_fonte(prefer_bold=False, size=32):
    """Tenta carregar DejaVu (comum). Cai para default se n�o achar."""
    try:
        fname = "DejaVuSans-Bold.ttf" if prefer_bold else "DejaVuSans.ttf"
        return ImageFont.truetype(fname, size)
    except:
        return ImageFont.load_default()

def montar_plaquinha(qr_path: str,
                     beneficiario: str,
                     cidade: str,
                     logo_path: str | None = None,
                     saida: str = "plaquinha_pix.png",
                     tamanho=(600, 800),
                     incluir_titulo=True):
    W, H = tamanho
    placa = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(placa)

    # Logo (opcional)
    y_cursor = 30
    if logo_path and os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        # dimensiona para caber na largura com altura ~120
        target_h = 120
        ratio = target_h / logo.height
        logo = logo.resize((int(logo.width * ratio), target_h), Image.LANCZOS)
        placa.paste(logo, ((W - logo.width)//2, y_cursor), logo)
        y_cursor += target_h + 20

    # T�tulo
    if incluir_titulo:
        f_title = carregar_fonte(prefer_bold=True, size=40)
        draw.text((W//2, y_cursor + 20), "PAGUE COM PIX", font=f_title, fill="black", anchor="mm")
        y_cursor += 90

    # QR centralizado
    qr = Image.open(qr_path).convert("RGB")
    # redimensionar para ~400px se couber
    qr_size = min(400, W - 120)
    qr = qr.resize((qr_size, qr_size), Image.NEAREST)
    placa.paste(qr, ((W - qr_size)//2, y_cursor))

    # Textos finais
    f_text = carregar_fonte(size=28)
    y_base = y_cursor + qr_size + 30
    draw.text((W//2, y_base), f"Benefici�rio: {beneficiario}", font=f_text, fill="black", anchor="mm")
    draw.text((W//2, y_base + 40), f"Cidade: {cidade}", font=f_text, fill="black", anchor="mm")
    draw.text((W//2, y_base + 80), "Aproxime a c�mera do celular", font=f_text, fill="gray", anchor="mm")

    placa.save(saida)
    return saida

def montar_plaquinha_A4(qr_path: str,
                        beneficiario: str,
                        cidade: str,
                        logo_path: str | None = None,
                        saida: str = "plaquinha_pix_A4.png"):
    # A4 a 300 DPI ~ 2480 x 3508
    return montar_plaquinha(qr_path, beneficiario, cidade, logo_path, saida, tamanho=(2480, 3508), incluir_titulo=True)

# ========= EXECU��O =========
if __name__ == "__main__":
    payload = montar_payload_pix(PIX_KEY, BENEFICIARIO, CIDADE, VALOR, TXID)
    qr_path = gerar_qrcode(payload, "pix_qrcode.png", box_size=10, border=4)

    # Plaquinha padr�o (600x800)
    montar_plaquinha(qr_path,
                     beneficiario=BENEFICIARIO,
                     cidade=CIDADE,
                     logo_path=LOGO_PATH if os.path.exists(LOGO_PATH) else None,
                     saida="plaquinha_pix.png",
                     tamanho=(600, 800),
                     incluir_titulo=True)

    # Opcional: A4
    if GERAR_A4:
        montar_plaquinha_A4(qr_path,
                            beneficiario=BENEFICIARIO,
                            cidade=CIDADE,
                            logo_path=LOGO_PATH if os.path.exists(LOGO_PATH) else None,
                            saida="plaquinha_pix_A4.png")

    print("Payload PIX:\n", payload)
    print("Arquivos gerados: pix_qrcode.png, plaquinha_pix.png", "+ plaquinha_pix_A4.png" if GERAR_A4 else "")
