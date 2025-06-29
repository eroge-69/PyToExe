#!/usr/bin/env python3

# The actual Hotel Reservation application. It requires setup before use.

# "If you're using global statements, you're doing something evil, hiding the fact that your code needs parameters, bloatful. It also won't work."

# TODOs

# NOTICE, TODO, WARNING, CODE, META: The usage of such variables for label and text was bad and needs to be changed in further releases. It is more overhead, harder-to-maintain and harder-to-debug. REPLACE ASAP.
# TODO: Import the person filler value from setup or manually define it for easier code
# TODO: Make this code have many versions. They should be better. Not limited to 18 rooms, customizable, free, beautiful etc. etc. etc.
# TODO: Add well-documented doctypes
# TODO: Make code slightly less fragile by implementing more advanced versions that allow CSV modifications of fields and rows (easy but not viable as of now since this version should be easy and specific)

# BUG: This program has a bug (more of a feature, no?) that nothing happens to the GUI nor the console after each bug. This is a "error-handling" feature.

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import Calendar

from datetime import datetime
from pyautogui import size
import pandas as pd
import setup
import tkinter.font as tkfont

# Variables

fillerValue = setup.fillerValue
baseCSVDatabase = setup.csvDatabasePath

windowBackgroundColor = "#F3F4F6" # Modern light background for better cross-platform look
buttonBackgroundColor = "#1976D2" # Accent blue for buttons
buttonForegroundColor = "#000000" # White button text
pureBlack = "#000000" # Deep gray-black for text

windowTitle = "Aplikacioni i Rezervimeve të Hotelit"
setRecordsWindowTitle = "Vendosni Rekordet"

setRecordsButton = "Vendosni Rekordet në Databazë"
showAllRoomsButton = "Të Gjitha Dhomat"
showAllTakenRoomsButton = "Dhomat e Zëna"
showAllNonTakenRoomsButton = "Dhomat e Lira"
searchRoomNumberLabel = "Kërko Numrin e Dhomës"
searchRoomNumberColumn, searchRoomNumberColumn2, searchRoomNumberColumn3, searchRoomNumberColumn4 = "Numri i Dhomës", "E zënë", "Datat e Rezervimit", "Njerëzit"

# SET RECORDS
chosenRoomNumberLabelText = "Numri i Dhomës: "
isRoomNumberTakenLabelText = "E zënë: "
roomNumberTakenDatesLabelText = "Datat e Rezervimit: "
peopleLabelText = "Njerëzit: "
submitButtonText = "Regjistroni të Dhënat"

maximumWindowSize = f"{size()[0]}x{size()[1]}"

# Functions

def datetimeCheck(): # Checks and calculates the datetime of the third (takendates) field of the CSV file to do automatic and very precise datetime checking (every minute)
    global baseCSVDatabase, fillerValue, window         
    baseCSVDatabaseDF = pd.read_csv(baseCSVDatabase)
    for index, row in baseCSVDatabaseDF.iterrows():
        if row["taken"] == fillerValue or row["takendates"] == fillerValue or row["people"] == fillerValue:
            pass
        else:
            try:
                endingDateStr = row["takendates"].split("-")[1]
                endingDate = datetime.strptime(endingDateStr, "%m/%d/%Y")
                if datetime.today() > endingDate:
                    baseCSVDatabaseDF.at[index, "taken"] = fillerValue
                    baseCSVDatabaseDF.at[index, "takendates"] = fillerValue
                    baseCSVDatabaseDF.at[index, "people"] = 0
            except Exception as e:
                messagebox.showerror("Problem", e)
    try:
        baseCSVDatabaseDF.to_csv(baseCSVDatabase, index=False)
    except PermissionError:
        messagebox.showerror("Leje e Gabuar", "Ju nuk keni privilegjet e sakta që t'i shkruani dokumentit. Gjithmonë përdoreni programin me privilegje administrative!")
    except FileNotFoundError:
        messagebox.showerror("Dokumenti Nuk Gjendet", "Ky aplikacion është modifikuar ose dokumentet kanë ikur. Fshini të gjitha dokumentet e programit dhe rihapeni aplikacionin e pamodifikuar.")
    except OSError:
        messagebox.showerror("Problem i Sistemit Operativ", "Sistemi operativ ka një problem fatal për shkrimin e dokumenteve ose manaxhimin e tyre.")
    except ValueError: 
        messagebox.showerror("Problemi i Vlerave", "Ky aplikacion ose informacioni është modifikuar ose dëmtuar në mënyrë fatale.")
    except Exception as e:
        messagebox.showerror("Problem", e)
    window.after(60000, datetimeCheck)

def validateSearch(roomNumber):
    if isinstance(roomNumber, str):
        try:
            int(roomNumber)
            if int(roomNumber) >= 101 and int(roomNumber) <= 106:
                return True
            elif int(roomNumber) >= 201 and int(roomNumber) <= 206:
                return True
            elif int(roomNumber) >= 301 and int(roomNumber) <= 306:
                return True
            else:
                messagebox.showerror("Limiti i Numrit të Dhomës", f"Numri i dhomës është i restriktuar nga limiti i dhomave në distrikt. Nëse ka problem, përdorni një version të palimituar të aplikacionit ose kontaktoni pronarin e programit.")
                return False
        except ValueError:
            messagebox.showerror("Vlerë e Keqe", f"{roomNumber} nuk është numër me bazë 10")
            return False
        except Exception as e:
            messagebox.showerror("Problem", e)
            return False

def search(roomNumber): 
    global baseCSVDatabase, fillerValue, searchRoomNumberTreeview
    baseCSVDatabaseDF = pd.read_csv(baseCSVDatabase)
    for row in searchRoomNumberTreeview.get_children():
        searchRoomNumberTreeview.delete(row)
    if validateSearch(roomNumber) != True:
        return None
    for index, row in baseCSVDatabaseDF.iterrows():
        if int(row.iloc[0]) == int(roomNumber):
            rows = list(row)
            rows[0] = int(rows[0])
            if rows[1] == fillerValue:
                searchRoomNumberTreeview.insert("", "end", values=rows, tags=("nontaken"))
                messagebox.showinfo("Sukses", "Kërkimi i numrit të dhomës u krye me sukses")
            else:
                searchRoomNumberTreeview.insert("", "end", values=rows, tags=("taken"))
                messagebox.showinfo("Sukses", "Kërkimi i numrit të dhomës u krye me sukses")

def submit(chosenRoom, isTaken, startTakenDate, endTakenDate, people):
    global baseCSVDatabase, fillerValue
    baseCSVDatabaseDFCopy = pd.read_csv(baseCSVDatabase)
    if chosenRoom == "":
        messagebox.showerror("Dhomë e paspecifikuar", "Dhoma nuk është zgjedhur nga lista")
        return None
    if isTaken == "":
        messagebox.showerror("E zënë apo jo?", "Nuk është zgjedhur status-i i dhomës nga lista. Nuk dihet nëse dhoma është e zënë apo jo.")
        return None
    if not isTaken == fillerValue:
        try:
            int(people)
        except ValueError:
            messagebox.showerror("Vlerë e Gabuar", "Numri i njerëzve duhet të jetë bazë 10 dhe nuk duhet të jetë e paspecifikuar.")
            return None
        except Exception as e:
            messagebox.showerror("Problem", e)
            return None
        baseCSVDatabaseDFCopy.loc[baseCSVDatabaseDFCopy["room"] == int(chosenRoom)] = [int(chosenRoom), isTaken, f"{startTakenDate}-{endTakenDate}", int(people)]
        if not int(people) <= 0:
            baseCSVDatabaseDFCopy.to_csv(baseCSVDatabase, index=False)
        else:
            messagebox.showerror("Problem Logjike", "Dhomat e zëna nuk mund të kenë 0 ose një numër negativ personash. Nuk ka kuptim.")
    else:
        baseCSVDatabaseDFCopy.loc[baseCSVDatabaseDFCopy["room"] == int(chosenRoom)] = [int(chosenRoom), fillerValue, fillerValue, 0]
        baseCSVDatabaseDFCopy.to_csv(baseCSVDatabase, index=False)
        messagebox.showinfo("Sukses", f"Numri i Dhomës: {chosenRoom}, {isTaken}")

def setRecords():
    global setRecordsWindowTitle, windowBackgroundColor, buttonBackgroundColor, buttonForegroundColor, pureBlack, chosenRoomNumberLabelText, baseCSVDatabase, fillerValue, roomNumberTakenDatesLabelText, peopleLabelText, submitButtonText

    setRecordsWindow = tk.Toplevel()
    setRecordsWindow.title(setRecordsWindowTitle)
    setRecordsWindow.configure(background=windowBackgroundColor)

    default_font = tkfont.nametofont("TkDefaultFont")
    default_font.configure(size=11, family="Segoe UI")
    setRecordsWindow.option_add("*Font", default_font)

    sfrm = ttk.Frame(setRecordsWindow, padding=20)
    sfrm.pack(expand=True, fill=tk.BOTH)

    ttk.Label(sfrm, text=chosenRoomNumberLabelText, foreground=pureBlack).pack(anchor="w", pady=(0, 4))
    chosenRoomNumberDropdown = ttk.Combobox(
        sfrm,
        state="readonly",
        values=[str(row.iloc[0]) for index, row in pd.read_csv(baseCSVDatabase).iterrows()],
        width=20
    )
    chosenRoomNumberDropdown.pack(fill=tk.X, pady=(0, 10))

    ttk.Label(sfrm, text=isRoomNumberTakenLabelText, foreground=pureBlack).pack(anchor="w", pady=(0, 4))
    isRoomNumberTakenDropdown = ttk.Combobox(
        sfrm,
        state="readonly",
        values=[fillerValue, "E zënë"],
        width=20
    )
    isRoomNumberTakenDropdown.pack(fill=tk.X, pady=(0, 10))

    ttk.Label(sfrm, text=roomNumberTakenDatesLabelText, foreground=pureBlack).pack(anchor="w", pady=(0, 4))
    datesFrame = ttk.Frame(sfrm)
    datesFrame.pack(fill=tk.X, pady=(0, 10))
    roomNumberTakenDatesCalendarStart = Calendar(datesFrame, date_pattern="mm/dd/yyyy")
    roomNumberTakenDatesCalendarStart.pack(side=tk.LEFT, padx=(0, 8))
    roomNumberTakenDatesCalendarEnd = Calendar(datesFrame, date_pattern="mm/dd/yyyy")
    roomNumberTakenDatesCalendarEnd.pack(side=tk.LEFT)

    ttk.Label(sfrm, text=peopleLabelText, foreground=pureBlack).pack(anchor="w", pady=(0, 4))
    peopleEntry = ttk.Entry(sfrm)
    peopleEntry.pack(fill=tk.X, pady=(0, 16))

    def close_and_submit():
        submit(
            chosenRoomNumberDropdown.get(),
            isRoomNumberTakenDropdown.get(),
            roomNumberTakenDatesCalendarStart.get_date(),
            roomNumberTakenDatesCalendarEnd.get_date(),
            peopleEntry.get()
        )
        setRecordsWindow.destroy()

    ttk.Button(
        sfrm,
        text=submitButtonText,
        style="Accent.TButton",
        command=close_and_submit
    ).pack(pady=(4, 0), ipadx=10, ipady=4)

def showAllRooms():
    global baseCSVDatabase, searchRoomNumberTreeview, fillerValue
    baseCSVDatabaseDF = pd.read_csv(baseCSVDatabase)
    for row in searchRoomNumberTreeview.get_children():
        searchRoomNumberTreeview.delete(row)
    for index, row in baseCSVDatabaseDF.iterrows():
        rows = list(row)
        rows[0] = int(rows[0])
        if rows[1] == fillerValue:
            searchRoomNumberTreeview.insert("", "end", values=rows, tags=("nontaken"))
        else:
            searchRoomNumberTreeview.insert("", "end", values=rows, tags=("taken"))
    messagebox.showinfo("Sukses", "Të gjitha dhomat janë treguar")

def showAllTakenRooms():
    global baseCSVDatabase, searchRoomNumberTreeview, fillerValue
    baseCSVDatabaseDF = pd.read_csv(baseCSVDatabase)
    for row in searchRoomNumberTreeview.get_children():
        searchRoomNumberTreeview.delete(row)
    for index, row in baseCSVDatabaseDF.iterrows():
        row = list(row)
        row[0] = int(row[0])
        if row[1] == fillerValue:
            pass
        else:
            searchRoomNumberTreeview.insert("", "end", values=row, tags=("taken",))
    messagebox.showinfo("Sukses", "Të gjitha dhomat e zëna janë treguar")

def showAllNonTakenRooms():
    global baseCSVDatabase, searchRoomNumberTreeview, fillerValue
    baseCSVDatabaseDF = pd.read_csv(baseCSVDatabase)
    for row in searchRoomNumberTreeview.get_children():
        searchRoomNumberTreeview.delete(row)
    for index, row in baseCSVDatabaseDF.iterrows():
        row = list(row)
        row[0] = int(row[0])
        if row[1] == fillerValue:
            searchRoomNumberTreeview.insert("", "end", values=row, tags=("nontaken",))
    messagebox.showinfo("Sukses", "Të gjitha dhomat e lira janë treguar")

def main():
    global window, windowBackgroundColor, buttonBackgroundColor, buttonForegroundColor, pureBlack, windowTitle, showAllRoomsButton, showAllTakenRoomsButton, showAllNonTakenRoomsButton, searchRoomNumberLabel, maximumWindowSize, searchRoomNumberColumn, searchRoomNumberColumn2, searchRoomNumberColumn3, searchRoomNumberColumn4, setRecords, searchRoomNumberTreeview, style

    window = tk.Tk()
    window.title(windowTitle)
    window.geometry(maximumWindowSize)
    window.configure(bg=windowBackgroundColor)
    
    style = ttk.Style(window)
    if "vista" in style.theme_names(): # If the Windows theme is there...
        style.theme_use("vista") # Use it!
    else: # If not...
        style.theme_use("clam") # Use clam, a simple but amazing theme.

    default_font = tkfont.nametofont("TkDefaultFont")
    default_font.configure(size=11, family="Segoe UI")
    window.option_add("*Font", default_font)

    style.configure("Accent.TButton",
        foreground=buttonForegroundColor, background=buttonBackgroundColor, font=('Segoe UI', 11, 'bold'),
        borderwidth=0, focusthickness=1, focuscolor=buttonBackgroundColor)
    style.map("Accent.TButton",
        background=[('active', '#1565C0'), ('pressed', '#1565C0')],
        foreground=[('disabled', '#ccc')])

    frm = ttk.Frame(window, padding=32)
    frm.pack(expand=True, fill=tk.BOTH)

    btnrow = ttk.Frame(frm)
    btnrow.pack(fill=tk.X, pady=(0, 12))
    ttk.Button(btnrow, text=setRecordsButton, style="Accent.TButton", command=setRecords).pack(side=tk.LEFT, padx=4)
    ttk.Button(btnrow, text=showAllRoomsButton, style="Accent.TButton", command=showAllRooms).pack(side=tk.LEFT, padx=4)
    ttk.Button(btnrow, text=showAllTakenRoomsButton, style="Accent.TButton", command=showAllTakenRooms).pack(side=tk.LEFT, padx=4)
    ttk.Button(btnrow, text=showAllNonTakenRoomsButton, style="Accent.TButton", command=showAllNonTakenRooms).pack(side=tk.LEFT, padx=4)

    ttk.Label(frm, text=searchRoomNumberLabel, font=("Segoe UI", 14, "bold"), foreground=pureBlack).pack(pady=(0, 8))
    searchFrame = ttk.Frame(frm)
    searchFrame.pack(fill=tk.X, pady=(0, 12))
    searchRoomNumberInput = ttk.Entry(searchFrame, width=16)
    searchRoomNumberInput.pack(side=tk.LEFT, padx=(0, 10))
    ttk.Button(searchFrame, text="Kërkoni", style="Accent.TButton",
        command=lambda: search(searchRoomNumberInput.get())).pack(side=tk.LEFT)

    treeFrame = ttk.Frame(frm)
    treeFrame.pack(expand=True, fill=tk.BOTH)
    searchRoomNumberTreeview = ttk.Treeview(
        treeFrame,
        columns=(searchRoomNumberColumn, searchRoomNumberColumn2, searchRoomNumberColumn3, searchRoomNumberColumn4),
        show="headings",
        height=20
    )
    searchRoomNumberTreeview.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)

    for col in (searchRoomNumberColumn, searchRoomNumberColumn2, searchRoomNumberColumn3, searchRoomNumberColumn4):
        searchRoomNumberTreeview.heading(col, text=col)
        searchRoomNumberTreeview.column(col, anchor=tk.CENTER, width=120)

    style.map("Treeview", background=[("selected", "#1976D2")])
    searchRoomNumberTreeview.tag_configure("taken", background="#FFCDD2")
    searchRoomNumberTreeview.tag_configure("nontaken", background="#C8E6C9")

    treeScroll = ttk.Scrollbar(treeFrame, orient="vertical", command=searchRoomNumberTreeview.yview)
    searchRoomNumberTreeview.configure(yscroll=treeScroll.set)
    treeScroll.pack(side=tk.RIGHT, fill=tk.Y)

    window.bind("<F11>", lambda event: window.attributes("-fullscreen", True))
    window.bind("<Escape>", lambda event: window.attributes("-fullscreen", False))

    datetimeCheck()

    window.mainloop()

if __name__ == "__main__":
    setup.setup()
    main()
else:
    pass
