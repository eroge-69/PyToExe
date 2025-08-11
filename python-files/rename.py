import os
from docx import Document

def extract_info(doc_path):
    try:
        doc = Document(doc_path)
        fam = None

        # Поиск фамилии в тексте документа
        for para in doc.paragraphs:
            text = para.text.strip()
            if text and len(text.split()) == 2:  # Допустим, фамилия + инициалы
                fam = text.split()[0]
                break

        return fam
    except Exception as e:
        print(f"[Ошибка чтения] {doc_path}: {e}")
        return None

def main():
    folder = input("Папка с документами (.docx): ").strip()
    date_str = input("Дата (в формате ДД.ММ.ГГГГ): ").strip()
    doc_num = input("Номер документа: ").strip()

    for file in os.listdir(folder):
        if file.lower().endswith(".docx"):
            path = os.path.join(folder, file)
            fam = extract_info(path)

            if fam:
                new_name = f"{doc_num}_{fam}_{date_str}.docx"
                new_path = os.path.join(folder, new_name)
                os.rename(path, new_path)
                print(f"✅ {file} → {new_name}")
            else:
                print(f"⚠ Фамилия не найдена в {file}")

if __name__ == "__main__":
    main()
