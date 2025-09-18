import time
import os

# Ask for content and filename
user_text = input("Agregar la información copiada y presionar Enter: ")
base_filename = input("Escanear etiqueta: ")

# Generate MMYY timestamp
timestamp = time.strftime("%m%y")
file_name = f"{timestamp}_{base_filename}.txt"

# Define where to save
save_dir = os.path.expanduser("C:\\Users\\MXETTECH\\Desktop\\bluetooth")
os.makedirs(save_dir, exist_ok=True)

# Full file path
file_path = os.path.join(save_dir, file_name)

# Write content to file
with open(file_path, "w", encoding="utf-8") as file:
    file.write(user_text)

print(f"Información guardada en: {file_path}")
time.sleep(5)
