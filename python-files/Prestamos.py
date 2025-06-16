import csv
import os
from datetime import datetime

class Cliente:
    def __init__(self, id_cliente, nombre, identificacion, contacto):
        self.id_cliente = id_cliente
        self.nombre = nombre
        self.identificacion = identificacion
        self.contacto = contacto

class Prestamo:
    def __init__(self, id_prestamo, id_cliente, monto, tasa_interes, plazo, estado="Activo"):
        self.id_prestamo = id_prestamo
        self.id_cliente = id_cliente
        self.monto = monto
        self.tasa_interes = tasa_interes
        self.plazo = plazo  # En meses
        self.estado = estado
        self.saldo = monto

class Pago:
    def __init__(self, id_pago, id_prestamo, monto, fecha):
        self.id_pago = id_pago
        self.id_prestamo = id_prestamo
        self.monto = monto
        self.fecha = fecha

class Financiera:
    def __init__(self):
        self.clientes = []
        self.prestamos = []
        self.pagos = []
        self.cargar_datos()

    def generar_id(self, tipo):
        if tipo == "cliente":
            return max([c.id_cliente for c in self.clientes], default=0) + 1
        elif tipo == "prestamo":
            return max([p.id_prestamo for p in self.prestamos], default=0) + 1
        elif tipo == "pago":
            return max([p.id_pago for p in self.pagos], default=0) + 1

    def registrar_cliente(self, nombre, identificacion, contacto):
        nuevo_id = self.generar_id("cliente")
        cliente = Cliente(nuevo_id, nombre, identificacion, contacto)
        self.clientes.append(cliente)
        self.guardar_clientes()
        return cliente

    def registrar_prestamo(self, id_cliente, monto, tasa_interes, plazo):
        if id_cliente not in [c.id_cliente for c in self.clientes]:
            return "Cliente no encontrado"
        
        nuevo_id = self.generar_id("prestamo")
        prestamo = Prestamo(nuevo_id, id_cliente, monto, tasa_interes, plazo)
        self.prestamos.append(prestamo)
        self.guardar_prestamos()
        return prestamo

    def registrar_pago(self, id_prestamo, monto):
        prestamo = next((p for p in self.prestamos if p.id_prestamo == id_prestamo), None)
        if not prestamo:
            return "Préstamo no encontrado"
        
        if monto > prestamo.saldo:
            return "Monto excede el saldo pendiente"
        
        prestamo.saldo -= monto
        if prestamo.saldo == 0:
            prestamo.estado = "Pagado"
        
        nuevo_id = self.generar_id("pago")
        pago = Pago(nuevo_id, id_prestamo, monto, datetime.now().strftime("%Y-%m-%d"))
        self.pagos.append(pago)
        
        self.guardar_pagos()
        self.guardar_prestamos()
        return pago

    def calcular_cuota(self, id_prestamo):
        prestamo = next((p for p in self.prestamos if p.id_prestamo == id_prestamo), None)
        if not prestamo:
            return "Préstamo no encontrado"
        
        tasa_mensual = prestamo.tasa_interes / 12 / 100
        cuota = (prestamo.monto * tasa_mensual) / (1 - (1 + tasa_mensual) ** (-prestamo.plazo))
        return round(cuota, 2)

    def generar_reporte(self, tipo):
        if tipo == "clientes":
            return self.clientes
        elif tipo == "prestamos":
            return [p for p in self.prestamos]
        elif tipo == "morosos":
            return [p for p in self.prestamos if p.saldo > 0 and p.estado == "Activo"]
        elif tipo == "pagos":
            return self.pagos
        return []

    # Persistencia de datos
    def guardar_clientes(self):
        with open('clientes.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["id", "nombre", "identificacion", "contacto"])
            for c in self.clientes:
                writer.writerow([c.id_cliente, c.nombre, c.identificacion, c.contacto])

    def guardar_prestamos(self):
        with open('prestamos.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["id", "id_cliente", "monto", "tasa", "plazo", "estado", "saldo"])
            for p in self.prestamos:
                writer.writerow([p.id_prestamo, p.id_cliente, p.monto, p.tasa_interes, p.plazo, p.estado, p.saldo])

    def guardar_pagos(self):
        with open('pagos.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["id", "id_prestamo", "monto", "fecha"])
            for p in self.pagos:
                writer.writerow([p.id_pago, p.id_prestamo, p.monto, p.fecha])

    def cargar_datos(self):
        # Cargar clientes
        if os.path.exists('clientes.csv'):
            with open('clientes.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.clientes.append(Cliente(
                        int(row['id']),
                        row['nombre'],
                        row['identificacion'],
                        row['contacto']
                    ))

        # Cargar préstamos
        if os.path.exists('prestamos.csv'):
            with open('prestamos.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.prestamos.append(Prestamo(
                        int(row['id']),
                        int(row['id_cliente']),
                        float(row['monto']),
                        float(row['tasa']),
                        int(row['plazo']),
                        row['estado']
                    ))
                    self.prestamos[-1].saldo = float(row['saldo'])

        # Cargar pagos
        if os.path.exists('pagos.csv'):
            with open('pagos.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.pagos.append(Pago(
                        int(row['id']),
                        int(row['id_prestamo']),
                        float(row['monto']),
                        row['fecha']
                    ))

# Interfaz de usuario
def main():
    financiera = Financiera()
    
    while True:
        print("\n--- SISTEMA FINANCIERO ---")
        print("1. Registrar cliente")
        print("2. Registrar préstamo")
        print("3. Registrar pago")
        print("4. Calcular cuota")
        print("5. Generar reportes")
        print("6. Salir")
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == "1":
            nombre = input("Nombre: ")
            identificacion = input("Identificación: ")
            contacto = input("Contacto: ")
            cliente = financiera.registrar_cliente(nombre, identificacion, contacto)
            print(f"Cliente registrado ID: {cliente.id_cliente}")
        
        elif opcion == "2":
            id_cliente = int(input("ID Cliente: "))
            monto = float(input("Monto: "))
            tasa = float(input("Tasa anual (%): "))
            plazo = int(input("Plazo (meses): "))
            prestamo = financiera.registrar_prestamo(id_cliente, monto, tasa, plazo)
            if isinstance(prestamo, str):
                print(prestamo)
            else:
                cuota = financiera.calcular_cuota(prestamo.id_prestamo)
                print(f"Préstamo ID: {prestamo.id_prestamo} | Cuota estimada: ${cuota}")
        
        elif opcion == "3":
            id_prestamo = int(input("ID Préstamo: "))
            monto = float(input("Monto a pagar: "))
            resultado = financiera.registrar_pago(id_prestamo, monto)
            if isinstance(resultado, str):
                print(resultado)
            else:
                print(f"Pago registrado ID: {resultado.id_pago}")
        
        elif opcion == "4":
            id_prestamo = int(input("ID Préstamo: "))
            cuota = financiera.calcular_cuota(id_prestamo)
            if isinstance(cuota, str):
                print(cuota)
            else:
                print(f"Cuota mensual: ${cuota}")
        
        elif opcion == "5":
            print("\n--- REPORTES ---")
            print("1. Lista de clientes")
            print("2. Préstamos activos")
            print("3. Morosos")
            print("4. Historial de pagos")
            sub_op = input("Seleccione reporte: ")
            
            if sub_op == "1":
                for c in financiera.generar_reporte("clientes"):
                    print(f"ID: {c.id_cliente} | {c.nombre} | {c.identificacion}")
            
            elif sub_op == "2":
                for p in financiera.generar_reporte("prestamos"):
                    print(f"Préstamo ID: {p.id_prestamo} | Saldo: ${p.saldo} | Estado: {p.estado}")
            
            elif sub_op == "3":
                for p in financiera.generar_reporte("morosos"):
                    print(f"Préstamo ID: {p.id_prestamo} | Saldo pendiente: ${p.saldo}")
            
            elif sub_op == "4":
                for pago in financiera.generar_reporte("pagos"):
                    print(f"Pago ID: {pago.id_pago} | Monto: ${pago.monto} | Fecha: {pago.fecha}")
        
        elif opcion == "6":
            financiera.guardar_clientes()
            financiera.guardar_prestamos()
            financiera.guardar_pagos()
            print("¡Datos guardados! Hasta luego.")
            break

if __name__ == "__main__":
    main()