import pygame
import sys

pygame.init()
pygame.mixer.init()

# Configurações da tela
W, H = 400, 700
tela = pygame.display.set_mode((W, H))
pygame.display.set_caption("Lara Bijus 💖")

# Cores
ROSA_BEBE = (255, 228, 240)
ROSA_FORTE = (255, 105, 180)
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
CINZA_CLARO = (230, 230, 230)

# Fontes
fonte_pequena = pygame.font.SysFont("arial", 16)
fonte_media = pygame.font.SysFont("arial", 20, bold=True)
fonte_grande = pygame.font.SysFont("arial", 24, bold=True)

# Produtos
produtos = [
    {"nome": "Colar rosa e verde", "preco": 25.90, "img": None},
    {"nome": "kit pulseira azul e laranja", "preco": 15.00, "img": None},
    {"nome": "conjunto pulsera rubi", "preco": 25.50, "img": None},
    {"nome": "pulera ursinhos coloridos", "preco": 15.00, "img": None},
    {"nome": "bobby goods", "preco": 35.00, "img": None},
]

# Carregando imagens dos produtos (coloque os arquivos na pasta)
arquivos_imagem = ["colar.png", "pulseira.png", "brinco.png", "anel.png", "tiara.png"]
for p, arquivo_img in zip(produtos, arquivos_imagem):
    try:
        p["img"] = pygame.image.load(arquivo_img)
    except:
        sup = pygame.Surface((90, 90))
        sup.fill(ROSA_FORTE)
        p["img"] = sup

# Carregar imagem do QR Code Pix (qrcode.png na pasta), sem redimensionar
try:
    img_qrcode = pygame.image.load("qrcode.png")
except Exception as e:
    print("Erro ao carregar qrcode.png:", e)
    img_qrcode = None

carrinho = []
tela_atual = "loja"

def desenhar_texto(texto, fonte, cor, surface, x, y):
    txt = fonte.render(texto, True, cor)
    surface.blit(txt, (x, y))

def botao(surface, rect, texto, cor_fundo, cor_texto, hover=False):
    color = cor_fundo
    if hover:
        color = tuple(max(0, c-30) for c in cor_fundo)
    pygame.draw.rect(surface, color, rect, border_radius=12)
    desenhar_texto(texto, fonte_pequena, cor_texto, surface, rect.x + 15, rect.y + 10)

def desenhar_loja():
    tela.fill(ROSA_BEBE)
    desenhar_texto("     Lara Biju", fonte_grande, ROSA_FORTE, tela, 110, 10)
    y = 70
    botoes_produtos = []
    for p in produtos:
        rect = pygame.Rect(30, y, 340, 90)
        pygame.draw.rect(tela, BRANCO, rect, border_radius=12)

        if p["img"]:
            img = pygame.transform.smoothscale(p["img"], (80, 80))
            tela.blit(img, (rect.x + 10, rect.y + 5))

        desenhar_texto(p["nome"], fonte_media, PRETO, tela, rect.x + 100, rect.y + 10)
        desenhar_texto(f"R$ {p['preco']:.2f}", fonte_media, ROSA_FORTE, tela, rect.x + 100, rect.y + 45)

        btn_rect = pygame.Rect(rect.right - 110, rect.y + 45, 90, 35)
        btn_hover = btn_rect.collidepoint(pygame.mouse.get_pos())
        botao(tela, btn_rect, "Comprar", ROSA_FORTE, BRANCO, btn_hover)

        botoes_produtos.append((btn_rect, p))
        y += 100

    btn_carrinho = pygame.Rect(50, H - 75, 300, 45)
    btn_hover = btn_carrinho.collidepoint(pygame.mouse.get_pos())
    botao(tela, btn_carrinho, f"Ver Carrinho ({len(carrinho)})", ROSA_FORTE, BRANCO, btn_hover)

    return botoes_produtos, btn_carrinho

def desenhar_carrinho():
    tela.fill(BRANCO)
    desenhar_texto("Carrinho 🛒", fonte_grande, ROSA_FORTE, tela, 150, 10)
    y = 70
    botoes_remover = []
    total = 0.0
    for i, p in enumerate(carrinho):
        rect = pygame.Rect(30, y, 340, 70)
        pygame.draw.rect(tela, CINZA_CLARO, rect, border_radius=12)
        img = pygame.transform.smoothscale(p["img"], (60, 60))
        tela.blit(img, (rect.x + 10, rect.y + 5))
        desenhar_texto(p["nome"], fonte_media, PRETO, tela, rect.x + 85, rect.y + 10)
        desenhar_texto(f"R$ {p['preco']:.2f}", fonte_media, ROSA_FORTE, tela, rect.x + 85, rect.y + 40)

        btn_remover = pygame.Rect(rect.right - 65, rect.y + 15, 45, 25)
        btn_hover = btn_remover.collidepoint(pygame.mouse.get_pos())
        botao(tela, btn_remover, "X", (255, 100, 100), BRANCO, btn_hover)
        botoes_remover.append((btn_remover, i))
        total += p['preco']
        y += 80

    desenhar_texto(f"Total: R$ {total:.2f}", fonte_media, ROSA_FORTE, tela, 30, H - 140)

    btn_voltar = pygame.Rect(50, H - 85, 120, 45)
    btn_finalizar = pygame.Rect(230, H - 85, 120, 45)
    botao(tela, btn_voltar, "Voltar", ROSA_FORTE, BRANCO, btn_voltar.collidepoint(pygame.mouse.get_pos()))
    botao(tela, btn_finalizar, "Finalizar", ROSA_FORTE, BRANCO, btn_finalizar.collidepoint(pygame.mouse.get_pos()))

    return botoes_remover, btn_voltar, btn_finalizar

def desenhar_qrcode_e_instrucao():
    tela.fill(ROSA_BEBE)
    desenhar_texto("Pague com Pix 💖", fonte_grande, ROSA_FORTE, tela, 110, 10)

    if img_qrcode:
        pos_x = (W - img_qrcode.get_width()) // 2
        pos_y = 70
        tela.blit(img_qrcode, (pos_x, pos_y))
    else:
        desenhar_texto("QR Code não encontrado.", fonte_media, (255, 0, 0), tela, 80, 180)

    texto = [
        "Após o pagamento, envie um e-mail",
        "guilhermelclfreire@gmail.com",
        "",
        "Anexe o comprovante e o nome",
        "do(s) item(ns) comprado(s).",
        "para finalizar a compra",
        "Obrigado pela preferência! 💖"
    ]
    y = 320
    for linha in texto:
        desenhar_texto(linha, fonte_media, ROSA_FORTE, tela, 40, y)
        y += 30

    btn_ok = pygame.Rect(140, H - 85, 120, 45)
    btn_hover = btn_ok.collidepoint(pygame.mouse.get_pos())
    botao(tela, btn_ok, "Ok", ROSA_FORTE, BRANCO, btn_hover)
    return btn_ok

clock = pygame.time.Clock()

while True:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if tela_atual == "loja":
                botoes, btn_carrinho = desenhar_loja()
                for btn, p in botoes:
                    if btn.collidepoint(mouse_pos):
                        carrinho.append(p)
                if btn_carrinho.collidepoint(mouse_pos):
                    tela_atual = "carrinho"

            elif tela_atual == "carrinho":
                botoes_remover, btn_voltar, btn_finalizar = desenhar_carrinho()
                for btn, idx in botoes_remover:
                    if btn.collidepoint(mouse_pos):
                        carrinho.pop(idx)
                if btn_voltar.collidepoint(mouse_pos):
                    tela_atual = "loja"
                if btn_finalizar.collidepoint(mouse_pos):
                    if len(carrinho) > 0:
                        tela_atual = "qrcode"

            elif tela_atual == "qrcode":
                btn_ok = desenhar_qrcode_e_instrucao()
                if btn_ok.collidepoint(mouse_pos):
                    tela_atual = "loja"
                    carrinho.clear()

    if tela_atual == "loja":
        desenhar_loja()
    elif tela_atual == "carrinho":
        desenhar_carrinho()
    elif tela_atual == "qrcode":
        desenhar_qrcode_e_instrucao()

    pygame.display.flip()
    clock.tick(60)
