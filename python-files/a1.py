import json
import os
import sys

def json_to_m3u(json_file):
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("JSON muss eine Liste von Objekten sein.")

        output_file = os.path.splitext(json_file)[0] + ".m3u"

        with open(output_file, 'w', encoding='utf-8') as m3u:
            m3u.write("#EXTM3U\n")
            for entry in data:
                title = entry.get("title", "Unbenannt")
                url = entry.get("url", "")
                if url:
                    m3u.write(f"#EXTINF:-1,{title}\n{url}\n")

        print(f"✅ M3U-Datei wurde erstellt: {output_file}")

    except Exception as e:
        print(f"❌ Fehler: {e}")

def main():
    json_filename = "channels.json"
    if not os.path.exists(json_filename):
        print(f"❌ Datei '{json_filename}' nicht gefunden im Ordner: {os.getcwd()}")
        input("\nDrücke Enter zum Beenden...")
        sys.exit(1)

    json_to_m3u(json_filename)
    input("\nDrücke Enter zum Beenden...")

if __name__ == "__main__":
    main()