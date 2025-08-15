import math as mt
def perimetro_de_viviani(R,n):
    delta_t=(2*mt.pi)/n
    suma_de_Rheimann=0.0

    for i in range(n):
        t=(i+0.5)*delta_t
        f_de_t=mt.sqrt(1+mt.cos(t/2)**2)
        suma_de_Rheimann+=f_de_t
    Longitud=(R/2)*suma_de_Rheimann*delta_t
    return Longitud

if __name__=="__main__":
    try:
        R=float(input("Ingrese el valor numérico del radio R de la esfera, en centímetros"))
        n=int(input("Ingrese el número de subintervalos para la aproximación con una suma de Rheimann"))
        perimetro=perimetro_de_viviani(R,n)
        print(f"El perímetro aproximado de la ventana de Viviani, utilizando {R} como el radio y {n} como la cantidad de subintervalos, equivale a {perimetro:.8f} centímetros")
    except ValueError:
        print("Por favor ingrese valores numéricos válidos.")

input("\nPresione ENTER para cerrar el programa.")