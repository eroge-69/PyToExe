import os

# --- Código principal ---
def converter_mtl_dds_para_png(caminho_mtl):
    if not os.path.isfile(caminho_mtl):
        print("Arquivo MTL não encontrado:", caminho_mtl)
        return

    with open(caminho_mtl, "r") as f:
        linhas = f.readlines()

    novas_linhas = [linha.replace(".dds", ".png") for linha in linhas]

    with open(caminho_mtl, "w") as f:
        f.writelines(novas_linhas)

    print("Conversão concluída:", caminho_mtl)


if __name__ == "__main__":
    mtl_path = os.path.join(os.path.dirname(__file__), "seuarquivo.mtl")
    converter_mtl_dds_para_png(mtl_path)


# --- Parte cx_Freeze para gerar .exe ---
try:
    from cx_Freeze import setup, Executable

    if "build" in os.sys.argv:
        setup(
            name="MTL2PNG",
            version="1.0",
            description="Converte DDS para PNG dentro de arquivos MTL",
            executables=[Executable(__file__, base=None)]
        )
except ImportError:
    pass  # cx_Freeze não instalado, só roda a conversão normal
