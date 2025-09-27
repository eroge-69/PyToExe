@echo off
title BonziMortal - Caos Total

:: Mensagem inicial do Bonzi
echo Foi avisado! > "%temp%\BonziWarning.txt"
start notepad "%temp%\BonziWarning.txt"

:: Verifica se está rodando como administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Reiniciando como administrador...
    powershell -Command "Start-Process '%~f0' -Verb runAs"
    exit
)

:: Primeiro aviso
echo ==========================================================
echo AVISO: Este arquivo pode alterar o PC, abrir varias janelas e tocar sons.
echo Digite "1" para continuar.
set /p escolha=
if not "%escolha%"=="1" exit

start "" "%~dp0assets\Bonzi_alert1.mp3"

:: Segundo aviso
echo ==========================================================
echo CONFIRMACAO: Tem certeza? Digite "1" novamente.
set /p escolha2=
if not "%escolha2%"=="1" exit

start "" "%~dp0assets\Bonzi_alert2.mp3"

:: Terceiro aviso detalhado
echo ==========================================================
echo ATENCAO FINAL: Este "virus" faz o seguinte:
echo - Abre varias janelas (notepad, calc, mspaint, cmd, explorer)
echo - Toca sons simultaneos do Bonzi
echo - Abre 2 pop-ups com imagens do Bonzi
echo - Alterna o papel de parede entre duas imagens do Bonzi 10 vezes
echo - Toca o vídeo final
echo Digite "1" para aceitar e iniciar.
set /p escolha3=
if not "%escolha3%"=="1" exit

start "" "%~dp0assets\Bonzi_laugh.mp3"

echo Iniciando Bonzi Mortal em 3 segundos...
timeout /t 3 >nul

for /l %%i in (1,1,10) do (
    reg add "HKCU\Control Panel\Desktop" /v Wallpaper /t REG_SZ /d "%~dp0assets\Bonzi_epic1.jpg" /f >nul 2>&1
    RUNDLL32.EXE user32.dll,UpdatePerUserSystemParameters >nul 2>&1
    timeout /t 1 >nul
    reg add "HKCU\Control Panel\Desktop" /v Wallpaper /t REG_SZ /d "%~dp0assets\Bonzi_epic2.jpg" /f >nul 2>&1
    RUNDLL32.EXE user32.dll,UpdatePerUserSystemParameters >nul 2>&1
    timeout /t 1 >nul

    start notepad
    start calc
    start mspaint
    start cmd
    start explorer

    start "" "%~dp0assets\Bonzi_popup1.jpg"
    start "" "%~dp0assets\Bonzi_popup2.jpg"
)

start "" "%~dp0assets\Bonzi_epic.mp4"

echo Bonzi dominou seu PC! > "%temp%\BonziFinal.txt"
start notepad "%temp%\BonziFinal.txt"

pause