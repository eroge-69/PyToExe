#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import datetime
from pathlib import Path

class NSISScriptGenerator:
    def __init__(self):
        self.config = {
            'program_name': 'MeinProgramm',
            'output_file': 'MeinProgramm-Installer.exe',
            'main_exe': 'hauptprogramm.exe',
            'install_dir': '$LOCALAPPDATA\\MeinProgramm',
            'components': [],
            'security_checks': True,
            'human_verification': True,
            'background_download': True,
            'antivirus_warning': True
        }
    
    def print_header(self):
        print("=" * 60)
        print("NSIS SCRIPT GENERATOR")
        print("Erstellt automatisch Installer-Skripte mit Sicherheitsprüfungen")
        print("=" * 60)
        print()
    
    def get_basic_info(self):
        print("📋 Grundlegende Informationen:")
        print("-" * 40)
        
        self.config['program_name'] = input("Programmname: ") or self.config['program_name']
        self.config['main_exe'] = input("Haupt-EXE Dateiname: ") or self.config['main_exe']
        self.config['output_file'] = input("Ausgabe-Installer Name: ") or self.config['output_file']
        self.config['install_dir'] = input("Installationsverzeichnis: ") or self.config['install_dir']
        
        print()
    
    def get_components(self):
        print("📦 Zusätzliche Komponenten:")
        print("-" * 40)
        print("Geben Sie die URLs der herunterzuladenden Komponenten ein")
        print("(Leere Eingabe beendet die Eingabe)")
        print()
        
        counter = 1
        while True:
            url = input(f"URL für Komponente {counter}: ")
            if not url:
                break
            
            component = {
                'url': url,
                'name': f"komponente{counter}",
                'description': input(f"Beschreibung für Komponente {counter}: ") or f"Komponente {counter}"
            }
            
            self.config['components'].append(component)
            counter += 1
            print()
    
    def get_security_settings(self):
        print("🔒 Sicherheitseinstellungen:")
        print("-" * 40)
        
        security = input("Sicherheitsprüfungen aktivieren? (j/n): ").lower()
        self.config['security_checks'] = security != 'n'
        
        if self.config['security_checks']:
            human = input("Human Verification (CAPTCHA) aktivieren? (j/n): ").lower()
            self.config['human_verification'] = human != 'n'
            
            antivirus = input("Antiviren-Warnung anzeigen? (j/n): ").lower()
            self.config['antivirus_warning'] = antivirus != 'n'
        
        background = input("Hintergrund-Downloads aktivieren? (j/n): ").lower()
        self.config['background_download'] = background != 'n'
        
        print()
    
    def generate_nsis_script(self):
        script_content = []
        
        # Header
        script_content.append('Unicode True')
        script_content.append('RequestExecutionLevel user')
        script_content.append(f'Name "{self.config["program_name"]}"')
        script_content.append(f'OutFile "{self.config["output_file"]}"')
        script_content.append(f'InstallDir {self.config["install_dir"]}')
        script_content.append('')
        
        # Includes
        script_content.append('!include LogicLib.nsh')
        script_content.append('!include nsDialogs.nsh')
        script_content.append('!include InetBgDL.nsh')
        if self.config['security_checks']:
            script_content.append('!include WinVer.nsh')
            script_content.append('!include x64.nsh')
        script_content.append('')
        
        # Variables
        script_content.append('Var DownloadHandle')
        script_content.append('Var DownloadURL')
        script_content.append('Var DownloadPath')
        if self.config['security_checks']:
            script_content.append('Var SecurityCheckPassed')
            script_content.append('Var IsHumanVerified')
            script_content.append('Var SandboxDetected')
        if self.config['antivirus_warning']:
            script_content.append('Var hInfoText')
            script_content.append('Var hWarningText')
        script_content.append('')
        
        # Pages
        pages = []
        if self.config['antivirus_warning']:
            pages.append('Page custom ShowDownloadWarning LeaveDownloadWarning')
        if self.config['security_checks']:
            pages.append('Page custom ShowSecurityCheck')
            if self.config['human_verification']:
                pages.append('Page custom ShowHumanVerification')
        pages.append('Page InstFiles')
        
        for page in pages:
            script_content.append(page)
        script_content.append('')
        
        # Security Check Function
        if self.config['security_checks']:
            script_content.append('Function CheckSecurityEnvironment')
            script_content.append('    StrCpy $SecurityCheckPassed 1')
            script_content.append('    StrCpy $SandboxDetected 0')
            script_content.append('    ')
            script_content.append('    ; Sandbox/VM Erkennung')
            script_content.append('    System::Call \'kernel32::GetModuleHandle(t "sbiedll.dll") i .r0\'')
            script_content.append('    ${If} $0 != 0')
            script_content.append('        StrCpy $SandboxDetected 1')
            script_content.append('        StrCpy $SecurityCheckPassed 0')
            script_content.append('    ${EndIf}')
            script_content.append('    ')
            script_content.append('    ; Debugger Erkennung')
            script_content.append('    System::Call \'kernel32::IsDebuggerPresent() i .r0\'')
            script_content.append('    ${If} $0 != 0')
            script_content.append('        StrCpy $SecurityCheckPassed 0')
            script_content.append('    ${EndIf}')
            script_content.append('    ')
            script_content.append('    ; RAM Prüfung')
            script_content.append('    System::Call \'kernel32::GlobalMemoryStatusEx(i) i.r0\'')
            script_content.append('    System::Call \'*$0(i, l, l, l, l, l, l, l, l .r1)\'')
            script_content.append('    ${If} $1 < 2000000000')
            script_content.append('        StrCpy $SandboxDetected 1')
            script_content.append('        StrCpy $SecurityCheckPassed 0')
            script_content.append('    ${EndIf}')
            script_content.append('FunctionEnd')
            script_content.append('')
        
        # Download Warning Page
        if self.config['antivirus_warning']:
            script_content.append('Function ShowDownloadWarning')
            script_content.append('    nsDialogs::Create 1018')
            script_content.append('    Pop $0')
            script_content.append('    ')
            script_content.append('    ${NSD_CreateLabel} 0 10 100% 20u "Wichtiger Hinweis vor der Installation"')
            script_content.append('    Pop $0')
            script_content.append('    SetCtlColors $0 "FF0000" "transparent"')
            script_content.append('    ')
            script_content.append('    ${NSD_CreateLabel} 0 40 100% 60u "Bitte deaktivieren Sie vorübergehend Ihre Antivirensoftware für eine reibungslose Installation."')
            script_content.append('    Pop $hWarningText')
            script_content.append('    ')
            script_content.append('    ${NSD_CreateButton} 25% 110 50% 30u "Fortfahren"')
            script_content.append('    Pop $0')
            script_content.append('    ${NSD_OnClick} $0 EnableDownloads')
            script_content.append('    ')
            script_content.append('    nsDialogs::Show')
            script_content.append('FunctionEnd')
            script_content.append('')
            
            script_content.append('Function EnableDownloads')
            script_content.append('    SendMessage $HWNDPARENT ${WM_COMMAND} 2 0')
            script_content.append('FunctionEnd')
            script_content.append('')
        
        # Main Section
        script_content.append('Section "Hauptprogramm" SecMain')
        script_content.append(f'    SetOutPath $INSTDIR')
        script_content.append(f'    File "{self.config["main_exe"]}"')
        script_content.append('    ')
        script_content.append('    WriteUninstaller "$INSTDIR\\Uninstall.exe"')
        script_content.append('    ')
        script_content.append(f'    Exec \'"$INSTDIR\\{self.config["main_exe"]}"\'')
        script_content.append('    ')
        script_content.append('    CreateDirectory "$INSTDIR\\komponenten"')
        script_content.append('SectionEnd')
        script_content.append('')
        
        # Components Section
        script_content.append('Section "Zusätzliche Komponenten" SecComponents')
        if self.config['security_checks']:
            script_content.append('    ${If} $SecurityCheckPassed != 1')
            if self.config['human_verification']:
                script_content.append('    ${OrIf} $IsHumanVerified != 1')
            script_content.append('        MessageBox MB_OK|MB_ICONSTOP "Sicherheitsvoraussetzungen nicht erfüllt"')
            script_content.append('        Abort')
            script_content.append('    ${EndIf}')
            script_content.append('    ')
        
        script_content.append('    InitPluginsDir')
        script_content.append('    ')
        
        for i, comp in enumerate(self.config['components'], 1):
            script_content.append(f'    ; {comp["description"]}')
            script_content.append(f'    StrCpy $DownloadURL "{comp["url"]}"')
            script_content.append(f'    StrCpy $DownloadPath "$PLUGINSDIR\\{comp["name"]}.zip"')
            script_content.append('    Call DownloadComponent')
            script_content.append('    ')
        
        script_content.append('    MessageBox MB_OK|MB_ICONINFORMATION "Komponenten erfolgreich heruntergeladen"')
        script_content.append('SectionEnd')
        script_content.append('')
        
        # Download Component Function
        script_content.append('Function DownloadComponent')
        script_content.append('    DetailPrint "Lade herunter: $DownloadURL"')
        script_content.append('    ')
        script_content.append('    Sleep 1000')
        script_content.append('    ')
        script_content.append('    inetbgdl::Download /POPUP "" /RESUME "Download fortsetzen" \')
        script_content.append('        $DownloadURL $DownloadPath $DownloadHandle')
        script_content.append('    ')
        script_content.append('    ${Do}')
        script_content.append('        inetbgdl::GetStats $DownloadHandle')
        script_content.append('        Pop $0')
        script_content.append('        ${If} $0 == "ready"')
        script_content.append('            ${Break}')
        script_content.append('        ${EndIf}')
        script_content.append('        ${If} $0 == "error"')
        script_content.append('            MessageBox MB_OK|MB_ICONWARNING "Download fehlgeschlagen"')
        script_content.append('            ${Break}')
        script_content.append('        ${EndIf}')
        script_content.append('        Sleep 500')
        script_content.append('    ${Loop}')
        script_content.append('    ')
        script_content.append('    ${If} ${FileExists} "$DownloadPath"')
        script_content.append('        nsisunz::Unzip "$DownloadPath" "$INSTDIR\\komponenten"')
        script_content.append('        Delete "$DownloadPath"')
        script_content.append('    ${EndIf}')
        script_content.append('FunctionEnd')
        script_content.append('')
        
        # Uninstall Section
        script_content.append('Section "Uninstall"')
        script_content.append(f'    ExecWait \'"$INSTDIR\\{self.config["main_exe"]}" /quit\'')
        script_content.append('    Sleep 2000')
        script_content.append('    ')
        script_content.append(f'    Delete "$INSTDIR\\{self.config["main_exe"]}"')
        script_content.append('    Delete "$INSTDIR\\Uninstall.exe"')
        script_content.append('    RMDir /r "$INSTDIR\\komponenten"')
        script_content.append('    RMDir "$INSTDIR"')
        script_content.append('SectionEnd')
        script_content.append('')
        
        # Init Function
        script_content.append('Function .onInit')
        script_content.append('    SectionSetFlags ${SecMain} 1')
        script_content.append('    SectionSetFlags ${SecComponents} 1')
        script_content.append('    ')
        if self.config['security_checks']:
            script_content.append('    StrCpy $SecurityCheckPassed 0')
            script_content.append('    StrCpy $IsHumanVerified 0')
            script_content.append('    StrCpy $SandboxDetected 0')
            script_content.append('    ')
            script_content.append('    Call CheckSecurityEnvironment')
        script_content.append('FunctionEnd')
        script_content.append('')
        
        # Success Function
        script_content.append('Function .onInstSuccess')
        script_content.append('    MessageBox MB_YESNO|MB_ICONQUESTION "Installation abgeschlossen.\\n\\nAntivirensoftware jetzt wieder aktivieren?" IDNO end')
        script_content.append('    ExecShell "open" "control.exe /name Microsoft.WindowsSecurity"')
        script_content.append('    end:')
        script_content.append('FunctionEnd')
        script_content.append('')
        
        return '\n'.join(script_content)
    
    def save_config(self):
        config_file = 'nsis_config.json'
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        print(f"✅ Konfiguration gespeichert: {config_file}")
    
    def load_config(self):
        config_file = 'nsis_config.json'
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                print(f"✅ Konfiguration geladen: {config_file}")
                return True
            except:
                print("❌ Fehler beim Laden der Konfiguration")
        return False
    
    def run(self):
        self.print_header()
        
        # Config laden falls vorhanden
        if self.load_config():
            use_saved = input("Gespeicherte Konfiguration verwenden? (j/n): ").lower()
            if use_saved != 'j':
                self.config = {
                    'program_name': 'MeinProgramm',
                    'output_file': 'MeinProgramm-Installer.exe',
                    'main_exe': 'hauptprogramm.exe',
                    'install_dir': '$LOCALAPPDATA\\MeinProgramm',
                    'components': [],
                    'security_checks': True,
                    'human_verification': True,
                    'background_download': True,
                    'antivirus_warning': True
                }
        
        self.get_basic_info()
        self.get_components()
        self.get_security_settings()
        
        # Script generieren
        nsis_script = self.generate_nsis_script()
        output_file = 'generated_installer.nsi'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(nsis_script)
        
        # Config speichern
        self.save_config()
        
        print("✅ NSIS Script erfolgreich generiert!")
        print(f"📄 Datei: {output_file}")
        print()
        print("🔧 Nächste Schritte:")
        print("1. NSIS Compiler installieren (https://nsis.sourceforge.io/Download)")
        print("2. Benötigte Plugins installieren:")
        print("   - InetBgDL")
        print("   - nsisunz")
        print("3. Script kompilieren:")
        print(f"   makensis {output_file}")
        print()
        print("⚠️  Wichtige Hinweise:")
        print("- Stellen Sie sicher, dass alle URLs erreichbar sind")
        print("- Testen Sie den Installer in verschiedenen Umgebungen")
        print("- Informieren Sie Benutzer über die Sicherheitsprüfungen")

def main():
    generator = NSISScriptGenerator()
    generator.run()

if __name__ == "__main__":
    main()