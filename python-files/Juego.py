def bucle_del_juego():
    juego_terminado = False
    juego_cerrado = False

    ## Establece la posición inicial de la serpiente
    x1 = ANCHO / 2
    y1 = ALTO / 2
    cambio_x1 = 0
    cambio_y1 = 0

    ## Establece el cuerpo de la serpiente
    lista_de_serpiente = []
    longitud_de_serpiente = 1

    ## Establece el poder-up
    x_del_poder-up = round(random.randrange(0, ANCHO - tamaño_del_bloque_del_poder-up) / 20) * 20
    y_del_poder-up = round(random.randrange(0, ALTO - tamaño_del_bloque_del_poder-up) / 20) * 20

    ## Establece el bucle del juego
    while not juego_terminado:
        while juego_cerrado:
            pantalla.fill(COLOR_DE_FONDO)
            mensaje = estilo_de_fuente.render("Presiona ESPACIO para jugar de nuevo", True, AMARILLO)
            pantalla.blit(mensaje, [ANCHO / 2 - 200, ALTO / 2 - 50])
            pygame.display.flip()

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    juego_terminado = True
                    juego_cerrado = False
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE:
                        bucle_del_juego()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                juego_terminado = True
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_LEFT:
                    cambio_x1 = -tamaño_del_bloque_de_la_serpiente
                    cambio_y1 = 0
                elif evento.key == pygame.K_RIGHT:
                    cambio_x1 = tamaño_del_bloque_de_la_serpiente
                    cambio_y1 = 0
                elif evento.key == pygame.K_UP:
                    cambio_y1 = -tamaño_del_bloque_de_la_serpiente
                    cambio_x1 = 0
                elif evento.key == pygame.K_DOWN:
                    cambio_y1 = tamaño_del_bloque_de_la_serpiente
                    cambio_x1 = 0

        if x1 >= ANCHO or x1 < 0 or y1 >= ALTO or y1 < 0:
            juego_cerrado = True

        x1 += cambio_x1
        y1 += cambio_y1
        pantalla.fill(COLOR_DE_FONDO)
        pygame.draw.rect(
            pantalla, AZUL, [x_del_poder-up, y_del_poder-up, tamaño_del_bloque_del_poder-up, tamaño_del_bloque_del_poder-up]
        )

        cabeza_de_serpiente = []
        cabeza_de_serpiente.append(x1)
        cabeza_de_serpiente.append(y1)
        lista_de_serpiente.append(cabeza_de_serpiente)
        if len(lista_de_serpiente) > longitud_de_serpiente:
            del lista_de_serpiente[0]

        for x in lista_de_serpiente[:-1]:
            if x == cabeza_de_serpiente:
                juego_cerrado = True

        dibujar_serpiente(tamaño_del_bloque_de_la_serpiente, lista_de_serpiente)
        mostrar_puntuación(longitud_de_serpiente - 1)

        pygame.display.flip()

        if x1 == x_del_poder-up and y1 == y_del_poder-up:
            x_del_poder-up = round(random.randrange(0, ANCHO - tamaño_del_bloque_del_poder-up) / 20) * 20
            y_del_poder-up = (
                round(random.randrange(0, ALTO - tamaño_del_bloque_del_poder-up) / 20) * 20
            )
            longitud_de_serpiente += 1

        reloj.tick(velocidad_de_la_serpiente)

    pygame.quit()
