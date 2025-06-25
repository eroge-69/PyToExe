@echo off
setlocal enabledelayedexpansion

:START
cls
color 0F
echo ===============================
echo     CONVERTOR PLAIN ? ELITE
echo ===============================
echo.
echo Scrie 'exit' pentru a iesi oricand.
echo.

:INPUT
set /p plain=Introdu numarul de Plain: 

if /i "%plain%"=="exit" goto END

rem Verificare daca input-ul e numeric
for /f "delims=0123456789" %%a in ("%plain%") do (
    color 0C
    echo Eroare: Te rog sa introduci un numar valid!
    timeout /t 2 >nul
    color 0F
    goto INPUT
)

rem Calcule
set /a simple=plain / 4
set /a plain_rest=plain %% 4

set /a rare=simple / 4
set /a simple_rest=simple %% 4

set /a elite=rare / 4
set /a rare_rest=rare %% 4

color 0A
echo.
echo Rezultat:
echo  Elite: !elite!
echo  Rare: !rare_rest!
echo  Simple: !simple_rest!
echo  Plain ramase: !plain_rest!
echo.

color 0F
set /p choice=Vrei sa faci alta conversie? (d/n): 
if /i "%choice%"=="d" goto START

:END
echo Multumim pentru utilizare!
timeout /t 2 >nul
exit
