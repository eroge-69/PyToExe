import subprocess

# Uruchamia PowerShell, wykonuje polecenie instalacji i symuluje wpisanie "Y"
process = subprocess.Popen(
    'powershell -Command "irm https://beatrun.jonnybro.ru/install | iex; exit"',
    shell=True,
    stdin=subprocess.PIPE
)

# Wysyła literę "Y" jako odpowiedź na pytanie
process.communicate(input=b'Y\n')
