
import os

def scan_document(content):
    semnale = ["corupție", "mită", "Nicușor Dan", "președinte", "offshore", "licitație trucată"]
    alerte = [cuv for cuv in semnale if cuv.lower() in content.lower()]
    return alerte

def main():
    print("=== AI Anticorupție - Monitorizare Documente ===")
    path = "./scan_docs"
    if not os.path.exists(path):
        print("Folderul 'scan_docs' nu există.")
        return
    for filename in os.listdir(path):
        if filename.endswith(".txt"):
            with open(os.path.join(path, filename), "r", encoding="utf-8") as file:
                content = file.read()
                alerte = scan_document(content)
                if alerte:
                    print(f"[ALERTĂ] Fișier: {filename} conține: {', '.join(alerte)}")
                else:
                    print(f"[OK] Fișierul {filename} nu conține semnale de corupție.")

if __name__ == "__main__":
    main()
