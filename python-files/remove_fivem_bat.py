REM هذا ملف Batch ينظف جهازك من كل بقايا FiveM وملفات الحساب (CitizenFX + DigitalEntitlements)

@echo off

echo اغلاق FiveM في حال كان شغال...
taskkill /F /IM FiveM.exe >nul 2>&1

REM حذف مجلد FiveM من LocalAppData
echo حذف: %localappdata%\FiveM
rd /s /q "%localappdata%\FiveM"

REM حذف مجلد CitizenFX من Roaming
echo حذف: %appdata%\CitizenFX
rd /s /q "%appdata%\CitizenFX"

REM حذف مجلد DigitalEntitlements (ملف الحساب)
echo حذف: %localappdata%\DigitalEntitlements
rd /s /q "%localappdata%\DigitalEntitlements"

REM حذف FiveM من Program Files
echo حذف: C:\Program Files\FiveM
rd /s /q "C:\Program Files\FiveM"

echo حذف: C:\Program Files (x86)\FiveM
rd /s /q "C:\Program Files (x86)\FiveM"

REM حذف Rockstar Games cache (اختياري)
echo حذف: %localappdata%\Rockstar Games
rd /s /q "%localappdata%\Rockstar Games"

echo حذف: %appdata%\Rockstar Games
rd /s /q "%appdata%\Rockstar Games"

echo ---
echo ✅ تم مسح كل بقايا FiveM وملفات الحساب.
echo الرجاء اعادة تشغيل الكمبيوتر قبل تثبيت FiveM من جديد.
pause
