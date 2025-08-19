impuestos={
  "impuesto sobre venta":[],
  "Impuestos sobre la renta":[],
  "impuestos aduanerosa":[],
  "Impuestos sobre combustibles":[],
  "Impuesto sobre nóminas de trabajadores y mano de obra":[],
  "Impuesto sobre la propiedad ":[],
  "Impuestos sobre el Patrimonio":[],


}




import datetime

# Función para guardar en archivo
def guardar_log(texto):
    with open("acciones.txt", "a", encoding="utf-8") as archivo:
        fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        archivo.write(f"[{fecha_hora}] {texto}\n")

opcion=""
nombre=input("ingrese el nombre del usuario:")
print(f"Bienvenido(a){nombre}, a su calculadora de impustos, porfavor ingrese al menu y elija un impuesto\n")

while opcion!=8:

 print("\t\t\t*******************************MENU DE IMPUESTOS*******************************\n")
 print("\t\t\t*\t\t\t               1-impuestos sobre ventas                          \t\t\t*")
 print("\t\t\t*\t\t\t               2- Impuestos sobre la renta                       \t\t\t*")
 print("\t\t\t*\t\t\t               3-impuestos aduaneros                             \t\t\t*")
 print("\t\t\t*\t\t\t               4- Impuestos sobre combustibles                   \t\t\t*")
 print("\t\t\t*\t\t\t      5- Impuesto sobre nóminas de trabajadores y mano de obra   \t\t\t*")
 print("\t\t\t*\t\t\t              6- Impuesto sobre la propiedad                     \t\t\t*")
 print("\t\t\t*\t\t\t               7- Impuestos sobre el Patrimonio                  \t\t\t*")
 print("\t\t\t*\t\t\t                         8-salir                                 \t\t\t*")
 print("\t\t\t*******************************************************************************\n")
 
 opcion=int(input("seleccione cualquiera de estas 8 opciones:"))

 if opcion == 1:
    print("\t\t\t*****************************Impuestos sobre ventas*****************************")
    valor1 = float(input("Ingrese el valor de las importaciones: "))
    impuestosobreventa = 0.012
    impuesto = valor1 * impuestosobreventa
    print("Su impuesto sobre venta es:", impuesto)

 elif opcion == 2:
    print("\t\t\t****************************Impuestos sobre la renta****************************")
    valor2 = float(input("Ingrese el valor de la renta: "))
    impuestosobrerenta = 0.08
    impuesto2 = impuestosobrerenta * valor2
    print("Su impuesto sobre renta es:", impuesto2)

 elif opcion == 3:
    print("\t\t\t****************************Impuestos aduaneros****************************")
    valor3 = float(input("Ingrese el valor del contenido: "))
    impuestoaduaneros = 0.012
    impuesto3 = impuestoaduaneros * valor3
    print("Su impuesto aduanero es:", impuesto3)

 elif opcion == 4: 
    print("\t\t\t*************************Impuestos sobre combustibles*************************") 
    valor4 = float(input("Ingrese el valor del combustible: "))
    impuestocombustible=0.016
    impuesto4= impuestocombustible*valor4
    print("Su impuesto sobre combustible es:", impuesto4)

 elif opcion == 5:
    print("\t\t\t*********************Impuesto sobre nóminas de trabajadores y mano de obra*********************")
    valor5=float(input("Ingrese el valor del pago"))
    impuestodeanonimas=0.03
    impuesto5=valor5*impuestodeanonimas
    print("Su impuesto sobre anonimas en el pago es:", impuesto5)


 elif opcion == 6:
    print("\t\t\t*************************Impuesto sobre la propiedad*************************") 
    valor6 = float(input("Ingrese el valor de la propiedad: "))
    impuestopropiedad=0.05
    impuesto6= impuestopropiedad*valor6

    print("Su impuesto sobre la propiedad es:", impuesto6)


 elif opcion == 7:
    print("\t\t\t*************************Impuestos sobre el Patrimonio*************************")
    valor7 = float(input("Ingrese el valor de la propiedad: "))
    impuestopatrimonio=0.01
    impuesto7= impuestopatrimonio*valor7

    print("Su impuesto sobre el patrimonio es:", impuesto7)
                                 

 elif opcion == 8:
    print("\t\t\t*************************SALIR*************************")
    print("Gracias por usar nuestro programa")

 else:
    print("Opción inválida")

    import datetime








