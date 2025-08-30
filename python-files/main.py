import os
import openai  # Példaként az OpenAI API-t használjuk
import shutil

# API kulcs beállítása
openai.api_key = os.getenv("OPENAI_API_KEY")

def modify_script(file_path, prompt):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        
        # API hívás a script módosításához
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"{prompt}\n\n{content}",
            max_tokens=150
        )
        
        modified_content = response.choices[0].text.strip()
        
        with open(file_path, 'w') as file:
            file.write(modified_content)
        
        print(f"A {file_path} fájl sikeresen módosítva.")
    
    except Exception as e:
        print(f"Hiba történt a fájl módosítása közben: {e}")

def delete_script(file_path):
    try:
        os.remove(file_path)
        print(f"A {file_path} fájl sikeresen törölve.")
    except Exception as e:
        print(f"Hiba történt a fájl törlése közben: {e}")

def move_script(src_path, dest_path):
    try:
        shutil.move(src_path, dest_path)
        print(f"A {src_path} fájl sikeresen áthelyezve ide: {dest_path}.")
    except Exception as e:
        print(f"Hiba történt a fájl áthelyezése közben: {e}")

def main():
    print("Script kezelő program")
    while True:
        command = input("Adjon meg egy parancsot (modify/delete/move/exit): ").strip().lower()
        
        if command == "exit":
            break
        
        if command == "modify":
            file_path = input("Adja meg a módosítandó fájl elérési útját: ")
            prompt = input("Adja meg a módosításhoz szükséges promptot: ")
            modify_script(file_path, prompt)
        
        elif command == "delete":
            file_path = input("Adja meg a törlendő fájl elérési útját: ")
            delete_script(file_path)
        
        elif command == "move":
            src_path = input("Adja meg az áthelyezendő fájl elérési útját: ")
            dest_path = input("Adja meg az új elérési útját: ")
            move_script(src_path, dest_path)
        
        else:
            print("Érvénytelen parancs. Kérem, próbálja újra.")

if __name__ == "__main__":
    main()