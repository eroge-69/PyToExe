# programa que le solicite al usuario un entero y lo imprima por pantalla.
ejercicio_1 = input("1. ingrese un numero: ")
print(ejercicio_1)

# programa que le solicite al usuario dos números enteros y luego imprima por pantalla:

numero_1 = int(input("2. ingrese un numero: "))
numero_2 = int(input("ingrese otro numero: "))

print(numero_1)
print(numero_2)
print(numero_1 + numero_2)
print(numero_1 - numero_2)
print(numero_1 * numero_2)
print(numero_1 // numero_2)
print(numero_1 % numero_2)

# programa que solicite al usuario un numero entero y este determine si es par o impar

def par_o_impar():
    numero = int(input("3. ingrese un numero entero: "))
    print(numero)
    if numero % 2==0:
       print(f"El número es par")
    else: 
       print(f"El número es impar")

par_o_impar() 

# programa que pida año de nacimiento del usuario y otro año, y le diga que edad tenia en ese año

año_de_nacimiento = int(input("4. ingresar año de nacimiento "))
print(año_de_nacimiento)
año_aleatorio = int(input("ingresar otro año "))
print(año_aleatorio)
print("el usuario en ese año tenia: ")
print(año_aleatorio - año_de_nacimiento)

# programa que le pida 5 numero enteros sl usuario y muestre el promedio de ellos 

def calcular_promedio ():
    numero_1 = int(input("5. ingresar un numero: "))
    print(numero_1)
    numero_2 = int(input("ingresar otro numero: "))
    print(numero_2)
    numero_3 = int(input("ingresar un tercer numero: "))
    print(numero_3)
    numero_4 = int(input("ingresar un cuarto numero: "))
    print(numero_4)
    numero_5 = int(input("ingresar un ultimo numero: "))
    print(numero_5)
    numeros = (numero_1, numero_2, numero_3, numero_4, numero_5)
    promedio = sum(numeros) / len(numeros)
    print(f" El promedio de los numeros ingresados es: {promedio}")
calcular_promedio()