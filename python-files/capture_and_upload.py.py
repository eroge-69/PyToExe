import cv2
import dropbox

# Configuración de Dropbox
ACCESS_TOKEN = 'sl.u.AF2LPavuN47vCmnln47AEoh6MUhkOGjkGJa5ZZamPV0FI5fzSvp98lkTtapkPJDV_vmDBg0ZRWIlePKrJS3G_JwpajPV3eEOF2NJpz8wUgj7kXg4iAlJ6ciWiAl3s3ZIqa_e7Nq9yHWKBULAlTfUsDEjdDHFuJTCvRM78iQefulBA0nyRF5tzFJJgAukhtiUGMz2YCvBgXUnWECxEKrbE3m9iMkGekM6na5pl40YHzxb8Evn3u4RbVxZr112AUxz8JTrFCoIxyoyonLCtEeqp47Of75VnrTaINK0Z1vEtoxlAlQuE4qioeraE0blKq8j-5pL6GKC-iR8CCazLTdcjwga74zYv0TgmNc-gyrGiuP1pOC8otCCCxPEk_0olIwDDEz0z48P7FdWyJZM-68oppwLDIZfJGtnEHdOntOhDcV8lz3cb4P8uEeNE3MF04vNrdwzTJMCKXD97E2qmcg17b8OMFjgZaaL2Lr2XlQuvbMy3YD2hIcA1tZlOQsl8N5-UDmt_967xoOE2a_wMymMjqcwFh_x7m1EFqfZ84b3j4WcG8X9sfWLL2hoTEqP44WWfH1tQmmyrxUGZLi93HEpzShN_YDKwI-WVjA4MD0_lnHqTflOuAiSg0JNXV3gYNtLmmT9tAZuwgagPkMbR4e9BAItJhe_aT3ujW0DQiGMCzs9R8eY2E-4t6dlv8z3sKkC_tT2tW-MoK35yoJV6ieFsmF7M8i4KcjmmHskwxa-fBRLSmhMTy-rgB4A2SxTdT37AIVtxFiCJAPRmdzJ8LogPGy8vmiwCxI5aHbRAUqfAuWFXqPNF0LXFe8ZJRDuxbJVbnygf7QRu7FApGHSoxZcmIwCjE_7GyYGcLQ8t6j8hWbLfb7gFvCpTdZFBCw7oCNuIaUjLr9frtFA_aZMHvRLtCmpEbwgi_4Ymd1Zv6mnSdmaIi9iDZKH-UcZeRYUuU_m5ZTUHu994guTvni4_QM1r8Wl4xbh3S0Yn00Bx52nhfs2WXr1SVfqJL-GFsXsPiE26qDW9LZKIy31d-weKrYnvIDv3QvBEypz6-VUIuFwvLmTbOoAW-oE7YRiYDJS1vc_8Y6uojuF6b2FdJMjv_lH5WXvnp0xaq_yEjmycnnUrI6Qr4js-aMyN7gD_Hz0zz8u9Ln4l_DnIXTJGXvDI29AUGfdAofxWNnserdRrWGCgHB0kBSzuRQCRH3PIXQ9wE02gccLkALWNXI6k1oGDXroIoznEa9GA1FsoBxA43e50WGQRoFSgPTk6IhwmfmXdwfrEKScNaIsSn2MqoH4CIo4sQdOWijLalvXDRNITR6qsV-rwZe6c0cBmhus32de2pSHtQqTDEXlQNa9qvpzZ4LqyCb-cNUvDqGguvMQjTmYXMykKxlRkbMxzr-_3UKgHxXHCIJw2WAkvEn8Cm7RzFnoF8fmAbH7b1Bw_EQCMUw5s3rBhA'
dbx = dropbox.Dropbox(ACCESS_TOKEN)

# Capturar una imagen desde la cámara web
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: No se pudo abrir la cámara.")
    exit()

ret, frame = cap.read()
if not ret:
    print("Error: No se pudo capturar la imagen.")
    cap.release()
    exit()

# Guardar la imagen temporalmente
image_path = "captured_image.jpg"
cv2.imwrite(image_path, frame)
cap.release()

# Subir la imagen a Dropbox
with open(image_path, 'rb') as f:
    dbx.files_upload(f.read(), '/captured_image.jpg', mode=dropbox.files.WriteMode('overwrite'))

print("Imagen capturada y subida a Dropbox exitosamente.")