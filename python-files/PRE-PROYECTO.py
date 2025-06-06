
lista_productos = []

while True:
    print("\n--- MENÚ DE OPCIONES ---\n")
    print("1. Ingresar producto.")
    print("2. Ver producto.")
    print("3. Buscar producto.")
    print("4. Eliminar producto.")
    print("5. EXIT.")

    menu = input("\nIngrese la opción que desea seleccionar: \n")


    match menu:
        case "1":
            print("___Agregar producto___\n")

            agregar = input("Ingrese el producto que desea agregar: ").lower().strip()
            categoria = input("Ingrese la categoría del producto: ").lower().strip()
            precio = int(input("Ingrese el precio del producto sin centavos:$ "))

            if precio <0:
                 print("El numero no puede ser negativo.")
                 continue

            elif agregar == "":
                    print("El campo no puede estar vacío. Por favor intente de nuevo.\n")
            elif agregar in lista_productos:
                    print("El producto ya existe. Por favor intente de nuevo.\n")
            else:
                lista_productos.append([agregar, categoria, precio])
                print("Producto ingresado con éxito\n")
                print(f"Nombre: {agregar}\nCategoría: {categoria}\nPrecio:$ {precio}")
                

        case "2":
            print("___Ver productos___\n")
            
            if not lista_productos:
                 print("El producto no existe.\n")

            contador = 1
            for i in lista_productos:
                print(f"{contador} Nombre: {i[0]}\nCategoría: {i[1]}\nPrecio: ${i[2]}")
                contador += 1

            
        case "3":
            print("\n___Buscar productos___\n")

            buscador = input("Ingrese el producto a buscar: ").lower().strip()

            encontrado = False
            for producto in lista_productos:
                if buscador == producto[0]:
                    print(f"Producto encontrado:\nNombre: {producto[0]}\nCategoría: {producto[1]}\nPrecio: ${producto[2]}")
                    encontrado = True
                    break
            if not encontrado:
                print("El producto no existe.")

            
        case "4":
            print("\n___Eliminar productos___\n")

            eliminar = input("Ingrese el producto a eliminar: ").lower().strip()

            encontrado = False
            for producto in lista_productos:
                if producto[0] == eliminar:
                    lista_productos.remove(producto)
                    print(f"El producto '{eliminar}' fue eliminado.")
                    encontrado = True
                    break
            if not encontrado:
                print("El producto que desea eliminar no existe.")
               
        case "5":
            print("Saliendo...")
            print("Programa finalizado.")
            break
            