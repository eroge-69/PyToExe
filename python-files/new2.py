import os
import getpass
import sys
from pathlib import Path

class FolderLocker:
    def __init__(self):
        self.folder_name = "Private"
        self.locked_name = "Control Panel.{21EC2020-3AEA-1069-A2DD-08002B30309D}"
        self.password = "250825no.93R!"
    
    def run(self):
        """Ejecutar la aplicación principal"""
        print("=== FOLDER LOCKER PYTHON ===")
        print(f"Directorio actual: {os.getcwd()}")
        print()
        
        self.show_status()
        print()
        
        if self.is_locked():
            self.unlock_folder()
        elif not self.folder_exists():
            self.create_folder()
        else:
            self.confirm_lock()
    
    def is_locked(self):
        """Verificar si está bloqueado"""
        return os.path.exists(self.locked_name)
    
    def folder_exists(self):
        """Verificar si existe el folder"""
        return os.path.exists(self.folder_name)
    
    def show_status(self):
        """Mostrar estado actual"""
        if self.is_locked():
            print("🟢 Estado: BLOQUEADO")
            print(f"   Nombre: {self.locked_name}")
        elif self.folder_exists():
            print("🔴 Estado: DESBLOQUEADO")
            print(f"   Nombre: {self.folder_name}")
        else:
            print("🟡 Estado: NO EXISTE")
            print(f"   Se creará: {self.folder_name}")
    
    def confirm_lock(self):
        """Confirmar bloqueo"""
        while True:
            print("¿Está seguro de bloquear este Folder? (Y/N)")
            try:
                choice = input().strip().upper()
                if choice == 'Y':
                    self.lock_folder()
                    break
                elif choice == 'N':
                    print("Operación cancelada")
                    break
                else:
                    print("Invalid choice. Por favor ingrese Y o N")
            except KeyboardInterrupt:
                print("\nOperación cancelada")
                break
    
    def lock_folder(self):
        """Bloquear el folder"""
        try:
            os.rename(self.folder_name, self.locked_name)
            # Ocultar y marcar como sistema (Windows)
            if sys.platform == 'win32':
                os.system(f'attrib +h +s "{self.locked_name}"')
            print("✅ Folder locked successfully")
        except Exception as e:
            print(f"❌ Error al bloquear: {e}")
    
    def unlock_folder(self):
        """Desbloquear el folder"""
        try:
            print("Digite la contraseña para Desbloquear el Folder:")
            pass_input = getpass.getpass("")  # Entrada oculta
            
            if pass_input == self.password:
                try:
                    # Remover atributos ocultos
                    if sys.platform == 'win32':
                        os.system(f'attrib -h -s "{self.locked_name}"')
                    os.rename(self.locked_name, self.folder_name)
                    print("✅ Folder Unlocked successfully")
                except Exception as e:
                    print(f"❌ Error al desbloquear: {e}")
            else:
                print("❌ Invalid password")
                input("Presione Enter para continuar...")
                
        except KeyboardInterrupt:
            print("\nOperación cancelada")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def create_folder(self):
        """Crear folder"""
        try:
            os.makedirs(self.folder_name, exist_ok=True)
            print("✅ Private created successfully")
        except Exception as e:
            print(f"❌ Error al crear folder: {e}")

def main():
    # Configurar para Windows
    if sys.platform == 'win32':
        os.system('chcp 65001 > nul')  # UTF-8
        os.system('title Folder Locker Python')
    
    # Ejecutar la aplicación
    locker = FolderLocker()
    locker.run()
    
    # Pausa final
    input("\nPresione Enter para salir...")

if __name__ == "__main__":
    main()