import os
from gtts import gTTS

def main():
    print("=== TTS Konvertor (Text-to-Speech) ===")
    input_path = input("Zadej cestu k textovému souboru (.txt): ")

    if not os.path.exists(input_path):
        print("Soubor neexistuje.")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    if not text.strip():
        print("Soubor je prázdný.")
        return

    lang = input("Zadej jazyk (např. cs pro češtinu, en pro angličtinu): ") or "cs"
    output_file = input("Zadej název výstupního souboru (bez přípony): ") or "vystup"
    output_file += ".mp3"

    try:
        tts = gTTS(text=text, lang=lang)
        tts.save(output_file)
        print(f"Soubor byl uložen jako {output_file}")
    except Exception as e:
        print(f"Chyba při převodu: {e}")

if __name__ == "__main__":
    main()
