import pygame
import constantes
from personaje import Personaje
from weapon import Weapon
from textos import DamageText
from items import Item, NPC
from mundo import Mundo
import os
import csv

# Funciones:
# Escalar imagen
def escalar_img(image, scale):
    w = image.get_width()
    h = image.get_height()
    nueva_imagen = pygame.transform.scale(image, (w * scale, h * scale))
    return nueva_imagen


# Función para contar elementos
def contar_elementos(directorio):
    return len(os.listdir(directorio))

# Función listar nombres elementos
def nombres_carpetas(directorio):
    return os.listdir(directorio)

# --- Función para crear NPC instancia si world.npc es dict con coords ---
def crear_npc_si_hay(world, npc_surface):
    """
    Si world.npc es un dict con 'x' y 'y' (lo que genera process_data),
    la convertimos a una instancia real de NPC (items.NPC) y asignamos a world.npc.
    """
    if world.npc and isinstance(world.npc, dict):
        coords = world.npc
        try:
            x = coords.get("x", None)
            y = coords.get("y", None)
            if x is None and "rect" in coords:
                x, y = coords["rect"].center
            # si aun así falta, no hacer nada
            if x is None or y is None:
                return
            npc_inst = NPC(x, y, npc_surface)
            world.npc = npc_inst
        except Exception as e:
            # en caso de error dejamos world.npc como estaba
            print("Error creando NPC:", e)
            return

# ---------------------------------------------------------------

pygame.init()
pygame.mixer.init()

ventana = pygame.display.set_mode((constantes.ANCHO_VENTANA,
                                   constantes.ALTO_VENTANA))
pygame.display.set_caption("Thor: Thrial of Thunders v0.08")

#variables
posicion_pantalla = [0, 0]
nivel = 1


#fuentes
font = pygame.font.Font("assets//fonts//letters.ttf", 20)
font_game_over = pygame.font.Font("assets//fonts//letters.ttf", 80)
font_reinicio = pygame.font.Font("assets//fonts//letters.ttf", 20)
font_inicio = pygame.font.Font("assets//fonts//letters.ttf", 20)
font_titulo = pygame.font.Font("assets//fonts//letters.ttf", 30)
font_by = pygame.font.Font("assets//fonts//letters.ttf", 15)

game_over_text = font_game_over.render("Game over", True, constantes.BLANCO)

texto_boton_reinicio = font_reinicio.render("Continue", True, constantes.NEGRO)

#botones de inicio
boton_jugar = pygame.Rect(constantes.ANCHO_VENTANA / 2-100,
                          constantes.ALTO_VENTANA / 2-50, 200, 50)
boton_salir = pygame.Rect(constantes.ANCHO_VENTANA / 2-100,
                          constantes.ALTO_VENTANA / 2+50, 200, 50)
texto_boton_jugar = font_inicio.render("Jugar", True,
                                       constantes.NEGRO)
texto_boton_salir = font_inicio.render("Salir", True,
                                       constantes.BLANCO)
#pantalla de inicio
def pantalla_inicio():
    ventana.fill(constantes.NEGRO)
    dibujar_texto("Thor: thrial of thunders", font_titulo, constantes.BLANCO,
                  constantes.ANCHO_VENTANA/5,
                  constantes.ALTO_VENTANA/2-200)
    dibujar_texto("brough to you by:", font_by, constantes.BLANCO,
                  constantes.ANCHO_VENTANA / 1.1-200,
                  constantes.ALTO_VENTANA /0.83-200)
    dibujar_texto("ASIER11711", font_titulo, constantes.BLANCO,
                  constantes.ANCHO_VENTANA /1.1-200,
                  constantes.ALTO_VENTANA/1.7+200)
    pygame.draw.rect(ventana, constantes.AMARILLO,boton_jugar)
    pygame.draw.rect(ventana, constantes.ROJO,boton_salir)
    ventana.blit(texto_boton_jugar, (boton_jugar.x + 50, boton_jugar.y + 10))
    ventana.blit(texto_boton_salir, (boton_salir.x + 50, boton_salir.y + 15))
    pygame.display.update()

# Importar imagenes
#energia
corazon_vacio = pygame.image.load(f"assets//images//items//heart_empty.png").convert_alpha()
corazon_vacio = escalar_img(corazon_vacio,constantes.SCALA_CORAZON)
corazon_mitad = pygame.image.load(f"assets//images//items//heart_half.png").convert_alpha()
corazon_mitad = escalar_img(corazon_mitad,constantes.SCALA_CORAZON)
corazon_lleno = pygame.image.load(f"assets//images//items//heart_full.png").convert_alpha()
corazon_lleno = escalar_img(corazon_lleno,constantes.SCALA_CORAZON)


# Personaje
animaciones = []
for i in range(3):
    img = pygame.image.load(f"assets//images//characters//player//f{i}.gif")
    img = escalar_img(img, constantes.SCALA_PERSONAJE)
    animaciones.append(img)

#enemigos
directorio_enemigos = "assets//images//characters//enemies"
tipo_enemigos = nombres_carpetas(directorio_enemigos)
animaciones_enemigos = []
for eni in tipo_enemigos:
    lista_temp = []
    ruta_temp = f"assets//images//characters//enemies//{eni}"
    num_animaciones = contar_elementos(ruta_temp)
    for i in range(num_animaciones):
        img_enemigo = pygame.image.load(f"{ruta_temp}//{eni}_{i + 1}.png").convert_alpha()
        img_enemigo = escalar_img(img_enemigo, constantes.SCALA_ENEMIGOS)
        lista_temp.append(img_enemigo)
    animaciones_enemigos.append(lista_temp)


# Arma
imagen_martillo = pygame.image.load(f"assets//images//weapons//martillo.png")
imagen_martillo = escalar_img(imagen_martillo, constantes.SCALA_ARMA)

# Balas
imagen_rayo = pygame.image.load(f"assets//images//weapons//rayo.png").convert_alpha()
imagen_rayo = escalar_img(imagen_rayo, constantes.SCALA_ARMA)

tile_list = []
for x in range(constantes.TILE_TYPES):
    tile_image = pygame.image.load(f"assets//images//tiles//tile ({x+1}).png").convert_alpha()
    tile_image = pygame.transform.scale(tile_image, (constantes.TILE_SIZE, constantes.TILE_SIZE))
    tile_list.append(tile_image)

#cargar imagenes de los items
potion_roja = pygame.image.load("assets//images//items//potion.png").convert_alpha()
potion_roja = escalar_img(potion_roja, 1.2)

apple = pygame.image.load("assets//images//items//apple.png").convert_alpha()
apple = escalar_img(apple, 1.2)

coin_images = []
ruta_img = "assets//images//items//coin"
num_coin_images = contar_elementos(ruta_img)
for i in range(num_coin_images):
    img = pygame.image.load(f"assets//images//items//coin//C{i + 1}.png").convert_alpha()
    img = escalar_img(img, 0.60)
    coin_images.append(img)

item_imagenes = [coin_images, [potion_roja], [apple]]

# --- IMAGENES DEL NPC Y DEL BELT ---
belt_img = pygame.image.load("assets//images//items//powerups//belt.png").convert_alpha()
belt_img = escalar_img(belt_img, 1.2)

npc_img = pygame.image.load("assets//images//characters//NPC//dwarve1.png").convert_alpha()
# Escalar para que encaje con TILE_SIZE (ajusta si hace falta)
npc_img = pygame.transform.scale(npc_img, (constantes.TILE_SIZE, constantes.TILE_SIZE))
# ------------------------------------

def dibujar_texto(texto, fuente, color, x, y):
    img =fuente.render(texto, True, color)
    ventana.blit(img, (x, y))

def vida_jugador():
    c_mitad_dibujado = False
    for i in range(4):
        if jugador.energia >= ((i+1)*25):
            ventana.blit(corazon_lleno, (5+i*50, 5))
        elif jugador.energia % 25 > 0 and c_mitad_dibujado == False:
            ventana.blit(corazon_mitad, (5+i*50, 5))
            c_mitad_dibujado = True
        else:
            ventana.blit(corazon_vacio, (5+i*50, 5))

def resetear_mundo():
    grupo_damage_text.empty()
    grupo_rayos.empty()
    grupo_items.empty()

    #crear lista de tile vacias
    data = []
    for fila in range(constantes.FILAS):
        filas = [2] * constantes.COLUMNAS
        data.append(filas)

    return data

world_data = []

for fila in range(constantes.FILAS):
    filas = [78] * constantes.COLUMNAS
    world_data.append(filas)

# cargar el archivo de los niveles
with open(f"niveles//nivel_1.csv", newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, fila in enumerate(reader):
        for y, columna in enumerate(fila):
            world_data[x][y] = int(columna)

world = Mundo()
world.process_data(world_data, tile_list, item_imagenes, animaciones_enemigos)

# Crear instancia NPC si world.npc quedó como dict con coords
crear_npc_si_hay(world, npc_img)

def dibujar_grid():
    for x in range(30):
        pygame.draw.line(ventana, constantes.BLANCO, (x*constantes.TILE_SIZE, 0), (x*constantes.TILE_SIZE, constantes.ALTO_VENTANA))
        pygame.draw.line(ventana, constantes.BLANCO, (0 ,x*constantes.TILE_SIZE), (constantes.ANCHO_VENTANA, x* constantes.TILE_SIZE))


# crear un jugador de la clase personajes
jugador = Personaje(850, 650, animaciones, constantes.VIDA_PERSONAJE, 1)


#crear lista de enemigos
lista_enemigos = []
for ene in world.lista_enemigo:
    lista_enemigos.append(ene)


# crear un arma de la clase weapon
martillo = Weapon(imagen_martillo, imagen_rayo)

# crear un grupo de sprites
grupo_damage_text = pygame.sprite.Group()
grupo_rayos = pygame.sprite.Group()
grupo_items = pygame.sprite.Group()
#añadir items desde la data del nivel
for item in world.lista_item:
    grupo_items.add(item)


# definir las variables de movimiento del jugador
mover_arriba = False
mover_abajo = False
mover_izquierda = False
mover_derecha = False

# controlar el framerate
reloj = pygame.time.Clock()

# Botón de reinicio
boton_reinicio = pygame.Rect(constantes.ANCHO_VENTANA / 2 - 100,
                             constantes.ALTO_VENTANA / 2 + 100, 200, 50)

pygame.mixer.music.load("assets/sounds/music.mp3")
pygame.mixer.music.play(-1)

sonido_disparo = pygame.mixer.Sound("assets//sounds//disparo.mp3")

mostrar_inicio = True
run = True
while run == True:
    if mostrar_inicio == True:
        pantalla_inicio()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if boton_jugar.collidepoint(event.pos):
                    mostrar_inicio = False
                if boton_salir.collidepoint(event.pos):
                    run = False
    else:
        # que vaya a 60 fps
        reloj.tick(constantes.FPS)
        ventana.fill(constantes.COLOR_FONDO)

        if jugador.vivo == True:
            # Calcular el movimiento del jugador
            delta_x = 0
            delta_y = 0

            if mover_derecha == True:
                delta_x = constantes.VELOCIDAD
            if mover_izquierda == True:
                delta_x = -constantes.VELOCIDAD
            if mover_arriba == True:
                delta_y = -constantes.VELOCIDAD
            if mover_abajo == True:
                delta_y = constantes.VELOCIDAD

            # mover al jugador
            posicion_pantalla, nivel_completado = jugador.movimiento(delta_x, delta_y, world.obstaculos_tiles,
                                                                     world.exit_tile)

            # actualizar mapa (esto desplaza tiles internamente)
            world.update(posicion_pantalla)

            # Actualizar estado jugador
            jugador.update()

            # Actualiza estado enemigo
            for ene in lista_enemigos:
                ene.update()

            # Actualiza estado arma (devuelve un rayo si disparas)
            rayo = martillo.update(jugador)
            if rayo:
                grupo_rayos.add(rayo)
                sonido_disparo.play()
            for rayo in grupo_rayos:
                damage, pos_damage = rayo.update(lista_enemigos, world.obstaculos_tiles)
                if damage:
                    if damage <= 20:
                        color_damage_text = (constantes.ROJO)
                    else:
                        color_damage_text = (constantes.MORADO)
                    damage_text = DamageText(pos_damage.centerx, pos_damage.centery, str(damage), font,
                                             color_damage_text)
                    grupo_damage_text.add(damage_text)

            # actualizar daño
            grupo_damage_text.update(posicion_pantalla)

            # actualizar items (estos suman posicion_pantalla internamente)
            grupo_items.update(posicion_pantalla, jugador)

            # NOTA: no sumamos posicion_pantalla a world.npc.rect aquí.
            # mantenemos world.npc.rect como coordenadas del MUNDO para que NPC.give() spawnee items correctamente.

        # dibujar mundo
        world.draw(ventana)

        # dibujar NPC (si existe) -> calculamos su rect en pantalla sumando posicion_pantalla
        if world.npc and not isinstance(world.npc, dict):
            # crear rect de pantalla sin mutar world.npc.rect (world coords)
            npc_screen_rect = world.npc.rect.copy()
            npc_screen_rect.x += posicion_pantalla[0]
            npc_screen_rect.y += posicion_pantalla[1]
            ventana.blit(world.npc.image, npc_screen_rect)

        # dibujar al jugador
        jugador.dibujar(ventana)

        # dibujar al enemigo
        for ene in lista_enemigos:
            if ene.energia == 0:
                lista_enemigos.remove(ene)
            if ene.energia > 0:
                ene.enemigos(jugador, world.obstaculos_tiles, posicion_pantalla,
                             world.exit_tile)
                ene.dibujar(ventana)

        # dibujar al arma
        martillo.dibujar(ventana)

        # dibujar balas
        for rayo in grupo_rayos:
            rayo.dibujar(ventana)

        # dibujar los corazones
        vida_jugador()

        # dibujar textos
        grupo_damage_text.draw(ventana)
        dibujar_texto(f"Scales: {jugador.score}", font, (255, 255, 255), 675, 5)
        # nivel
        dibujar_texto(f"Level: " + str(nivel), font, constantes.BLANCO, constantes.ANCHO_VENTANA / 2, 5)

        # dibujar items
        grupo_items.draw(ventana)

        # mostrar mensaje del NPC si está hablando
        if world.npc and getattr(world.npc, "talking", False):
            # mostramos el último mensaje en pantalla (puedes cambiar posición/estilo)
            dibujar_texto(world.npc.last_message, font, constantes.BLANCO, 10, constantes.ALTO_VENTANA - 40)

        # chequear si nivel completado
        if nivel_completado == True:
            if nivel < constantes.NIVEL_MAXIMO:
                nivel += 1
                world_data = resetear_mundo()
                # cargar el archivo de los niveles
                with open(f"niveles//nivel_{nivel}.csv", newline='') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    for x, fila in enumerate(reader):
                        for y, columna in enumerate(fila):
                            world_data[x][y] = int(columna)
                world = Mundo()
                world.process_data(world_data, tile_list, item_imagenes, animaciones_enemigos)
                # crear NPC si corresponde en este nuevo mundo
                crear_npc_si_hay(world, npc_img)

                jugador.actualizar_coordenadas(constantes.COORDENADAS[str(nivel)])

                # crear lista de enemigos
                lista_enemigos = []
                for ene in world.lista_enemigo:
                    lista_enemigos.append(ene)

                # limpiar items previos y añadir items desde la data del nivel
                grupo_items.empty()
                for item in world.lista_item:
                    grupo_items.add(item)

        if jugador.vivo == False:
            ventana.fill(constantes.ROJO_OSCURO)
            text_rect = game_over_text.get_rect(center=(constantes.ANCHO_VENTANA / 2, constantes.ALTO_VENTANA / 2))
            ventana.blit(game_over_text, text_rect)
            # Botón de reinicio
            pygame.draw.rect(ventana, constantes.AMARILLO, boton_reinicio)
            ventana.blit(texto_boton_reinicio,
                         (boton_reinicio.x + 30, boton_reinicio.y + 10))

        for event in pygame.event.get():
            # Para cerrar el juego
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    mover_izquierda = True
                if event.key == pygame.K_d:
                    mover_derecha = True
                if event.key == pygame.K_w:
                    mover_arriba = True
                if event.key == pygame.K_s:
                    mover_abajo = True

                # Interacción con NPC / puerta al pulsar E
                if event.key == pygame.K_e:
                    # primero comprobamos si hay NPC y proximidad en pantalla
                    if world.npc and not isinstance(world.npc, dict):
                        # calculamos la rect del NPC en pantalla (sin mutar rect en mundo)
                        npc_screen_rect = world.npc.rect.copy()
                        npc_screen_rect.x += posicion_pantalla[0]
                        npc_screen_rect.y += posicion_pantalla[1]

                        buffer = 50
                        proximidad_rect = pygame.Rect(jugador.forma.x - buffer, jugador.forma.y - buffer,
                                                      jugador.forma.width + 2 * buffer, jugador.forma.height + 2 * buffer)
                        if proximidad_rect.colliderect(npc_screen_rect):
                            # activar diálogo
                            world.npc.talking = True
                            world.npc.last_message = "Give me coins (press 1-9)."
                        else:
                            # si no estás cerca del NPC, dejamos la funcionalidad original de cambiar puerta
                            if world.cambiar_puerta(jugador, tile_list):
                                print("cambiar puerta")
                    else:
                        # si no hay NPC, comportame como antes
                        if world.cambiar_puerta(jugador, tile_list):
                            print("cambiar puerta")

                # Para cuando se suelta la tecla
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    mover_izquierda = False
                if event.key == pygame.K_d:
                    mover_derecha = False
                if event.key == pygame.K_w:
                    mover_arriba = False
                if event.key == pygame.K_s:
                    mover_abajo = False

            # manejo de dar monedas al NPC (1..9) si está hablando
            if event.type == pygame.KEYDOWN:
                if world.npc and getattr(world.npc, "talking", False):
                    numeros = {
                        pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3,
                        pygame.K_4: 4, pygame.K_5: 5, pygame.K_6: 6,
                        pygame.K_7: 7, pygame.K_8: 8, pygame.K_9: 9
                    }
                    if event.key in numeros:
                        amount = numeros[event.key]
                        # llamamos al give del NPC: pasamos jugador, grupo_items, imagenes necesarias
                        world.npc.give(amount, jugador, grupo_items, potion_roja, belt_img, item_imagenes)
                        # cerramos diálogo por ahora
                        world.npc.talking = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if boton_reinicio.collidepoint(event.pos) and not jugador.vivo:
                    jugador.vivo = True
                    jugador.energia = 100
                    jugador.score = 0
                    nivel = 1
                    world_data = resetear_mundo()
                    with open(f"niveles//nivel_{nivel}.csv", newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, fila in enumerate(reader):
                            for y, columna in enumerate(fila):
                                world_data[x][y] = int(columna)
                    world = Mundo()
                    world.process_data(world_data, tile_list, item_imagenes, animaciones_enemigos)
                    # crear NPC si corresponde
                    crear_npc_si_hay(world, npc_img)

                    jugador.actualizar_coordenadas(constantes.COORDENADAS[str(nivel)])

                    # limpiar enemigos e items antes de añadir para evitar duplicados
                    lista_enemigos = []
                    grupo_items.empty()

                    for item in world.lista_item:
                        grupo_items.add(item)
                    for ene in world.lista_enemigo:
                        lista_enemigos.append(ene)

        # actualizar pantalla dentro del bucle
        pygame.display.update()

pygame.quit()
