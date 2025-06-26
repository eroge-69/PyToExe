import random as rd

def adivinar():
    # Creo variables para los datos generales
    numeros = "12345"
    letras = "ABCDE"
    puntosGT = 200
    puntosGP = 50
    intentos = 5
    jugadores = 2
    # Guardare el lista paralelas los nombres de jugadores y sus puntos
    # Se puede hacer en variable independiente pero el uso de lista me permite tener más jugadores
    lNombresJugadores = []
    lPuntosJugadores = []

    # El primer for es para los jugadores
    for i in range(jugadores):
        # Para cada jugador pido su nombre y genero los primeros datos aleatorio
        print("Ingrese el nombre del jugador",(i+1),": ")
        lNombresJugadores.append(input())
        numA = rd.choice(numeros)
        letA = rd.choice(letras)
        # Cada jugador empieza con 0 puntos
        puntos = 0
        # El segundo for es para los intentos de cada jugador
        for i in range(intentos):
            # Muestro siempre las opciones que tiene para seleccionar
            print("Las opciones de números a adivinar son:" , numeros)
            print("Las opciones de letras a adivinar son:", letras)
            # Pido el numero y la letra
            num = input("Ingrese el número: ")
            let = input("Ingrese la letra: ")

            if num==numA and let==letA: # Si adivina ambas cosas ingresa
                # Sumo los puntos y genero nuevamente el número y letra aletoriamente
                puntos += puntosGT
                numA = rd.choice(numeros)
                letA = rd.choice(letras)
                print("Adivinó la letra y el número")
            elif num==numA:  # Si solo adivina el número
                # Sumo los puntos y genero el número aleatoriamente
                puntos += puntosGP
                numA = rd.choice(numeros)
                print("Adivinó el número")
            elif  let==letA: # Si solo adivina la letra
                # Sumo los puntos y genero nuevamente letra aletoriamente
                puntos += puntosGT
                letA = rd.choice(letras)
                print("Adivinó la letra")
            else: # Sino adivino solo muestro un mensaje
                print("No adivinó")
        # Al final de los intentos guardo los puntos de ese jugador
        lPuntosJugadores.append(puntos)

    # Cuando ya jugaron todos, presento sus nombres y puntos
    for i in range(len(lPuntosJugadores)):
        print ("El jugador", lNombresJugadores[i],"tiene:",str(lPuntosJugadores[i]),"puntos.")

    # Identifico el valor mayor
    puntajeMayor = max(lPuntosJugadores)
    # Recorro todos los datos por si acaso hay algunos con jugadores que tienen ese valor
    for i in range(len(lPuntosJugadores)):
        # Solamente muestro los datos de los jugadores que tiene el valor máximo
        if lPuntosJugadores[i]==puntajeMayor:
            print ("El jugador", lNombresJugadores[i],"GANA con:",str(lPuntosJugadores[i]),"puntos.")

# Llamo a la función
adivinar()