import itertools
import string

def generar_combinaciones(limite=1000):
    letras = string.ascii_uppercase  # Letras A-Z
    contador = 0

    for numeros in itertools.product("0123456789", repeat=8):
        num_str = "".join(numeros)
        for letra in letras:
            print(num_str + letra, flush=True)
            contador += 1
            if contador >= limite:
                return  # salimos después de imprimir "limite" combinaciones

if __name__ == "__main__":
    generar_combinaciones()
    input("\n✅ Fin. Pulsa ENTER para salir...")
