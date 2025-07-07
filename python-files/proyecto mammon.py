import tkinter as tk
from tkinter import ttk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from keras.models import Sequential, load_model
from keras.layers import LSTM, Dense, Dropout
import requests
from imblearn.over_sampling import SMOTE
import schedule
import time
from apscheduler.schedulers.blocking import BlockingScheduler
import pickle
import pandas as pd

# Parámetros de análisis
TIEMPO_ADELANTADO = 1  # hora
CRIPTOMONEDAS = ['Bitcoin', 'Ethereum', 'Monero']
API_KEYS = {
    'CoinGecko': 'TU_API_KEY_COINGECKO',
    'Coinbase API': 'TU_API_KEY_COINBASE',
    'CryptoCompare': 'TU_API_KEY_CRYPTOCOMPARE'
}

# Función para obtener datos de la API
def obtener_datos(cryptomoneda):
    datos = []
    for api, api_key in API_KEYS.items():
        if api == 'CoinGecko':
            url = f"https://api.coingecko.com/api/v3/coins/{cryptomoneda}/market_chart?vs_currency=usd&days=30"
            respuesta = requests.get(url)
            datos_api = respuesta.json()
            datos.append(datos_api)
        elif api == 'Coinbase API':
            url = f"https://api.coinbase.com/v2/prices/{cryptomoneda}-USD/spot"
            respuesta = requests.get(url)
            datos_api = respuesta.json()
            datos.append(datos_api)
        elif api == 'CryptoCompare':
            url = f"https://min-api.cryptocompare.com/data/price?fsym={cryptomoneda}&tsyms=USD"
            respuesta = requests.get(url)
            datos_api = respuesta.json()
            datos.append(datos_api)
    return datos

# Función para preprocesar datos
def preprocesar_datos(datos):
    scaler = MinMaxScaler()
    datos_normalizados = scaler.fit_transform(datos)
    return datos_normalizados

# Función para entrenar modelo
def entrenar_modelo(datos_normalizados):
    try:
        # Cargar el modelo entrenado anteriormente
        modelo = load_model('modelo_entrenado.h5')
        print("Modelo cargado correctamente")
    except FileNotFoundError:
        # Crear un nuevo modelo si no hay uno entrenado anteriormente
        modelo = Sequential()
        modelo.add(LSTM(units=50, return_sequences=True, input_shape=(datos_normalizados.shape[1], 1)))
        modelo.add(Dropout(0.2))
        modelo.add(LSTM(units=50))
        modelo.add(Dropout(0.2))
        modelo.add(Dense(units=1))
        modelo.compile(optimizer='adam', loss='mean_squared_error')
        # Entrenar el modelo con los nuevos datos
        X_train, X_test, y_train, y_test = train_test_split(datos_normalizados[:, :-1], datos_normalizados[:, -1], test_size=0.2, random_state=42)
        smote = SMOTE(random_state=42)
        X_train_res, y_train_res = smote.fit_resample(X_train, y_train)
        modelo.fit(X_train_res, y_train_res, epochs=100, batch_size=32, verbose=2)
        # Guardar el modelo entrenado
        modelo.save('modelo_entrenado.h5')
    return modelo

# Función para realizar predicciones
def realizar_predicciones(modelo, datos_normalizados):
    predicciones = modelo.predict(datos_normalizados)
    return predicciones

# Función para evaluar predicciones
def evaluar_predicciones(predicciones, datos_normalizados):
    accuracy = accuracy_score(datos_normalizados[:, -1], predicciones)
    return accuracy

# Función para determinar cuándo vender
def determinar_venta(predicciones, datos_normalizados, umbral_beneficio):
    venta = []
    for i in range(len(predicciones)):
        if predicciones[i] > datos_normalizados[i, -1] * (1 + umbral_beneficio):
            venta.append((i, predicciones[i], datos_normalizados[i, -1]))
    return venta

# Función para mostrar resultados
def mostrar_resultados(venta, cryptomoneda, hora_actual):
    print(f"Resultados para {cryptomoneda} a las {hora_actual}:")
    print("Hora\tPrecio de venta\tPrecio actual")
    for v in venta:
        print(f"{v[0]}\t{v[1]}\t{v[2]}")

# Función para actualizar datos y entrenar modelo
def actualizar_datos_y_entrenar_modelo():
    for cryptomoneda in CRIPTOMONEDAS:
        datos = obtener_datos(cryptomoneda)
        datos_normalizados = preprocesar_datos(datos)
        modelo = entrenar_modelo(datos_normalizados)
        predicciones = realizar_predicciones(modelo, datos_normalizados)
        accuracy = evaluar_predicciones(predicciones, datos_normalizados)
        print(f"Criptomoneda: {cryptomoneda}, Accuracy: {accuracy}")
        umbral_beneficio = 0.1  # 10% de beneficio
        venta = determinar_venta(predicciones, datos_normalizados, umbral_beneficio)
        hora_actual = time.strftime("%H:%M:%S")
        mostrar_resultados(venta, cryptomoneda, hora_actual)

# Programar la actualización de datos y entrenamiento del modelo cada hora
scheduler = BlockingScheduler()
scheduler.add_job(actualizar_datos_y_entrenar_modelo, 'interval', hours=1)
scheduler.start()

# Crear una ventana de Tkinter para mostrar los resultados
ventana = tk.Tk()
ventana.title("Análisis de Criptomonedas")

# Crear un frame para mostrar los resultados
frame_resultados = tk.Frame(ventana)
frame_resultados.pack()

# Crear un texto para mostrar los resultados
texto_resultados = tk.Text(frame_resultados)
texto_resultados.pack()

# Actualizar los resultados en la ventana cada hora
def actualizar_resultados():
    texto_resultados.delete(1.0, tk.END)
    for cryptomoneda in CRIPTOMONEDAS:
        datos = obtener_datos(cryptomoneda)
        datos_normalizados = preprocesar_datos(datos)
        modelo = entrenar_modelo(datos_normalizados)
        predicciones = realizar_predicciones(modelo, datos_normalizados)
        accuracy = evaluar_predicciones(predicciones, datos_normalizados)
        texto_resultados.insert(tk.END, f"Criptomoneda: {cryptomoneda}, Accuracy: {accuracy}\n")
        umbral_beneficio = 0.1  # 10% de beneficio
        venta = determinar_venta(predicciones, datos_normalizados, umbral_beneficio)
        hora_actual = time.strftime("%H:%M:%S")
        texto_resultados.insert(tk.END, f"Resultados para {cryptomoneda} a las {hora_actual}:\n")
        texto_resultados.insert(tk.END, "Hora\tPrecio de venta\tPrecio actual\n")
        for v in venta:
            texto_resultados.insert(tk.END, f"{v[0]}\t{v[1]}\t{v[2]}\n")
    ventana.after(3600000, actualizar_resultados)  # Actualizar cada hora

actualizar_resultados()

ventana.mainloop()

# Crear un frame para mostrar los resultados
frame_resultados = tk.Frame(ventana)
frame_resultados.pack()

# Crear un texto para mostrar los resultados
texto_resultados = tk.Text(frame_resultados)
texto_resultados.pack()

# Actualizar los resultados en la ventana cada hora
def actualizar_resultados():
    texto_resultados.delete(1.0, tk.END)
    for cryptomoneda in CRIPTOMONEDAS:
        datos = obtener_datos(cryptomoneda)
        datos_normalizados = preprocesar_datos(datos)
        modelo = entrenar_modelo(datos_normalizados)
        predicciones = realizar_predicciones(modelo, datos_normalizados)
        accuracy = evaluar_predicciones(predicciones, datos_normalizados)
        texto_resultados.insert(tk.END, f"Criptomoneda: {cryptomoneda}, Accuracy: {accuracy}\n")
        umbral_beneficio = 0.1  # 10% de beneficio
        venta = determinar_venta(predicciones, datos_normalizados, umbral_beneficio)
        hora_actual = time.strftime("%H:%M:%S")
        texto_resultados.insert(tk.END, f"Resultados para {cryptomoneda} a las {hora_actual}:\n")
        texto_resultados.insert(tk.END, "Hora\tPrecio de venta\tPrecio actual\n")
        for v in venta:
            texto_resultados.insert(tk.END, f"{v[0]}\t{v[1]}\t{v[2]}\n")
    ventana.after(3600000, actualizar_resultados)  # Actualizar cada hora

actualizar_resultados()

ventana.mainloop()

ventana.mainloop()

# Función para cerrar la ventana y detener el scheduler
def cerrar_ventana():
    scheduler.shutdown()
    ventana.destroy()

# Agregar un botón para cerrar la ventana
boton_cerrar = tk.Button(ventana, text="Cerrar", command=cerrar_ventana)
boton_cerrar.pack()

# Función para guardar los resultados en un archivo
def guardar_resultados():
    with open("resultados.txt", "w") as archivo:
        for cryptomoneda in CRIPTOMONEDAS:
            datos = obtener_datos(cryptomoneda)
            datos_normalizados = preprocesar_datos(datos)
            modelo = entrenar_modelo(datos_normalizados)
            predicciones = realizar_predicciones(modelo, datos_normalizados)
            accuracy = evaluar_predicciones(predicciones, datos_normalizados)
            archivo.write(f"Criptomoneda: {cryptomoneda}, Accuracy: {accuracy}\n")
            umbral_beneficio = 0.1  # 10% de beneficio
            venta = determinar_venta(predicciones, datos_normalizados, umbral_beneficio)
            hora_actual = time.strftime("%H:%M:%S")
            archivo.write(f"Resultados para {cryptomoneda} a las {hora_actual}:\n")
            archivo.write("Hora\tPrecio de venta\tPrecio actual\n")
            for v in venta:
                archivo.write(f"{v[0]}\t{v[1]}\t{v[2]}\n")

# Agregar un botón para guardar los resultados
boton_guardar = tk.Button(ventana, text="Guardar resultados", command=guardar_resultados)
boton_guardar.pack()
# ...

# Función para mostrar los resultados en una gráfica
def mostrar_gráfica():
    for cryptomoneda in CRIPTOMONEDAS:
        datos = obtener_datos(cryptomoneda)
        datos_normalizados = preprocesar_datos(datos)
        modelo = entrenar_modelo(datos_normalizados)
        predicciones = realizar_predicciones(modelo, datos_normalizados)
        plt.plot(predicciones)
        plt.title(f"Predicciones para {cryptomoneda}")
        plt.xlabel("Hora")
        plt.ylabel("Precio")
        plt.show()

# Agregar un botón para mostrar los resultados en una gráfica
boton_gráfica = tk.Button(ventana, text="Mostrar gráfica", command=mostrar_gráfica)
boton_gráfica.pack()

# Función para enviar un correo electrónico con los resultados
def enviar_correo():
    for cryptomoneda in CRIPTOMONEDAS:
        datos = obtener_datos(cryptomoneda)
        datos_normalizados = preprocesar_datos(datos)
        modelo = entrenar_modelo(datos_normalizados)
        predicciones = realizar_predicciones(modelo, datos_normalizados)
        accuracy = evaluar_predicciones(predicciones, datos_normalizados)
        umbral_beneficio = 0.1  # 10% de beneficio
        venta = determinar_venta(predicciones, datos_normalizados, umbral_beneficio)
        hora_actual = time.strftime("%H:%M:%S")
        mensaje = f"Resultados para {cryptomoneda} a las {hora_actual}:\n"
        mensaje += "Hora\tPrecio de venta\tPrecio actual\n"
        for v in venta:
            mensaje += f"{v[0]}\t{v[1]}\t{v[2]}\n"
        # Enviar el correo electrónico
        import smtplib
        from email.mime.text import MIMEText
        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login("tu_correo@gmail.com", "tu_contraseña")
        mensaje_email = MIMEText(mensaje)
        mensaje_email["Subject"] = f"Resultados para {cryptomoneda}"
        mensaje_email["From"] = "tu_correo@gmail.com"
        mensaje_email["To"] = "destinatario@example.com"
        servidor.sendmail("tu_correo@gmail.com", "destinatario@example.com", mensaje_email.as_string())
        servidor.quit()

# Agregar un botón para enviar un correo electrónico con los resultados
boton_correo = tk.Button(ventana, text="Enviar correo", command=enviar_correo)
boton_correo.pack()