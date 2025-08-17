#!/usr/bin/env python3
"""
Script para compilar la aplicación Bypass MENU a ejecutable
Uso: python build_exe.py
"""

import os
import sys
import subprocess
import shutil

def create_spec_file():
    """Crear archivo .spec para PyInstaller"""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['bypass_menu.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('index.html', '.'),
        ('style.css', '.'),
        ('script.js', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BypassMENU',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
"""
    
    with open('bypass_menu.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✓ Archivo .spec creado")

def install_pyinstaller():
    """Instalar PyInstaller"""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
        print("✓ PyInstaller instalado")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando PyInstaller: {e}")
        return False
    return True

def build_executable():
    """Compilar el ejecutable"""
    try:
        # Usar el archivo spec personalizado
        cmd = [sys.executable, '-m', 'PyInstaller', '--clean', 'bypass_menu.spec']
        subprocess.check_call(cmd)
        print("✓ Ejecutable compilado exitosamente")
        
        # Verificar que el ejecutable existe
        exe_path = os.path.join('dist', 'BypassMENU.exe')
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"✓ Archivo ejecutable: {exe_path} ({size_mb:.1f} MB)")
            return True
        else:
            print("❌ No se encontró el ejecutable generado")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error compilando: {e}")
        return False

def cleanup():
    """Limpiar archivos temporales"""
    try:
        # Eliminar carpetas temporales
        folders_to_remove = ['build', '__pycache__']
        for folder in folders_to_remove:
            if os.path.exists(folder):
                shutil.rmtree(folder)
                print(f"✓ Eliminado: {folder}")
        
        # Eliminar archivo spec
        if os.path.exists('bypass_menu.spec'):
            os.remove('bypass_menu.spec')
            print("✓ Eliminado: bypass_menu.spec")
            
    except Exception as e:
        print(f"⚠️ Error limpiando: {e}")

def main():
    """Función principal"""
    print("🔨 Compilando Bypass MENU a ejecutable...")
    print("=" * 50)
    
    # Verificar archivos necesarios
    required_files = ['bypass_menu.py', 'index.html', 'style.css', 'script.js']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Archivos faltantes: {', '.join(missing_files)}")
        return False
    
    print("✓ Todos los archivos necesarios encontrados")
    
    # Instalar PyInstaller
    if not install_pyinstaller():
        return False
    
    # Crear archivo spec
    create_spec_file()
    
    # Compilar ejecutable
    if not build_executable():
        return False
    
    # Limpiar archivos temporales
    cleanup()
    
    print("\n" + "=" * 50)
    print("🎉 ¡Compilación completada!")
    print("📁 El ejecutable está en: dist/BypassMENU.exe")
    print("\n📋 Instrucciones:")
    print("1. Copia el archivo BypassMENU.exe donde quieras")
    print("2. Ejecuta como administrador para funcionalidad completa")
    print("3. El ejecutable incluye tanto la interfaz de escritorio como la web")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        input("\nPresiona Enter para salir...")
        sys.exit(1)
    else:
        input("\nPresiona Enter para salir...")