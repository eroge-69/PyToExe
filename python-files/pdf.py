import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForVision2Seq
from PyPDF2 import PdfReader
from pdf2image import convert_from_path

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
POPPLER_PATH = r"C:\poppler\poppler-24.08.0\Library\bin"  # <- ustaw swoją ścieżkę do popplera

processor = AutoProcessor.from_pretrained("HuggingFaceTB/SmolVLM-500M-Instruct")
model = AutoModelForVision2Seq.from_pretrained(
    "HuggingFaceTB/SmolVLM-500M-Instruct",
    torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32
).to(DEVICE)

def analyze_image(image, prompt="Opisz zawartość dokumentu."):
    messages = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": prompt}]}]
    prompt_text = processor.apply_chat_template(messages, add_generation_prompt=True)
    inputs = processor(text=prompt_text, images=[image], return_tensors="pt").to(DEVICE)
    output = model.generate(**inputs, max_new_tokens=400)
    return processor.batch_decode(output, skip_special_tokens=True)[0]

def summarize_pdf_text(pdf_path):
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() or ""
    summary_prompt = f"Proszę streść następującą treść dokumentu:\n{full_text[:4000]}"
    inputs = processor(text=summary_prompt, images=[], return_tensors="pt").to(DEVICE)
    output = model.generate(**inputs, max_new_tokens=400)
    return processor.batch_decode(output, skip_special_tokens=True)[0]

def summarize_pdf_images(pdf_path):
    images = convert_from_path(pdf_path, dpi=150, poppler_path=POPPLER_PATH)
    summaries = []
    for idx, img in enumerate(images):
        summ = analyze_image(img, prompt=f"Opisz stronę {idx+1} tego dokumentu, wskaż istotne punkty, dane i nagłówki.")
        summaries.append(summ)
    return summaries

def compare_texts(text1, text2):
    prompt = f"Jakie są najważniejsze różnice między tymi dwoma tekstami?\nTekst 1:\n{text1}\n\nTekst 2:\n{text2}"
    inputs = processor(text=prompt, images=[], return_tensors="pt").to(DEVICE)
    output = model.generate(**inputs, max_new_tokens=200)
    return processor.batch_decode(output, skip_special_tokens=True)[0]

def load_and_summarize(path):
    try:
        # Próba odczytu tekstowego PDF
        text = summarize_pdf_text(path)
        if len(text.strip()) > 0:
            return "tekstowy", text
        else:
            # jeśli brak tekstu, traktujemy jako skan
            imgs = summarize_pdf_images(path)
            return "obrazowy", "\n".join(imgs)
    except Exception as e:
        return "error", f"Błąd podczas analizy pliku {path}: {e}"

def main():
    print("=== Interaktywny Analizator PDF oparty na SmolVLM-500M ===")
    print("Podaj ścieżki do plików PDF do załadowania (oddzielone przecinkiem):")
    paths = input().strip().split(",")
    paths = [p.strip() for p in paths if p.strip() != ""]

    documents = {}
    for p in paths:
        print(f"Analizuję plik: {p} ...")
        doc_type, summary = load_and_summarize(p)
        if doc_type == "error":
            print(summary)
        else:
            documents[p] = {"type": doc_type, "summary": summary}
            print(f"Załadowano dokument '{p}', typ: {doc_type}")

    if not documents:
        print("Brak prawidłowo załadowanych dokumentów. Kończę działanie.")
        return

    print("\nMożesz teraz zadawać pytania o wczytane pliki, np:")
    print("- Zapytaj o zawartość konkretnego pliku: zawartość pliku.pdf")
    print("- Poproś o porównanie dwóch plików: porównaj plik1.pdf i plik2.pdf")
    print("- Zapytaj o szczegóły w pliku: szczegóły pliku.pdf")
    print("- Wyjdź z programu wpisując: exit\n")

    while True:
        user_input = input(">> ").strip().lower()

        if user_input == "exit":
            print("Zakończono działanie.")
            break

        # Polecenie o zawartości pliku
        if user_input.startswith("zawartość "):
            filename = user_input.replace("zawartość ", "").strip()
            if filename in documents:
                print(f"Streszczenie zawartości pliku '{filename}':\n")
                print(documents[filename]["summary"])
            else:
                print(f"Plik '{filename}' nie został wczytany lub nazwa jest niepoprawna.")

        # Polecenie porównania dwóch plików
        elif user_input.startswith("porównaj "):
            parts = user_input.replace("porównaj ", "").split(" i ")
            if len(parts) == 2:
                f1, f2 = parts[0].strip(), parts[1].strip()
                if f1 in documents and f2 in documents:
                    print(f"Porównuję pliki '{f1}' i '{f2}'...")
                    diff = compare_texts(documents[f1]["summary"], documents[f2]["summary"])
                    print("Różnice i analiza porównawcza:")
                    print(diff)
                else:
                    print(f"Jeden lub oba pliki '{f1}', '{f2}' nie zostały wczytane.")
            else:
                print("Poprawny format komendy: porównaj plik1.pdf i plik2.pdf")

        # Polecenie o szczegóły pliku
        elif user_input.startswith("szczegóły "):
            filename = user_input.replace("szczegóły ", "").strip()
            if filename in documents:
                print(f"Dodatkowa analiza pliku '{filename}':")
                # Można tu np. ponownie wywołać bardziej szczegółowe zapytanie
                prompt = f"Podaj więcej szczegółów i informacji o zawartości tego dokumentu:\n{documents[filename]['summary'][:3000]}"
                inputs = processor(text=prompt, images=[], return_tensors="pt").to(DEVICE)
                output = model.generate(**inputs, max_new_tokens=400)
                details = processor.batch_decode(output, skip_special_tokens=True)[0]
                print(details)
            else:
                print(f"Plik '{filename}' nie został wczytany lub nazwa jest niepoprawna.")

        else:
            print("Nieznana komenda. Dostępne komendy:\n - zawartość [nazwa_pliku]\n - porównaj [plik1] i [plik2]\n - szczegóły [nazwa_pliku]\n - exit")

if __name__ == "__main__":
    main()
