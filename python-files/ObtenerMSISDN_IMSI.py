# script_txt_to_oneline.py

input_file = "entrada.txt"
output_file = "salida.txt"

with open(input_file, "r", encoding="utf-8") as txt_file:
    # Leemos todas las líneas y eliminamos saltos de línea
    numbers = [line.strip() for line in txt_file if line.strip()]

# Unimos todo en una sola línea separado por ","
result = ",".join(numbers)

# Guardamos en salida.txt
with open(output_file, "w", encoding="utf-8") as out_file:
    out_file.write(result)

print(f"Archivo generado: {output_file}")
