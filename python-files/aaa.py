#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Programa educativo para recuperación de contraseñas BIOS mediante contraseñas maestras.
Uso exclusivo en equipos propios y con fines legales.
Autor: ChatGPT (OpenAI) - 2025
"""

import sys
import os

# Diccionario con marcas y contraseñas maestras conocidas (solo BIOS antiguos)
MASTER_PASSWORDS = {
    "Dell": [
        "Dell", "BIOS", "setup", "dell", "Dell123", "DellMaster",
        "589589", "589721", "595B", "2A7B", "D35B", "FF6A"
    ],
    "HP/Compaq": [
        "HP", "compaq", "CMOS", "BIOS", "HP123", "hewwpack",
        "hpq-tap", "hpbios", "phoenix"
    ],
    "Acer": [
        "Acer", "PHOENIX", "bios", "ACER123", "CMOSPWD",
        "ZAAADA", "J262", "ZJAAADC"
    ],
    "Toshiba": [
        "Toshiba", "TOSHIBA", "Toshiba123", "ToshibaBIOS",
        "ToshibaMaster", "TOSH123", "ToshibaBIOSPassword"
    ],
    "Sony": [
        "Sony", "VAIO", "sonybios", "sony123", "Phoenix",
        "PHX", "SONY", "biossony"
    ],
    "Lenovo": [
        "Lenovo", "lenovo123", "LNV", "lenovobios", "Thinkpad",
        "LenovoMaster", "lenovopass"
    ],
    "Asus": [
        "Asus", "ASUS", "asus123", "BIOS", "Phoenix",
        "CMOSPWD", "admin"
    ],
    "Otros": [
        "AMI", "AWARD_SW", "AWARD_SW", "BIOS", "PASSWORD",
        "phoenix", "biosstar", "setup", "cmos", "cmosPWD"
    ]
}

def limpiar_pantalla():
    os.system("cls" if os.name == "nt" else "clear")

def mostrar_banner():
    print("=" * 50)
    print(" 🔐  BIOS Password Recovery (Educativo) ")
    print("=" * 50)
    print("⚠️  Uso exclusivo en equipos propios.\n")

def mostrar_menu():
    print("Selecciona una marca de BIOS para ver posibles contraseñas:")
    for i, marca in enumerate(MASTER_PASSWORDS.keys(), 1):
        print(f" {i}. {marca}")
    print(" 0. Salir")

def mostrar_contrasenas(marca):
    limpiar_pantalla()
    mostrar_banner()
    print(f"Marca seleccionada: {marca}")
    print("-" * 50)
    for pwd in MASTER_PASSWORDS[marca]:
        print(f" ➤ {pwd}")
    print("-" * 50)
    input("\nPresiona ENTER para volver al menú...")

def main():
    while True:
        limpiar_pantalla()
        mostrar_banner()
        mostrar_menu()

        try:
            opcion = int(input("\nOpción: "))
        except ValueError:
            continue

        if opcion == 0:
            print("\nSaliendo... ¡Úsalo con responsabilidad!")
            sys.exit()

        marcas = list(MASTER_PASSWORDS.keys())
        if 1 <= opcion <= len(marcas):
            mostrar_contrasenas(marcas[opcion - 1])
        else:
            continue

if __name__ == "__main__":
    main()
