import pygame
import sys
from random import choice

# --- CONFIGURACIÓN ---
pygame.init()
pygame.mixer.init()

# Colores y fuente
color_fondo = (0, 0, 0)
color_marco = (255, 255, 255)
color_caja = (50, 50, 50)
color_texto = (0, 255, 0)
color_input = (200, 200, 200)
fuente_texto = pygame.font.SysFont('Courier', 22)

# Ventana
ancho, alto = 800, 600
pantalla = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption("Aventura 8 Bits Final")

# Idioma
idioma = "es"  # 'es' o 'en'

# --- DATOS DEL JUEGO ---
textos = {
    "es": {"norte":"norte","sur":"sur","este":"este","oeste":"oeste",
           "bienvenido":"¡Bienvenido a la aventura!", "inventario":"Inventario",
           "objetos":"Objetos", "comando":"Escribe un comando:"},
    "en": {"norte":"north","sur":"south","este":"east","oeste":"west",
           "bienvenido":"Welcome to the adventure!", "inventario":"Inventory",
           "objetos":"Objects", "comando":"Enter a command:"}
}

mundo = {
    "bosque": {
        "descripcion": {"es": "Estás en un bosque misterioso. Hay un camino al norte.",
                        "en": "You are in a mysterious forest. There is a path to the north."},
        "salidas": {"norte": "castillo"},
        "objetos": ["espada"]
    },
    "castillo": {
        "descripcion": {"es": "Llegas a un castillo antiguo. Las puertas están cerradas.",
                        "en": "You arrive at an ancient castle. The doors are closed."},
        "salidas": {"sur": "bosque"},
        "objetos": ["escudo"]
    }
}

# Protagonista
jugador = {
    "nombre": "Héroe",
    "vida": 100,
    "fuerza": 10,
    "inventario": [],
    "apariencia": "Humano"
}

escena_actual = "bosque"
entrada_texto = ""
mensajes = []

# --- FUNCIONES ---
def dibujar_texto(texto, x, y, color=color_texto):
    render = fuente_texto.render(texto, True, color)
    pantalla.blit(render, (x, y))

def generar_imagen_8bit():
    img = pygame.Surface((200, 200))
    colores = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255)]
    img.fill(choice(colores))
    return img

def reproducir_musica_8bit():
    frecuencia = choice([220, 330, 440, 550, 660])
    duracion = 500  # ms
    # Sonido simple
    try:
        sonido = pygame.mixer.Sound(buffer=pygame.sndarray.make_sound(
            (32767 * (pygame.surfarray.array2d(pygame.Surface((1, duracion))) % 2)).astype('int16')
        ))
        sonido.play()
    except:
        pass  # Manejo simple si falla el sonido

def procesar_comando(comando):
    global escena_actual
    partes = comando.lower().split()
    if not partes:
        return
    if partes[0] == "ir":
        if len(partes) > 1:
            direccion = partes[1]
            if direccion in mundo[escena_actual]["salidas"]:
                escena_actual = mundo[escena_actual]["salidas"][direccion]
                mensajes.append(f"Vas hacia {direccion}.")
            else:
                mensajes.append("No puedes ir por ahí.")
    elif partes[0] == "tomar":
        if len(partes) > 1:
            objeto = partes[1]
            if objeto in mundo[escena_actual].get("objetos", []):
                jugador["inventario"].append(objeto)
                mundo[escena_actual]["objetos"].remove(objeto)
                mensajes.append(f"{objeto} agregado al inventario.")
            else:
                mensajes.append(f"No hay {objeto} aquí.")
    elif partes[0] == "inventario":
        inv = ", ".join(jugador["inventario"]) or "Vacío"
        mensajes.append(f"{textos[idioma]['inventario']}: {inv}")
    else:
        mensajes.append("Comando no reconocido.")

# --- LOOP PRINCIPAL ---
reproducir_musica_8bit()
while True:
    pantalla.fill(color_fondo)
    
    # Marco y caja
    pygame.draw.rect(pantalla, color_marco, (50, 50, 700, 500), 3)
    pygame.draw.rect(pantalla, color_caja, (60, 60, 680, 480))
    
    # Descripción
    descripcion = mundo[escena_actual]["descripcion"][idioma]
    dibujar_texto(descripcion, 70, 70)
    
    # Objetos de la escena
    objetos = mundo[escena_actual].get("objetos", [])
    dibujar_texto(f"{textos[idioma]['objetos']}: {', '.join(objetos) if objetos else 'Ninguno'}", 70, 110)
    
    # Inventario en pantalla
    dibujar_texto(f"{textos[idioma]['inventario']}: {', '.join(jugador['inventario']) or 'Vacío'}", 70, 140)
    
    # Mensajes recientes
    for i, msg in enumerate(mensajes[-5:]):
        dibujar_texto(msg, 70, 180 + i*25, color=(200,200,200))
    
    # Imagen 8 bits
    img = generar_imagen_8bit()
    pantalla.blit(img, (550, 350))
    
    # Entrada de texto
    pygame.draw.rect(pantalla, (30,30,30), (60, 520, 680, 30))
    dibujar_texto(entrada_texto, 65, 525, color_input)
    
    pygame.display.flip()
    
    # Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN:
                procesar_comando(entrada_texto)
                entrada_texto = ""
            elif evento.key == pygame.K_BACKSPACE:
                entrada_texto = entrada_texto[:-1]
            else:
                entrada_texto += evento.unicode
