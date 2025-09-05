import os
import pdfplumber

# 📂 Папка, где лежат твои PDF
INPUT_FOLDER = "pdfs"
# 📄 Файл для результата
OUTPUT_FILE = "1-108.txt"

with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
    # перебор всех PDF в папке
    for filename in os.listdir(INPUT_FOLDER):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(INPUT_FOLDER, filename)

            with pdfplumber.open(file_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

            # ищем кусок от Beneficiary до To Date of Service
            start = text.find("Beneficiary:")
            end = text.find("To Date of Service:")
            if start != -1 and end != -1:
                block = text[start:end].strip()
                block += "\nTo Date of Service:"  # добавляем финальную строку

                # правим Provider/Supplier и NPI
                lines = block.splitlines()
                new_lines = []
                for line in lines:
                    if line.startswith("Provider/Supplier:"):
                        new_lines.append("Provider/Supplier: ")
                    elif line.startswith("NPI:"):
                        new_lines.append("NPI: ")
                    else:
                        new_lines.append(line)

                # записываем в итоговый файл
                out.write("\n".join(new_lines) + "\n\n")

print(f"✅ Готово! Данные собраны в файл: {OUTPUT_FILE}")
