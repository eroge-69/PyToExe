#!/usr/bin/env python3
"""
Crea una imagen Docker con el toolchain de ST para STM32MP1
directamente desde Windows, utilizando WSL.
Autor: Pakito ;)
"""

import os
import sys
import shutil
import textwrap
import pathlib
import tempfile
import subprocess


def ask_until_ok(prompt, check):
    """Pregunta al usuario hasta que la función check devuelva True."""
    while True:
        value = input(prompt).strip().strip('"')
        if check(value):
            return value
        print("⛔  Valor inválido, inténtalo de nuevo.\n")


def build_dockerfile(ctx_dir: pathlib.Path, installer_name: str):
    """Genera el Dockerfile dentro del contexto de build."""
    dockerfile = ctx_dir / "Dockerfile"
    dockerfile.write_text(textwrap.dedent(f"""\
        FROM ubuntu:22.04

        ENV DEBIAN_FRONTEND=noninteractive \\
            SDK_INSTALL_DIR=/opt/st/sdk

        # ---- Utilities --------------------------------------------------------
        RUN apt-get update && \\
            apt-get install -y --no-install-recommends \\
                python3 xz-utils sudo tar gzip bzip2 \\
                ca-certificates git build-essential \\
                file findutils && \\
            rm -rf /var/lib/apt/lists/*

        # ---- Copy ST SDK installer -------------------------------------------
        COPY {installer_name} /tmp/sdk.sh

        # ---- Install SDK ------------------------------------------------------
        RUN chmod +x /tmp/sdk.sh && \\
            sed -i 's|for replace in "\\$target_sdk_dir -maxdepth 1" "\\$native_sysroot"|for dir in "\\$target_sdk_dir" "\\$native_sysroot"|' /tmp/sdk.sh && \\
            sed -i 's|find \\$replace -type f|find "\\$dir" -xdev -maxdepth 1 -type f|' /tmp/sdk.sh && \\
            sed -i 's|xargs -n100|xargs -r -n100|' /tmp/sdk.sh && \\
            /tmp/sdk.sh -y -d ${{SDK_INSTALL_DIR}} && \\
            rm -f /tmp/sdk.sh

        # ---- Auto-source SDK in interactive shells ---------------------------
        RUN echo 'for f in ${{SDK_INSTALL_DIR}}/environment-setup-*; do [ -f "$f" ] && . "$f"; done' > /etc/profile.d/90-stm32mp1-sdk.sh

        WORKDIR /workspace
        ENTRYPOINT ["/bin/bash", "-l"]
    """))
    return dockerfile


def main() -> None:
    print("\n=== Generador de imagen Docker STM32MP1 ===\n")

    # 1. Pedimos la ruta al .sh y la validamos
    sdk_path = ask_until_ok(
        "Ruta del instalador (.sh) de ST SDK: ",
        lambda p: os.path.isfile(p),
    )
    sdk_path = pathlib.Path(sdk_path)
    installer_name = sdk_path.name

    # 2. Pedimos el nombre de la imagen (con tag)
    image_name = input("Nombre de la imagen Docker (ej. stm32mp1-sdk:latest): ").strip()
    if ":" not in image_name:
        image_name += ":latest"

    # 3. Creamos el contexto de build temporal
    with tempfile.TemporaryDirectory() as ctx:
        ctx_path = pathlib.Path(ctx)
        shutil.copy2(sdk_path, ctx_path / installer_name)
        dockerfile = build_dockerfile(ctx_path, installer_name)
        print(f"\n✅ Dockerfile generado en: {dockerfile}")

        # 4. Lanzamos el build dentro de WSL
        print("⏳ Iniciando la construcción dentro de WSL...\n")
        wsl_build_cmd = (
            f"cd $(wslpath '{ctx}') && "
            f"docker build -t '{image_name}' ."
        )
        result = subprocess.run(
            ["wsl", "bash", "-c", wsl_build_cmd],
            text=True,
        )

        if result.returncode == 0:
            print(f"\n🎉 Imagen '{image_name}' creada satisfactoriamente.")
        else:
            print("\n❌ Hubo errores durante la construcción.")
            sys.exit(result.returncode)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelado por el usuario.")
