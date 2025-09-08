import streamlit as st
import random

# Datos históricos
frecuentes = [2, 21, 24, 34, 43]
calientes_2025 = [2, 17, 34, 41, 43, 33, 5]
fríos_2025 = [6, 11, 15, 20, 23, 30]

def generar_combinacion(filtro):
    seleccionados = set()

    # Filtro: solo pares
    if filtro == "Solo pares":
        pares = [n for n in calientes_2025 + frecuentes if n % 2 == 0]
        seleccionados.update(random.sample(pares, 5))
    # Filtro: decenas altas (30 a 43)
    elif filtro == "Decenas altas":
        altos = [n for n in calientes_2025 + frecuentes if 30 <= n <= 43]
        seleccionados.update(random.sample(altos, 5))
    # Filtro: sin repetidos
    else:
        seleccionados.update(random.sample(calientes_2025, 3))
        restantes = list(set(frecuentes) - seleccionados)
        seleccionados.update(random.sample(restantes, 2))

    # Añadir número frío
    seleccionados.add(random.choice(fríos_2025))

    # Superbalota
    superbalota = random.randint(1, 16)
    return sorted(list(seleccionados)), superbalota

# Interfaz visual
st.title("🎯 Generador Inteligente de Baloto")
num_combos = st.slider("¿Cuántas combinaciones quieres?", 1, 10, 3)
filtro = st.selectbox("Elige un filtro:", ["Normal", "Solo pares", "Decenas altas"])

for _ in range(num_combos):
    combo, sb = generar_combinacion(filtro)
    st.write(f"Combinación: {combo} | Superbalota: {sb}")
