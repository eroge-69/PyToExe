import os
import re

def get_vehicle_names_from_stream(folder_path):
    vehicles = set()
    for root, dirs, files in os.walk(folder_path):  # tüm alt klasörleri tara
        for file in files:
            if file.endswith(".yft"):
                model_name = os.path.splitext(file)[0]

                # "_" veya "+" içeren dosyaları atla (ör: lod, hi, bumper, chassis)
                if "_" in model_name or "+" in model_name:
                    continue

                # "hi" veya "lod" gibi dosya varyasyonlarını atla
                if re.search(r"(lod|hi)$", model_name, re.IGNORECASE):
                    continue

                vehicles.add(model_name)
    return sorted(list(vehicles))

def generate_vehicle_entry(model_name):
    return f"""['{model_name}'] = {{
    ['name'] = '{model_name}',
    ['brand'] = '{model_name}',
    ['model'] = '{model_name}',
    ['price'] = 10000,
    ['category'] = 'viodonate',
    ['hash'] = `{model_name}`,
    ['shop'] = 'donate',
}},"""

def convert_stream_folder(folder_path):
    vehicle_names = get_vehicle_names_from_stream(folder_path)
    if not vehicle_names:
        print("Hiç uygun .yft dosyası bulunamadı.")
        return

    output_path = os.path.join(folder_path, "formatted_vehicles.lua")
    with open(output_path, "w", encoding="utf-8") as file:
        file.write("return {\n")
        for model in vehicle_names:
            file.write(generate_vehicle_entry(model) + "\n")
        file.write("}\n")

    print(f"{len(vehicle_names)} araç başarıyla bulundu ve dönüştürüldü!")
    print(f"Oluşturulan dosya: {output_path}")

if __name__ == "__main__":
    current_folder = os.getcwd()
    convert_stream_folder(current_folder)
    input("\nDevam etmek için Enter'a bas...")
