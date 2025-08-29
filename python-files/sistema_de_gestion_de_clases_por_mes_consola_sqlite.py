#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de gestión de clases por mes
- Registro de maestros
- Registro de clases (fecha, horario, materia, maestro)
- Consultas por mes y por maestro
- Reporte mensual por maestro
- Exportación a CSV

Base de datos: SQLite (archivo gestion_clases.db)
Ejecución: python gestion_clases.py
"""

import sqlite3
import os
import csv
from datetime import datetime
from typing import Optional, List, Tuple

DB_PATH = "gestion_clases.db"

# ------------------------------
# Inicialización de la base de datos
# ------------------------------

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS maestros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS clases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,        -- formato ISO: YYYY-MM-DD
                horario TEXT NOT NULL,      -- p.ej. "8:30 a.m. - 10:00 a.m."
                materia TEXT NOT NULL,
                maestro_id INTEGER NOT NULL,
                notas TEXT,
                FOREIGN KEY(maestro_id) REFERENCES maestros(id)
            )
            """
        )
        conn.commit()

# ------------------------------
# Utilidades
# ------------------------------

def input_no_vacio(prompt: str) -> str:
    while True:
        s = input(prompt).strip()
        if s:
            return s
        print("⚠️  Este campo no puede estar vacío.")


def input_fecha_iso(prompt: str) -> str:
    """Pide una fecha y la valida en formato YYYY-MM-DD."""
    while True:
        s = input(prompt + " (YYYY-MM-DD): ").strip()
        try:
            datetime.strptime(s, "%Y-%m-%d")
            return s
        except ValueError:
            print("⚠️  Fecha inválida. Usa el formato YYYY-MM-DD, por ejemplo 2025-08-15.")


def input_mes_anio() -> Tuple[int, int]:
    while True:
        mes_str = input("Mes (1-12): ").strip()
        anio_str = input("Año (e.g., 2025): ").strip()
        try:
            mes = int(mes_str)
            anio = int(anio_str)
            if 1 <= mes <= 12:
                return mes, anio
            print("⚠️  El mes debe estar entre 1 y 12.")
        except ValueError:
            print("⚠️  Ingresa números válidos para mes y año.")

# ------------------------------
# Operaciones con maestros
# ------------------------------

def agregar_maestro(nombre: str) -> int:
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO maestros (nombre) VALUES (?)", (nombre,))
        conn.commit()
        # Obtener id
        c.execute("SELECT id FROM maestros WHERE nombre = ?", (nombre,))
        row = c.fetchone()
        return row[0]


def listar_maestros() -> List[Tuple[int, str]]:
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT id, nombre FROM maestros ORDER BY nombre ASC")
        return c.fetchall()


def seleccionar_maestro_interactivo() -> Optional[int]:
    maestros = listar_maestros()
    if not maestros:
        print("No hay maestros registrados. Agrega uno primero.")
        return None
    print("\nMaestros:")
    for mid, nom in maestros:
        print(f"  {mid}. {nom}")
    while True:
        try:
            mid = int(input("ID del maestro: ").strip())
            if any(m[0] == mid for m in maestros):
                return mid
            print("⚠️  ID no válido.")
        except ValueError:
            print("⚠️  Ingresa un número válido.")

# ------------------------------
# Operaciones con clases
# ------------------------------

def agregar_clase(fecha: str, horario: str, materia: str, maestro_id: int, notas: Optional[str] = None) -> int:
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO clases (fecha, horario, materia, maestro_id, notas)
            VALUES (?,?,?,?,?)
            """,
            (fecha, horario, materia, maestro_id, notas),
        )
        conn.commit()
        return c.lastrowid


def clases_por_mes(mes: int, anio: int, maestro_id: Optional[int] = None) -> List[Tuple]:
    mes_str = f"{mes:02d}"
    anio_str = str(anio)
    with get_conn() as conn:
        c = conn.cursor()
        base = (
            "SELECT c.id, c.fecha, c.horario, c.materia, m.nombre, IFNULL(c.notas, '') "
            "FROM clases c JOIN maestros m ON c.maestro_id = m.id "
            "WHERE strftime('%m', c.fecha) = ? AND strftime('%Y', c.fecha) = ?"
        )
        params = [mes_str, anio_str]
        if maestro_id:
            base += " AND m.id = ?"
            params.append(maestro_id)
        base += " ORDER BY c.fecha ASC, c.horario ASC"
        c.execute(base, params)
        return c.fetchall()


def resumen_mensual(mes: int, anio: int) -> List[Tuple[str, int]]:
    mes_str = f"{mes:02d}"
    anio_str = str(anio)
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(
            """
            SELECT m.nombre, COUNT(c.id) AS total_clases
            FROM clases c
            JOIN maestros m ON c.maestro_id = m.id
            WHERE strftime('%m', c.fecha) = ? AND strftime('%Y', c.fecha) = ?
            GROUP BY m.nombre
            ORDER BY m.nombre ASC
            """,
            (mes_str, anio_str),
        )
        return c.fetchall()


def exportar_csv(mes: int, anio: int, ruta_csv: str, maestro_id: Optional[int] = None) -> int:
    filas = clases_por_mes(mes, anio, maestro_id)
    with open(ruta_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Fecha", "Horario", "Materia", "Maestro", "Notas"])
        writer.writerows(filas)
    return len(filas)

# ------------------------------
# Interfaz de consola (menú)
# ------------------------------

def menu():
    print("\n===== Sistema de Gestión de Clases =====")
    print("1) Agregar maestro")
    print("2) Listar maestros")
    print("3) Agregar clase")
    print("4) Consultar clases por mes")
    print("5) Consultar clases por mes y maestro")
    print("6) Resumen mensual (clases por maestro)")
    print("7) Exportar a CSV")
    print("0) Salir")


def accion_agregar_maestro():
    nombre = input_no_vacio("Nombre del maestro: ")
    mid = agregar_maestro(nombre)
    print(f"✅ Maestro registrado con ID {mid}.")


def accion_listar_maestros():
    datos = listar_maestros()
    if not datos:
        print("(Sin maestros aún)")
        return
    print("\nID  | Nombre")
    print("----+-------------------------------")
    for mid, nom in datos:
        print(f"{mid:<3} | {nom}")


def accion_agregar_clase():
    if not listar_maestros():
        print("⚠️  Primero debes registrar al menos un maestro.")
        return
    fecha = input_fecha_iso("Fecha de la clase")
    horario = input_no_vacio("Horario (ej. 8:30 a.m. - 10:00 a.m.): ")
    materia = input_no_vacio("Materia: ")
    mid = seleccionar_maestro_interactivo()
    if mid is None:
        return
    notas = input("Notas (opcional): ").strip() or None
    cid = agregar_clase(fecha, horario, materia, mid, notas)
    print(f"✅ Clase registrada con ID {cid}.")


def imprimir_tabla_clases(filas: List[Tuple]):
    if not filas:
        print("(No hay clases registradas en ese periodo)")
        return
    print("\nID  | Fecha       | Horario                 | Materia         | Maestro           | Notas")
    print("----+-------------+-------------------------+-----------------+-------------------+--------------------")
    for cid, fecha, horario, materia, maestro, notas in filas:
        print(f"{cid:<3} | {fecha:<11} | {horario:<23} | {materia:<15} | {maestro:<17} | {notas or ''}")


def accion_consultar_por_mes(maestro_filtrado: bool = False):
    mes, anio = input_mes_anio()
    maestro_id = None
    if maestro_filtrado:
        maestro_id = seleccionar_maestro_interactivo()
        if maestro_id is None:
            return
    filas = clases_por_mes(mes, anio, maestro_id)
    imprimir_tabla_clases(filas)


def accion_resumen_mensual():
    mes, anio = input_mes_anio()
    resumen = resumen_mensual(mes, anio)
    if not resumen:
        print("(No hay clases registradas en ese periodo)")
        return
    print("\nMaestro                 | Total clases")
    print("------------------------+--------------")
    for nombre, total in resumen:
        print(f"{nombre:<24} | {total}")


def accion_exportar_csv():
    mes, anio = input_mes_anio()
    filtrar = input("¿Filtrar por maestro? (s/n): ").strip().lower() == 's'
    maestro_id = None
    sufijo = ""
    if filtrar:
        maestro_id = seleccionar_maestro_interactivo()
        if maestro_id is None:
            return
        sufijo = f"_maestro{maestro_id}"
    nombre = f"reporte_{anio}_{mes:02d}{sufijo}.csv"
    ruta = input(f"Ruta del archivo CSV (Enter para '{nombre}'): ").strip() or nombre
    total = exportar_csv(mes, anio, ruta, maestro_id)
    print(f"✅ Exportado {total} registro(s) a '{ruta}'.")


def main():
    init_db()
    print("Base de datos lista en:", os.path.abspath(DB_PATH))
    while True:
        menu()
        opcion = input("Selecciona una opción: ").strip()
        if opcion == '1':
            accion_agregar_maestro()
        elif opcion == '2':
            accion_listar_maestros()
        elif opcion == '3':
            accion_agregar_clase()
        elif opcion == '4':
            accion_consultar_por_mes(False)
        elif opcion == '5':
            accion_consultar_por_mes(True)
        elif opcion == '6':
            accion_resumen_mensual()
        elif opcion == '7':
            accion_exportar_csv()
        elif opcion == '0':
            print("¡Hasta luego!")
            break
        else:
            print("⚠️  Opción no válida. Intenta de nuevo.")


if __name__ == "__main__":
    main()
