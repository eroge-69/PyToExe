#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IDIOTENSICHERE EXCEL-KONVERTIERUNGSLÖSUNG
==========================================

Robuste Lösung zur Konvertierung von Excel-Dateien mit mehrzeiligen Werten,
die durch "|" getrennt sind.

Autor: Manus AI
Datum: 24.06.2025
Version: 1.0

Diese Lösung behandelt alle bekannten Edge Cases und ist für den produktiven
Einsatz konzipiert.
"""

import pandas as pd
import numpy as np
import os
import sys
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import argparse
import json

class ExcelPipeConverter:
    """
    Robuste Klasse zur Konvertierung von Excel-Dateien mit pipe-getrennten Werten
    """
    
    def __init__(self, log_level: str = 'INFO'):
        """
        Initialisiert den Converter
        
        Args:
            log_level: Logging-Level (DEBUG, INFO, WARNING, ERROR)
        """
        self.setup_logging(log_level)
        self.logger = logging.getLogger(__name__)
        self.stats = {
            'input_rows': 0,
            'output_rows': 0,
            'processed_sheets': 0,
            'errors': 0,
            'warnings': 0
        }
    
    def setup_logging(self, log_level: str):
        """Konfiguriert das Logging"""
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('excel_converter.log', encoding='utf-8')
            ]
        )
    
    def validate_input_file(self, file_path: str) -> bool:
        """
        Validiert die Eingabedatei
        
        Args:
            file_path: Pfad zur Excel-Datei
            
        Returns:
            True wenn Datei gültig ist, False sonst
        """
        if not os.path.exists(file_path):
            self.logger.error(f"Datei nicht gefunden: {file_path}")
            return False
        
        if not file_path.lower().endswith(('.xlsx', '.xls')):
            self.logger.error(f"Ungültiges Dateiformat: {file_path}")
            return False
        
        try:
            # Teste ob Datei lesbar ist
            pd.ExcelFile(file_path)
            self.logger.info(f"Eingabedatei validiert: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Fehler beim Lesen der Datei: {e}")
            return False
    
    def analyze_pipe_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analysiert die Struktur der pipe-getrennten Werte
        
        Args:
            df: DataFrame zur Analyse
            
        Returns:
            Dictionary mit Analyseergebnissen
        """
        analysis = {
            'columns_with_pipes': [],
            'max_parts_per_column': {},
            'max_parts_overall': 0,
            'inconsistent_columns': [],
            'empty_parts_found': False
        }
        
        for col in df.columns:
            pipe_found = False
            max_parts = 1
            parts_counts = []
            
            for idx, value in df[col].items():
                if pd.notna(value) and '|' in str(value):
                    pipe_found = True
                    parts = str(value).split('|')
                    parts_count = len(parts)
                    parts_counts.append(parts_count)
                    max_parts = max(max_parts, parts_count)
                    
                    # Prüfe auf leere Teile
                    if any(part.strip() == '' for part in parts):
                        analysis['empty_parts_found'] = True
            
            if pipe_found:
                analysis['columns_with_pipes'].append(col)
                analysis['max_parts_per_column'][col] = max_parts
                analysis['max_parts_overall'] = max(analysis['max_parts_overall'], max_parts)
                
                # Prüfe auf inkonsistente Anzahl von Teilen
                if len(set(parts_counts)) > 1:
                    analysis['inconsistent_columns'].append(col)
        
        self.logger.info(f"Pipe-Struktur analysiert: {len(analysis['columns_with_pipes'])} Spalten mit Pipes")
        return analysis
    
    def clean_and_split_value(self, value: Any, expected_parts: int) -> List[str]:
        """
        Bereinigt und teilt einen Wert auf
        
        Args:
            value: Zu teilender Wert
            expected_parts: Erwartete Anzahl von Teilen
            
        Returns:
            Liste der bereinigten Teile
        """
        if pd.isna(value):
            return [''] * expected_parts
        
        value_str = str(value).strip()
        
        if '|' not in value_str:
            # Wenn kein Pipe vorhanden, verwende Wert nur für ersten Teil
            result = [value_str] + [''] * (expected_parts - 1)
            return result[:expected_parts]
        
        # Teile am Pipe-Zeichen
        parts = value_str.split('|')
        
        # Bereinige jeden Teil
        cleaned_parts = [part.strip() for part in parts]
        
        # Fülle auf erwartete Anzahl auf oder kürze
        if len(cleaned_parts) < expected_parts:
            cleaned_parts.extend([''] * (expected_parts - len(cleaned_parts)))
        elif len(cleaned_parts) > expected_parts:
            self.logger.warning(f"Mehr Teile als erwartet: {len(cleaned_parts)} > {expected_parts}")
            cleaned_parts = cleaned_parts[:expected_parts]
        
        return cleaned_parts
    
    def convert_dataframe(self, df: pd.DataFrame, sheet_name: str = '') -> pd.DataFrame:
        """
        Konvertiert einen DataFrame mit pipe-getrennten Werten
        
        Args:
            df: Zu konvertierender DataFrame
            sheet_name: Name des Arbeitsblatts (für Logging)
            
        Returns:
            Konvertierter DataFrame
        """
        self.logger.info(f"Konvertiere Arbeitsblatt '{sheet_name}': {df.shape[0]} Zeilen, {df.shape[1]} Spalten")
        self.stats['input_rows'] += df.shape[0]
        
        # Analysiere Pipe-Struktur
        analysis = self.analyze_pipe_structure(df)
        
        if not analysis['columns_with_pipes']:
            self.logger.info("Keine Pipes gefunden - gebe ursprünglichen DataFrame zurück")
            self.stats['output_rows'] += df.shape[0]
            return df.copy()
        
        # Bestimme maximale Anzahl von Teilen
        max_parts = analysis['max_parts_overall']
        self.logger.info(f"Maximale Anzahl von Teilen: {max_parts}")
        
        # Warne bei inkonsistenten Spalten
        if analysis['inconsistent_columns']:
            self.logger.warning(f"Inkonsistente Spalten gefunden: {analysis['inconsistent_columns']}")
            self.stats['warnings'] += len(analysis['inconsistent_columns'])
        
        # Erstelle neue Zeilen
        expanded_rows = []
        
        for idx, row in df.iterrows():
            try:
                # Bestimme die tatsächliche Anzahl von Teilen für diese Zeile
                actual_parts = 1
                for col in analysis['columns_with_pipes']:
                    if pd.notna(row[col]) and '|' in str(row[col]):
                        parts_count = len(str(row[col]).split('|'))
                        actual_parts = max(actual_parts, parts_count)
                
                # Erstelle für jeden Teil eine neue Zeile
                for part_idx in range(actual_parts):
                    new_row = {}
                    
                    for col in df.columns:
                        if col in analysis['columns_with_pipes']:
                            # Teile pipe-getrennte Werte
                            parts = self.clean_and_split_value(row[col], actual_parts)
                            new_row[col] = parts[part_idx] if part_idx < len(parts) else ''
                        else:
                            # Für Spalten ohne Pipes: Wert nur in erste Zeile
                            new_row[col] = row[col] if part_idx == 0 else ''
                    
                    expanded_rows.append(new_row)
                
            except Exception as e:
                self.logger.error(f"Fehler bei Zeile {idx}: {e}")
                self.stats['errors'] += 1
                continue
        
        # Erstelle neuen DataFrame
        result_df = pd.DataFrame(expanded_rows)
        
        # Entferne komplett leere Zeilen
        result_df = result_df.dropna(how='all')
        
        self.logger.info(f"Konvertierung abgeschlossen: {result_df.shape[0]} Ausgabezeilen")
        self.stats['output_rows'] += result_df.shape[0]
        
        return result_df
    
    def convert_excel_file(self, 
                          input_path: str, 
                          output_path: Optional[str] = None,
                          sheet_names: Optional[List[str]] = None) -> bool:
        """
        Konvertiert eine komplette Excel-Datei
        
        Args:
            input_path: Pfad zur Eingabedatei
            output_path: Pfad zur Ausgabedatei (optional)
            sheet_names: Liste der zu verarbeitenden Arbeitsblätter (optional)
            
        Returns:
            True bei Erfolg, False bei Fehler
        """
        try:
            # Validiere Eingabedatei
            if not self.validate_input_file(input_path):
                return False
            
            # Bestimme Ausgabepfad
            if output_path is None:
                base_name = os.path.splitext(input_path)[0]
                output_path = f"{base_name}_converted.xlsx"
            
            self.logger.info(f"Starte Konvertierung: {input_path} -> {output_path}")
            
            # Lade Excel-Datei
            excel_file = pd.ExcelFile(input_path)
            
            # Bestimme zu verarbeitende Arbeitsblätter
            if sheet_names is None:
                sheet_names = excel_file.sheet_names
            
            # Konvertiere jedes Arbeitsblatt
            converted_sheets = {}
            
            for sheet_name in sheet_names:
                if sheet_name not in excel_file.sheet_names:
                    self.logger.warning(f"Arbeitsblatt '{sheet_name}' nicht gefunden")
                    self.stats['warnings'] += 1
                    continue
                
                try:
                    # Lade Arbeitsblatt
                    df = pd.read_excel(input_path, sheet_name=sheet_name)
                    
                    # Konvertiere
                    converted_df = self.convert_dataframe(df, sheet_name)
                    converted_sheets[sheet_name] = converted_df
                    self.stats['processed_sheets'] += 1
                    
                except Exception as e:
                    self.logger.error(f"Fehler bei Arbeitsblatt '{sheet_name}': {e}")
                    self.stats['errors'] += 1
                    continue
            
            if not converted_sheets:
                self.logger.error("Keine Arbeitsblätter konnten konvertiert werden")
                return False
            
            # Speichere Ergebnis
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                for sheet_name, df in converted_sheets.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            self.logger.info(f"Konvertierung erfolgreich abgeschlossen: {output_path}")
            self.print_statistics()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Unerwarteter Fehler: {e}")
            return False
    
    def print_statistics(self):
        """Gibt Statistiken aus"""
        print("\n" + "="*60)
        print("KONVERTIERUNGS-STATISTIKEN")
        print("="*60)
        print(f"Eingabezeilen:        {self.stats['input_rows']}")
        print(f"Ausgabezeilen:        {self.stats['output_rows']}")
        print(f"Verarbeitete Blätter: {self.stats['processed_sheets']}")
        print(f"Warnungen:            {self.stats['warnings']}")
        print(f"Fehler:               {self.stats['errors']}")
        
        if self.stats['input_rows'] > 0:
            expansion_factor = self.stats['output_rows'] / self.stats['input_rows']
            print(f"Expansionsfaktor:     {expansion_factor:.2f}x")
        
        print("="*60)
    
    def create_backup(self, file_path: str) -> str:
        """
        Erstellt ein Backup der ursprünglichen Datei
        
        Args:
            file_path: Pfad zur zu sichernden Datei
            
        Returns:
            Pfad zur Backup-Datei
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(file_path)[0]
        extension = os.path.splitext(file_path)[1]
        backup_path = f"{base_name}_backup_{timestamp}{extension}"
        
        import shutil
        shutil.copy2(file_path, backup_path)
        self.logger.info(f"Backup erstellt: {backup_path}")
        
        return backup_path


def main():
    """Hauptfunktion für Kommandozeilen-Nutzung"""
    parser = argparse.ArgumentParser(
        description="Idiotensichere Excel-Konvertierung für pipe-getrennte Werte",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python excel_converter.py input.xlsx
  python excel_converter.py input.xlsx -o output.xlsx
  python excel_converter.py input.xlsx -s "Sheet1" "Sheet2"
  python excel_converter.py input.xlsx --backup --log-level DEBUG
        """
    )
    
    parser.add_argument('input_file', help='Pfad zur Excel-Eingabedatei')
    parser.add_argument('-o', '--output', help='Pfad zur Ausgabedatei (optional)')
    parser.add_argument('-s', '--sheets', nargs='+', help='Zu verarbeitende Arbeitsblätter')
    parser.add_argument('--backup', action='store_true', help='Backup der Originaldatei erstellen')
    parser.add_argument('--log-level', default='INFO', 
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging-Level')
    
    args = parser.parse_args()
    
    # Erstelle Converter
    converter = ExcelPipeConverter(log_level=args.log_level)
    
    # Erstelle Backup falls gewünscht
    if args.backup:
        converter.create_backup(args.input_file)
    
    # Führe Konvertierung durch
    success = converter.convert_excel_file(
        input_path=args.input_file,
        output_path=args.output,
        sheet_names=args.sheets
    )
    
    if success:
        print("\n✅ Konvertierung erfolgreich abgeschlossen!")
        sys.exit(0)
    else:
        print("\n❌ Konvertierung fehlgeschlagen!")
        sys.exit(1)


if __name__ == "__main__":
    main()

