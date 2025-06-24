#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EINFACHER EXCEL-KONVERTER
=========================

Benutzerfreundliches Wrapper-Skript für die Excel-Konvertierung.
Einfach zu verwenden - keine Kommandozeilen-Parameter erforderlich.

Verwendung:
1. Lege deine Excel-Datei in den gleichen Ordner wie dieses Skript
2. Führe das Skript aus
3. Wähle die zu konvertierende Datei aus
4. Die konvertierte Datei wird automatisch erstellt

Autor: Manus AI
"""

import os
import sys
import glob
from excel_converter import ExcelPipeConverter

def find_excel_files():
    """Findet alle Excel-Dateien im aktuellen Verzeichnis"""
    patterns = ['*.xlsx', '*.xls']
    files = []
    
    for pattern in patterns:
        files.extend(glob.glob(pattern))
    
    return sorted(files)

def select_file(files):
    """Lässt den Benutzer eine Datei auswählen"""
    if not files:
        print("❌ Keine Excel-Dateien im aktuellen Verzeichnis gefunden!")
        return None
    
    if len(files) == 1:
        print(f"📁 Gefundene Excel-Datei: {files[0]}")
        return files[0]
    
    print("📁 Gefundene Excel-Dateien:")
    for i, file in enumerate(files, 1):
        print(f"  {i}. {file}")
    
    while True:
        try:
            choice = input(f"\nWähle eine Datei (1-{len(files)}): ").strip()
            index = int(choice) - 1
            
            if 0 <= index < len(files):
                return files[index]
            else:
                print(f"❌ Ungültige Auswahl. Bitte wähle eine Zahl zwischen 1 und {len(files)}.")
        
        except (ValueError, KeyboardInterrupt):
            print("\n❌ Abgebrochen.")
            return None

def main():
    """Hauptfunktion"""
    print("🔄 EXCEL PIPE-KONVERTER")
    print("=" * 50)
    print("Konvertiert Excel-Dateien mit pipe-getrennten Werten (|)")
    print()
    
    # Finde Excel-Dateien
    excel_files = find_excel_files()
    
    # Lasse Benutzer Datei auswählen
    selected_file = select_file(excel_files)
    
    if not selected_file:
        return
    
    print(f"\n🔄 Konvertiere: {selected_file}")
    print("-" * 50)
    
    # Erstelle Converter
    converter = ExcelPipeConverter(log_level='INFO')
    
    # Bestimme Ausgabedatei
    base_name = os.path.splitext(selected_file)[0]
    output_file = f"{base_name}_konvertiert.xlsx"
    
    # Erstelle automatisch ein Backup
    backup_file = converter.create_backup(selected_file)
    print(f"💾 Backup erstellt: {backup_file}")
    
    # Führe Konvertierung durch
    success = converter.convert_excel_file(
        input_path=selected_file,
        output_path=output_file
    )
    
    if success:
        print(f"\n✅ Konvertierung erfolgreich!")
        print(f"📄 Ausgabedatei: {output_file}")
        print(f"💾 Backup: {backup_file}")
        
        # Zeige Vorschau der konvertierten Daten
        try:
            import pandas as pd
            df = pd.read_excel(output_file)
            print(f"\n📊 Vorschau der konvertierten Daten ({df.shape[0]} Zeilen):")
            print(df.head(10).to_string(index=False))
            
            if df.shape[0] > 10:
                print(f"... und {df.shape[0] - 10} weitere Zeilen")
        
        except Exception as e:
            print(f"⚠️  Konnte keine Vorschau anzeigen: {e}")
    
    else:
        print(f"\n❌ Konvertierung fehlgeschlagen!")
        print("📋 Prüfe die Log-Datei 'excel_converter.log' für Details.")
    
    input("\nDrücke Enter zum Beenden...")

if __name__ == "__main__":
    main()

