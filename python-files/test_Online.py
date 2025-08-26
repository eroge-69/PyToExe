import os
import shutil

# Modifica qui i percorsi delle cartelle
rete = r"U:\Test_Ricette"
target = r"C:\Users\matteo.poli\Desktop\New folder"

def sync(src, dst):
    for root, dirs, files in os.walk(src):
        rel_path = os.path.relpath(root, src)
        dst_root = os.path.join(dst, rel_path)

        if not os.path.exists(dst_root):
            os.makedirs(dst_root)

        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(dst_root, file)

            if not os.path.exists(dst_file):
                shutil.copy2(src_file, dst_file)
                print(f"Nuovo file copiato: {src_file} → {dst_file}")
            else:
                if os.path.getmtime(src_file) > os.path.getmtime(dst_file):
                    shutil.copy2(src_file, dst_file)
                    print(f"Overscritto con versione più nuova: {src_file} → {dst_file}")

# Sincronizzazione bidirezionale
sync(rete, target)
sync(target, rete)

print("Sincronizzazione completata")
input("Premi INVIO per chiudere...")