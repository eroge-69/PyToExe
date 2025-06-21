import random
import datetime

def filter_num(cadena):
    caracteres_permitidos = ['0','1','2','3','4','5','6','7','8','9','+','-','*','/','(',')']
    resultado = ''.join([c for c in cadena if c in caracteres_permitidos])
    return resultado

def generar_historieta_por_palabras():
    sujetos = [
        "El pez", "Una nube", "Mi sombra", "Esa tostadora", "Un pixel", "El café", "Una cebolla", "Un gato",
        "Un caracol invisible", "El anciano del bosque", "Una lámpara encendida", "El código fuente", "Mi reflejo",
        "La puerta mágica", "Un meteorito parlante", "La mantequilla rebelde", "El reloj del fin del mundo",
        "Una zapatilla voladora", "El pingüino sabio", "Un árbol que canta"
    ]

    verbos = [
        "baila", "explota", "grita", "susurra", "salta", "se esconde", "rompe", "flota",
        "devora", "absorbe", "programa", "olvida", "construye", "vigila", "anula", "camina lentamente",
        "predice", "confiesa", "reprograma", "transforma"
    ]

    objetos = [
        "la lógica", "una galaxia", "el silencio", "mi alma", "una silla", "el universo", "la puerta", "el WiFi",
        "la esperanza", "un archivo .zip", "la realidad", "el sueño eterno", "una bicicleta cuántica",
        "el algoritmo secreto", "una tostadora sin pan", "el canal 404", "el tiempo comprimido",
        "un dado de 7 caras", "el diccionario sin palabras", "la conexión emocional"
    ]

    remates = [
        "sin razón aparente.", "antes del martes.", "en una dimensión paralela.", "porque sí.",
        "hasta que llueve café.", "sin dejar rastro.", "como si nada.", "en código binario.",
        "bajo la lluvia de asteroides.", "gritando '¡hola mundo!'", "por error del sistema.",
        "al ritmo de una cumbia galáctica.", "sin entender la sintaxis.", "dentro de un bucle infinito.",
        "cuando nadie lo esperaba.", "como si el tiempo se detuviera.", "entre líneas de código obsoleto.",
        "en el último segundo.", "mientras dormías.", "en el silencio absoluto."
    ]

    linea1 = f"{random.choice(sujetos)} {random.choice(verbos)} {random.choice(objetos)}"
    linea2 = f"{random.choice(remates)}"
    return f"{linea1} {linea2}"

def main():
    output = input("Tú: ")

    if any(op in output for op in ['+', '-', '*', '/']):
        try:
            resultado = eval(filter_num(output))
            print("Resultado:", resultado)
        except Exception as e:
            print("Error al evaluar la expresión:", e)

    elif any(palabra in output.lower() for palabra in ['segundo', 'minuto', 'hora', 'fecha', 'dia', 'mes', 'año']):
        print("La hora es:", datetime.datetime.now())

    else:
        historieta=""
        for i in range(1000):
            historieta+=generar_historieta_por_palabras()
        print(historieta)
    main()

if __name__ == "__main__":
    main()
