import os
import subprocess
import sys
import platform
import webbrowser
from pathlib import Path

# Проверка операционной системы
OS = platform.system()
if OS not in ["Windows", "Linux", "Darwin"]:
    print("Unsupported operating system.")
    sys.exit(1)

# Путь для сохранения изображений
OUTPUT_DIR = Path.home() / "DockerImages"
OUTPUT_DIR.mkdir(exist_ok=True)


def is_docker_installed():
    """Проверяет, установлен ли Docker."""
    try:
        subprocess.run(["docker", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_docker():
    """Устанавливает Docker."""
    if OS == "Windows":
        print("Downloading Docker Desktop for Windows...")
        docker_installer = "DockerDesktopInstaller.exe"
        subprocess.run(["curl", "-o", docker_installer, "https://desktop.docker.com/win/main/amd64/DockerDesktopInstaller.exe"]) 
        subprocess.run([docker_installer, "/S"], check=True)
        os.remove(docker_installer)
    elif OS == "Darwin":
        print("Downloading Docker Desktop for macOS...")
        subprocess.run(["brew", "install", "--cask", "docker"], check=True)
    elif OS == "Linux":
        print("Installing Docker on Linux...")
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run(["sudo", "apt-get", "install", "-y", "docker.io"], check=True)
    print("Docker installed successfully.")


def pull_docker_image(image_name):
    """Скачивает Docker-образ."""
    print(f"Pulling Docker image: {image_name}")
    subprocess.run(["docker", "pull", image_name], check=True)


def run_container(image_name):
    """Запускает контейнер и сохраняет изображения."""
    print(f"Running container from image: {image_name}")
    container_name = "my-python-app"
    subprocess.run(["docker", "run", "--name", container_name, image_name], check=True)
    print("Container executed successfully.")


def copy_images_from_container(container_name):
    """Копирует изображения из контейнера на хост."""
    print("Copying images from container...")
    image_files = [
        "3d_plot.png",
        "efficiency_vs_cost.png",
        "efficiency_vs_maintenance.png",
        "cost_vs_maintenance.png"
    ]
    for img in image_files:
        output_path = OUTPUT_DIR / img
        subprocess.run(["docker", "cp", f"{container_name}:/app/{img}", str(output_path)], check=True)
    print("Images copied successfully.")


def open_images():
    """Открывает сохранённые изображения."""
    print("Opening images...")
    for img in OUTPUT_DIR.glob("*.png"):
        if OS == "Windows":
            os.startfile(img)
        elif OS == "Darwin":
            subprocess.run(["open", img], check=True)
        elif OS == "Linux":
            subprocess.run(["xdg-open", img], check=True)
    print("Images opened successfully.")


def cleanup(container_name):
    """Очищает контейнер."""
    print("Cleaning up container...")
    subprocess.run(["docker", "rm", container_name], check=True)


def main():
    # Шаг 1: Проверка и установка Docker
    if not is_docker_installed():
        print("Docker is not installed. Installing Docker...")
        install_docker()

    # Шаг 2: Скачивание Docker-образа
    image_name = "perfavore8/claster3t:latest"  # Замените на имя вашего образа
    pull_docker_image(image_name)

    # Шаг 3: Запуск контейнера
    container_name = "my-python-app"
    run_container(image_name)

    # Шаг 4: Копирование изображений
    copy_images_from_container(container_name)

    # Шаг 5: Открытие изображений
    open_images()

    # Шаг 6: Очистка
    cleanup(container_name)
    print("Automation completed successfully.")


if __name__ == "__main__":
    main()