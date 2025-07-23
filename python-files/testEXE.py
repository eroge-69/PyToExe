import win32com.client
import os
import pythoncom
 
output = []
 
try:
    pythoncom.CoInitialize()  # Inicializa COM
 
    session = win32com.client.Dispatch("Microsoft.Update.Session")
    searcher = session.CreateUpdateSearcher()
    results = searcher.Search("IsInstalled=0 and IsHidden=0 and Type='Software'")
 
    if results.Updates.Count == 0:
        output.append("[OK] No hay actualizaciones pendientes.")
    else:
        output.append("[INFO] Actualizaciones pendientes en Windows Update:")
        for i in range(results.Updates.Count):
            update = results.Updates.Item(i)
            output.append(f"[UPDATE] {update.Title}")
 
    os.makedirs(r"C:\Temp", exist_ok=True)
    with open(r"C:\Temp\update_results.txt", "w", encoding="utf-8") as f:
        for line in output:
            f.write(line + "\n")
 
    pythoncom.CoUninitialize()  # Libera COM
 
except Exception as e:
    with open(r"C:\Temp\update_results.txt", "w", encoding="utf-8") as f:
        f.write(f"[ERROR] {str(e)}\n")