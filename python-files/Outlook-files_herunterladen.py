import os
import win32com.client
import datetime

dt = datetime.datetime.now()

if dt.minute > 5:
    dt = dt.replace(minute=dt.minute - 5)
else:
    dt = dt.replace(hour=dt.hour - 1, minute=55)



speicherort = os.path.join("Outlook Dokumente")

outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")

ordner = outlook.GetDefaultFolder(6)

emails = ordner.Items
emails.Sort("[ReceivedTime]", True)

for i, mail in enumerate(emails):
    mailtime = mail.ReceivedTime
    if(mailtime < dt):
        break
    
    if mail.Attachments.Count > 0:
        for anhang in mail.Attachments:
            dateiname = f"{i}_{anhang.FileName}"
            dateipfad = os.path.join(speicherort, dateiname)
            anhang.SaveAsFile(dateipfad)
            print(f"Gespeichert: {anhang.FileName}")

print("Fertig.")
