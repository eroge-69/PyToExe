
@echo off
setlocal enabledelayedexpansion

:: Set folder path
set "folder=S:\LoadControlScanner"
set "date=19SEP25"

:: Loop through PDF files
for %%F in ("%folder%\*.pdf") do (
    echo Processing %%~nxF

    :: Use OCR to extract flight number and handler name (requires Python OCR script)
    python extract_flight_handler.py "%%F" > temp_info.txt

    set /p info=<temp_info.txt

    :: Split info into flight and handler
    for /f "tokens=1,2 delims=," %%a in ("!info!") do (
        set "flight=%%a"
        set "handler=%%b"
    )

    :: Check if valid info was found
    if not "!flight!"=="UNKNOWN" if not "!handler!"=="UNKNOWN" (
        set "newname=!flight! !date! !handler!.pdf"
        ren "%%F" "!newname!"
        echo Renamed to !newname!
    ) else (
        echo Skipped %%~nxF (not a trip file)
    )
)

:: Cleanup
if exist temp_info.txt del temp_info.txt

endlocal
