import os
import shutil
import subprocess
from glob import glob

def prepare_usb(device="/dev/sdb"):
    """Разметка флешки в стиле Ventoy"""
    print("🔧 Создаём разделы...")
    os.system(f"""
    sudo parted {device} mklabel gpt
    sudo parted {device} mkpart primary fat32 1MiB 90%
    sudo parted {device} mkpart primary ext4 90% 100%
    sudo mkfs.fat -F32 {device}1
    sudo mkfs.ext4 {device}2
    """)

def install_grub(device="/dev/sdb"):
    """Установка GRUB2 на флешку"""
    print("📀 Устанавливаем GRUB2...")
    os.system(f"""
    sudo mount {device}1 /mnt
    sudo grub-install --target=x86_64-efi --removable --boot-directory=/mnt/boot
    sudo cp -r /usr/lib/grub/x86_64-efi /mnt/boot/grub/
    """)

def create_grub_config():
    """Генерация меню загрузки"""
    menu = """
    set timeout=5
    menuentry "Windows 10" {
        search --file --no-floppy --set=root /ISO/win10.iso
        map --mem /ISO/win10.iso (hd32)
        chainloader (hd32)
    }
    menuentry "Ubuntu Live" {
        search --file --no-floppy --set=root /ISO/ubuntu.iso
        loopback loop /ISO/ubuntu.iso
        linux (loop)/casper/vmlinuz boot=casper iso-scan/filename=/ISO/ubuntu.iso
        initrd (loop)/casper/initrd
    }
    """
    with open("/mnt/boot/grub/grub.cfg", "w") as f:
        f.write(menu)

def copy_isos(iso_folder="ISO"):
    """Копируем ISO-образы на флешку"""
    os.makedirs(f"/mnt/{iso_folder}", exist_ok=True)
    for iso in glob("*.iso"):
        shutil.copy(iso, f"/mnt/{iso_folder}")
    print(f"📂 ISO-образы скопированы в /{iso_folder}")

if __name__ == "__main__":
    print("""
    ██╗   ██╗███████╗███╗   ██╗████████╗ ██████╗ ██╗   ██╗
    ██║   ██║██╔════╝████╗  ██║╚══██╔══╝██╔═══██╗╚██╗ ██╔╝
    ██║   ██║█████╗  ██╔██╗ ██║   ██║   ██║   ██║ ╚████╔╝ 
    ╚██╗ ██╔╝██╔══╝  ██║╚██╗██║   ██║   ██║   ██║  ╚██╔╝  
     ╚████╔╝ ███████╗██║ ╚████║   ██║   ╚██████╔╝   ██║   
      ╚═══╝  ╚══════╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝    ╚═╝   
    """)
    prepare_usb()
    install_grub()
    create_grub_config()
    copy_isos()
    print("✅ Готово! Флешка может загружать ISO напрямую.")