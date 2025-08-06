# Lista de planetas secretos
planetas_secretos = ["Zorlon", "Galatea", "Tierra", "Marte", "Saturno"]
coleccion_jugador = []

print("🌌 Bienvenido al juego 'Adivina el Planeta'")
print("Tienes que adivinar uno de los planetas secretos.")
print("Si aciertas, lo agregas a tu colección. ¡Buena suerte!\n")

# Pedimos al usuario que escriba su intento
intento = input("Escribe el nombre de un planeta: ")

# Comprobamos si el intento está en la lista
if intento in planetas_secretos:
    print(f"🎉 ¡Correcto! Has descubierto {intento}.")
    coleccion_jugador.append(intento)  # Lo agregamos a la colección
else:
    print(f"❌ Lo siento, {intento} no es un planeta secreto.")

# Mostramos la colección final
print(f"\nTu colección de planetas: {coleccion_jugador}")
