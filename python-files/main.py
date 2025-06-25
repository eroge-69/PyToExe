import sys
import os
import pyassimp

def convert(input_path, output_format="fbx"):
    try:
        scene = pyassimp.load(input_path)
        if scene is None:
            print("Hiba: nem sikerült betölteni a fájlt.")
            return

        filename, _ = os.path.splitext(input_path)
        output_path = f"{filename}.{output_format}"

        pyassimp.export(scene, output_path, file_type=output_format)
        pyassimp.release(scene)

        print(f"Sikeres konvertálás: {output_path}")
    except Exception as e:
        print(f"Hiba: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Használat: húzz rá egy .glb vagy .gltf fájlt az .exe-re.")
        input("Nyomj egy entert a kilépéshez...")
        sys.exit(1)

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print("A megadott fájl nem létezik.")
        sys.exit(1)

    # Módosítsd itt, ha OBJ-t akarsz:
    convert(input_file, output_format="fbx")  # vagy "obj"
