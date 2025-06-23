import pygame
import subprocess
import sys
import os
from datetime import datetime

ANCHO, ALTO = 800, 600
FPS = 60
ARCHIVO_RECIENTES = "recientes.txt"
MAX_RECIENTES = 5

pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("🎮 PapuLauncher 3000™ Simple Edition")
clock = pygame.time.Clock()

fuente = pygame.font.SysFont("Arial", 24)
fuente_titulo = pygame.font.SysFont("Arial", 32, bold=True)

# --- Paletas papusas ---
PALETAS = {
    "oscura": {
        "fondo": (30, 30, 50),
        "menu_bg": (50, 50, 80),
        "menu_text": (220, 220, 255),
        "menu_hover": (180, 180, 255),
        "caja": (60, 60, 90),
        "caja_sel": (90, 90, 130),
        "texto": (230, 230, 230)
    },
    "clara": {
        "fondo": (240, 240, 245),
        "menu_bg": (200, 200, 220),
        "menu_text": (40, 40, 50),
        "menu_hover": (80, 80, 120),
        "caja": (220, 220, 230),
        "caja_sel": (180, 180, 210),
        "texto": (30, 30, 40)
    },
    "neon": {
        "fondo": (10, 0, 20),
        "menu_bg": (40, 0, 60),
        "menu_text": (0, 255, 200),
        "menu_hover": (0, 180, 140),
        "caja": (20, 0, 40),
        "caja_sel": (0, 255, 255),
        "texto": (0, 255, 255)
    }
}

# Estado inicial paleta y fullscreen
paleta_actual = "oscura"
fullscreen_enabled = False
pantalla_completa = False

menu_items = ["Guía del Papu", "Sobre PapuLauncher", "Opciones", "Salir"]
submenu_opciones = ["Paleta Oscura", "Paleta Clara", "Paleta Neón", "Toggle Fullscreen (F11)"]

menu_rects = []
submenu_rects = []
submenu_visible = False

ARCHIVO_RECIENTES = "recientes.txt"
MAX_RECIENTES = 5

# Cargar juegos recientes
def cargar_recientes():
    if os.path.exists(ARCHIVO_RECIENTES):
        with open(ARCHIVO_RECIENTES, "r", encoding="utf-8") as f:
            lineas = [l.strip() for l in f.readlines()]
            return [l for l in lineas if os.path.isfile(l)]
    return []

def guardar_recientes(lista):
    with open(ARCHIVO_RECIENTES, "w", encoding="utf-8") as f:
        for ruta in lista[:MAX_RECIENTES]:
            f.write(ruta + "\n")

recientes = cargar_recientes()
seleccion_index = -1

def agregar_a_recientes(ruta):
    global recientes
    if ruta in recientes:
        recientes.remove(ruta)
    recientes.insert(0, ruta)
    guardar_recientes(recientes)

def dibujar_texto(texto, x, y, font, color, centrado=False):
    surf = font.render(texto, True, color)
    rect = surf.get_rect()
    if centrado:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    pantalla.blit(surf, rect)
    return rect

def ejecutar_juego(ruta):
    try:
        subprocess.Popen([sys.executable, ruta])
        agregar_a_recientes(ruta)
    except Exception as e:
        print("Error al ejecutar:", e)

def ventana_popup(titulo, texto):
    ancho_v, alto_v = 500, 300
    ventana = pygame.Surface((ancho_v, alto_v))
    ventana.fill(PALETAS[paleta_actual]["caja"])
    rect_ventana = ventana.get_rect(center=(ANCHO//2, ALTO//2))

    lineas = texto.split('\n')
    y_offset = 30
    fuente_popup = pygame.font.SysFont("Arial", 20)
    titulo_surf = fuente_popup.render(titulo, True, PALETAS[paleta_actual]["texto"])
    titulo_rect = titulo_surf.get_rect(center=(ancho_v//2, 20))
    ventana.blit(titulo_surf, titulo_rect)

    for linea in lineas:
        texto_surf = fuente_popup.render(linea, True, PALETAS[paleta_actual]["texto"])
        ventana.blit(texto_surf, (20, y_offset))
        y_offset += 25

    boton_rect = pygame.Rect(ancho_v//2 - 40, alto_v - 50, 80, 30)
    pygame.draw.rect(ventana, PALETAS[paleta_actual]["menu_bg"], boton_rect)
    cerrar_surf = fuente_popup.render("Cerrar", True, PALETAS[paleta_actual]["texto"])
    cerrar_rect = cerrar_surf.get_rect(center=boton_rect.center)
    ventana.blit(cerrar_surf, cerrar_rect)

    popup_activo = True
    while popup_activo:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if boton_rect.collidepoint(e.pos[0] - rect_ventana.x, e.pos[1] - rect_ventana.y):
                    popup_activo = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    popup_activo = False

        pantalla.fill(PALETAS[paleta_actual]["fondo"])
        dibujar_menu()
        dibujar_lista()
        pantalla.blit(ventana, rect_ventana)
        pygame.display.flip()
        clock.tick(FPS)

def dibujar_menu():
    pygame.draw.rect(pantalla, PALETAS[paleta_actual]["menu_bg"], (0, 0, ANCHO, 50))
    menu_rects.clear()
    x_offset = 10
    for item in menu_items:
        color = PALETAS[paleta_actual]["menu_text"]
        rect = dibujar_texto(item, x_offset, 10, fuente, color)
        menu_rects.append(rect)
        x_offset += rect.width + 30

    if submenu_visible:
        # Dibuja submenu debajo de "Opciones" (3er item)
        opciones_x = menu_rects[2].x
        opciones_y = 50
        submenu_rects.clear()
        for i, opt in enumerate(submenu_opciones):
            rect_sub = pygame.Rect(opciones_x, opciones_y + i*35, 180, 35)
            submenu_rects.append(rect_sub)
            pygame.draw.rect(pantalla, PALETAS[paleta_actual]["menu_bg"], rect_sub)
            dibujar_texto(opt, rect_sub.x + 10, rect_sub.y + 7, fuente, PALETAS[paleta_actual]["menu_text"])

def dibujar_lista():
    dibujar_texto("🎮 PapuLauncher 3000™ Simple Edition", ANCHO//2, 70, fuente_titulo, PALETAS[paleta_actual]["texto"], centrado=True)
    dibujar_texto("Juegos recientes:", 50, 110, fuente, PALETAS[paleta_actual]["texto"])

    for i, ruta in enumerate(recientes):
        rect = pygame.Rect(50, 140 + i*70, 700, 60)
        color = PALETAS[paleta_actual]["caja_sel"] if i == seleccion_index else PALETAS[paleta_actual]["caja"]
        pygame.draw.rect(pantalla, color, rect, border_radius=12)
        dibujar_texto(os.path.basename(ruta), rect.x + 10, rect.y + 15, fuente, PALETAS[paleta_actual]["texto"])

    # Zona arrastre
    zona_rect = pygame.Rect(50, ALTO - 100, 700, 60)
    pygame.draw.rect(pantalla, PALETAS[paleta_actual]["caja"], zona_rect, border_radius=12)
    dibujar_texto("⬇️ Arrastra aquí un archivo .py para lanzarlo", zona_rect.centerx, zona_rect.centery - 12, fuente, PALETAS[paleta_actual]["texto"], centrado=True)

# Variables globales
submenu_visible = False

running = True
while running:
    clock.tick(FPS)
    mouse_pos = pygame.mouse.get_pos()
    pantalla.fill(PALETAS[paleta_actual]["fondo"])

    dibujar_menu()
    dibujar_lista()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                if recientes:
                    seleccion_index = (seleccion_index + 1) % len(recientes)
            elif event.key == pygame.K_UP:
                if recientes:
                    seleccion_index = (seleccion_index - 1) % len(recientes)
            elif event.key == pygame.K_RETURN:
                if 0 <= seleccion_index < len(recientes):
                    ejecutar_juego(recientes[seleccion_index])
            elif event.key == pygame.K_F11:
                if fullscreen_enabled:
                    pantalla_completa = not pantalla_completa
                    if pantalla_completa:
                        pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)
                    else:
                        pantalla = pygame.display.set_mode((ANCHO, ALTO))

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Clic en menú
            for i, rect in enumerate(menu_rects):
                if rect.collidepoint(event.pos):
                    eleccion = menu_items[i]
                    if eleccion == "Guía del Papu":
                        ventana_popup("Guía del Papu",
                            "1. Arrastra un archivo .py dentro del recuadro.\n"
                            "2. Selecciona juegos con las flechas y Enter para jugar.\n"
                            "3. Los juegos se guardan en la lista reciente.\n"
                            "4. Haz clic en un juego para lanzarlo.\n\n"
                            "¡A papujugar sin drama!")
                        submenu_visible = False
                    elif eleccion == "Sobre PapuLauncher":
                        ventana_popup("Sobre PapuLauncher",
                            f"PapuLauncher 3000™ Simple Edition\nCreado con amor y mantequilla de maní.\nFecha: {datetime.now().strftime('%d/%m/%Y')}\n\nHecho para que los papus jueguen fácil y rápido.")
                        submenu_visible = False
                    elif eleccion == "Opciones":
                        submenu_visible = not submenu_visible
                    elif eleccion == "Salir":
                        running = False

            # Clic en submenu
            if submenu_visible:
                for i, rect_sub in enumerate(submenu_rects):
                    if rect_sub.collidepoint(event.pos):
                        opcion = submenu_opciones[i]
                        if opcion == "Paleta Oscura":
                            paleta_actual = "oscura"
                        elif opcion == "Paleta Clara":
                            paleta_actual = "clara"
                        elif opcion == "Paleta Neón":
                            paleta_actual = "neon"
                        elif opcion == "Toggle Fullscreen (F11)":
                            fullscreen_enabled = not fullscreen_enabled
                            texto_fs = "activada" if fullscreen_enabled else "desactivada"
                            ventana_popup("Fullscreen",
                                f"Opción fullscreen {texto_fs}.\n"
                                "Podés alternar con F11.")
                        submenu_visible = False

            # Clic en juegos recientes
            for i, ruta in enumerate(recientes):
                rect = pygame.Rect(50, 140 + i*70, 700, 60)
                if rect.collidepoint(event.pos):
                    ejecutar_juego(ruta)

        elif event.type == pygame.DROPFILE:
            archivo = event.file
            if archivo.endswith(".py") and os.path.isfile(archivo):
                ejecutar_juego(archivo)

    pygame.display.flip()

pygame.quit()
