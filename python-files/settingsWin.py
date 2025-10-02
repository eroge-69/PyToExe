import os
import subprocess
import time

def run_powershell_command(command):
    """Выполняет PowerShell команду"""
    try:
        result = subprocess.run(
            ["powershell", "-Command", command], 
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Ошибка выполнения PowerShell команды: {e}")
        return None

def unpin_taskbar_elements():
    """Открепляет элементы с панели задач"""
    print("Открепляю элементы с панели задач...")
    
    # PowerShell команды для открепления элементов
    commands = [
        # Открепление магазина Windows
        '$app = Get-StartApps "Microsoft Store" | Select-Object -ExpandProperty AppID; ((New-Object -Com Shell.Application).NameSpace("shell:::{4234d49b-0245-4df3-b780-3893943456e1}").Items() | Where-Object {$_.Path -like "*WindowsStore*"}).Verbs() | Where-Object {$_.Name -replace "&", "" -match "Unpin from taskbar"} | ForEach-Object {$_.DoIt()}',
        
        # Открепление поиска (оставляем значок, просто открепляем если закреплен)
        'try { ((New-Object -Com Shell.Application).NameSpace("shell:::{4234d49b-0245-4df3-b780-3893943456e1}").Items() | Where-Object {$_.Name -eq "Search"}).Verbs() | Where-Object {$_.Name -replace "&", "" -match "Unpin from taskbar"} | ForEach-Object {$_.DoIt()} } catch { Write-Host "Search already unpinned" }',
        
        # Открепление представления задач (Cortana/Widgets)
        'try { ((New-Object -Com Shell.Application).NameSpace("shell:::{4234d49b-0245-4df3-b780-3893943456e1}").Items() | Where-Object {$_.Name -eq "Task View"}).Verbs() | Where-Object {$_.Name -replace "&", "" -match "Unpin from taskbar"} | ForEach-Object {$_.DoIt()} } catch { Write-Host "Task View already unpinned" }'
    ]
    
    for cmd in commands:
        run_powershell_command(cmd)
        time.sleep(1)
    
    print("Элементы откреплены с панели задач")

def open_windows_update():
    """Открывает настройки обновления Windows"""
    print("Открываю обновления Windows...")
    subprocess.Popen("ms-settings:windowsupdate")
    time.sleep(2)

def open_network_settings():
    """Открывает сетевые настройки"""
    print("Открываю сетевые настройки...")
    subprocess.Popen("ms-settings:network")
    time.sleep(2)

def disable_sticky_keys():
    """Отключает залипание клавиш"""
    print("Отключаю залипание клавиш...")
    
    # Команды для отключения залипания клавиш через реестр
    commands = [
        'Set-ItemProperty -Path "HKCU:\\Control Panel\\Accessibility\\StickyKeys" -Name "Flags" -Value "506"',
        'Set-ItemProperty -Path "HKCU:\\Control Panel\\Accessibility\\Keyboard Response" -Name "Flags" -Value "122"',
        'Set-ItemProperty -Path "HKCU:\\Control Panel\\Accessibility\\ToggleKeys" -Name "Flags" -Value "58"'
    ]
    
    for cmd in commands:
        run_powershell_command(cmd)
    
    print("Залипание клавиш отключено")

def main():
    """Основная функция"""
    print("Запуск скрипта настройки Windows...")
    
    # 1. Открепляем элементы с панели задач
    unpin_taskbar_elements()
    time.sleep(2)
    
    # 2. Открываем обновления Windows
    open_windows_update()
    time.sleep(2)
    
    # 3. Открываем сетевые настройки
    open_network_settings()
    time.sleep(2)
    
    # 4. Отключаем залипание клавиш
    disable_sticky_keys()
    
    print("\nВсе операции завершены!")
    print("Панель задач: Магазин, Поиск и Представление задач откреплены")
    print("Открыты окна: Обновления Windows и Сетевые настройки")
    print("Залипание клавиш отключено")

if __name__ == "__main__":
    main()