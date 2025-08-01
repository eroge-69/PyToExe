import os
import sys
import tkinter as tk
import tkinter.ttk as ttk
import tkinter
from tkinter import *

from tkinter import Tk
from datetime import datetime, date
import time
import datetime
from tkcalendar import DateEntry
import sqlite3
import tkinter.messagebox as tkMessageBox
from xlsxwriter.workbook import Workbook
import os
import pandas as pd
import logging
#from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import openpyxl
#import psutil
from openpyxl import Workbook
import time
import xlrd
import imaplib
import email
#--------------------------------------------PROG MAIL ---------------------------------------------


df = pd.DataFrame()  # Empty dataframe as placeholder
cleaned_filepath = None  # Placeholder for global scope


# Email configuration
EMAIL = 'algojah@airalgerie.dz'
PASSWORD = 'InSP@Esc2025 '
IMAP_SERVER = 'mail.airalgerie.dz'
try:
    cleaned_filepath = None  # Initialize at t
except:
    print('cante share globakle variable cleaned filepath')
    pass


def convert_xls_to_xlsx(xls_filepath):
    # Open the .xls file
    xl_workbook = xlrd.open_workbook(xls_filepath)
    xlsx_filepath = xls_filepath.replace('.xls', '.xlsx')
    
    # Create a new workbook and copy the content
    wb = Workbook()
    sheet = wb.active
    for sheet_index in range(xl_workbook.nsheets):
        xl_sheet = xl_workbook.sheet_by_index(sheet_index)
        for row in range(xl_sheet.nrows):
            for col in range(xl_sheet.ncols):
                sheet.cell(row=row+1, column=col+1).value = xl_sheet.cell_value(row, col)
    
    # Save the new workbook as .xlsx
    wb.save(xlsx_filepath)

    return xlsx_filepath



def clean_excel_file(xlsx_filepath):
    global df
    
    global cleaned_filepath
    # Read the .xlsx file with pandas
    df = pd.read_excel(xlsx_filepath)

    # Drop all empty rows and columns
    df.dropna(how='all', inplace=True)  # Drop rows where all values are NaN
    df.dropna(axis=1, how='all', inplace=True)  # Drop columns where all values are NaN

    # Assuming headers are in the first row, reset index to remove unnecessary header rows
    df.columns = df.iloc[1]  # Set the first row as column headers
    df = df[2:]  # Remove the first row (now it's the header)

    # Reset the index to ensure the rows are numbered sequentially
    df.reset_index(drop=True, inplace=True)

    # Drop specific rows
    df.drop([0, 1], inplace=True)  # Drop row 1 and row 2
    df.drop(df.index[-1], inplace=True)  # Drop the last row

    # Keep only the required columns
    required_columns = ['DATE', 'FLT', 'TYPE', 'REG', 'AC', 'DEP', 'ARR', 'STD', 'STA', 'ATD', 'ATA']
    df = df[required_columns]

    # Filter the rows where TYPE starts with "A" (except ATR)
    df = df[df['AC'].str.startswith('A') & ~df['AC'].str.startswith('AT')&~df['AC'].str.contains('A320', na=False)]
    
    # Add "AH" before every flight number in the 'FLT' column
    df['FLT'] = 'AH' + df['FLT'].astype(str)
    
    # Save the cleaned file

    cleaned_filepath = xlsx_filepath.replace('.xlsx', '_cleaned.xlsx')
    df.to_excel(cleaned_filepath, index=False)
    
    return cleaned_filepath, df


def process_flight_data():



    # Connect to email server   
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select('inbox')

    # Search for target emails
    status, messages = mail.search(None, '(FROM "ecrew.dp@airalgerie.dz")')
    email_ids = messages[0].split()

    if not email_ids:
        print("No relevant emails found.")
        mail.logout()
        return

    try:
        # Process latest email
        latest_email_id = email_ids[-1]
        status, msg_data = mail.fetch(latest_email_id, '(RFC822)')

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])

                # Extract attachment
                for part in msg.walk():
                    if part.get_content_maintype() == 'multipart' or not part.get_filename():
                        continue

                    filename = part.get_filename()
                    if 'poinsituation.xls' in filename:
                        # Save attachment
                        xls_filepath = os.path.join(os.getcwd(), filename)
                        with open(xls_filepath, 'wb') as f:
                            f.write(part.get_payload(decode=True))

                        #print("Saved file: {}".format(filename))

                        # Convert to xlsx
                        xlsx_filepath = convert_xls_to_xlsx(xls_filepath)
                        #print(f"Converted file saved as: {xlsx_filepath}")

                        # Clean the Excel file
                        cleaned_filepath, df = clean_excel_file(xlsx_filepath)
                        #print(f"Cleaned file saved as: {cleaned_filepath}")

                        # Display the DataFrame in a Tkinter Treeview
                        display_dataframe_in_treeview(df)
                  


    finally:
        mail.logout()
        print("Email connection closed")


def display_dataframe_in_treeview(df):
    try:

        for row in PROGTREE.get_children():
            PROGTREE.delete(row)
        
        PROGTREE["columns"] = list(df.columns)
        PROGTREE["show"] = "headings"
        column_widths = {
            "DATE": 70,
            "FLT": 60,
            "TYPE": 40,
            "REG": 60,
            "AC": 40,
            "DEP": 50,
            "ARR": 50,
            "STD": 40,
            "STA": 40,
            "ATD": 40,
            "ATA": 40
        }

        for col in df.columns:
            PROGTREE.heading(col, text=col)
            PROGTREE.column(col, width=column_widths.get(col, 40))  # Default to 100 if column not in dictionary

        
        # Configure row tags for alternating colors
        PROGTREE.tag_configure('oddrow', background='white')
        PROGTREE.tag_configure('evenrow', background='#ebecf0')

        
        for index, row in df.iterrows():
            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            PROGTREE.insert("", "end", values=list(row), tags=(tag,))
       


    except:
        print('error loading programme manually')
        pass

def open_programme_excel():
    try:
        global cleaned_filepath
        if cleaned_filepath:
            os.startfile(cleaned_filepath)
        else:
            print("Error: No cleaned file available.")
    except:
        print('cant open excel file ')
        pass


#--------------filter programme tree
    
def filter_treeview():

    
    query = filter_var.get().lower()  # Get the search query and convert to lowercase
    for row in PROGTREE.get_children():
        PROGTREE.delete(row)  # Clear the Treeview
    # Configure the tag for highlighting matches (once)
    # Configure tags before inserting items
    PROGTREE.tag_configure('oddrow', background='white')
    PROGTREE.tag_configure('evenrow', background='#ffffcc')

    for index, row in df.iterrows():
        tag44 = 'evenrow' if index % 2 == 0 else 'oddrow'
        if any(query in str(row[col]).lower() for col in df.columns):  # Check if query matches any column value
            PROGTREE.insert("", "end", values=list(row), tags=(tag44,))


#---------------------FIN PROG FUNC-------------------------------------------------------------------------------



def get_today_date():
    # Get the current date
    current_datetime = datetime.datetime.now()


    # Format the date as a string
    formatted_date = formatted_date = current_datetime.strftime("%d/%m/%Y")

    # Insert the formatted date into the Entry widget
    DATEENT.delete(0, tk.END)  # Clear any existing content
    DATEENT.insert(0, formatted_date)


def lookupstock(event):
    
    
    # Load Excel file into DataFrame
    df = pd.read_excel("stock.xlsx")

    # Specify the destination value you want to look up
    destination_value = STOCKexcelentescale.get().upper().strip()
    if destination_value.strip():
        # Perform vertical lookup
        result = df.loc[df['DESTINATION'] == destination_value, 'AKE']



        STOCKexcelentescalelabel.configure(text=len(result))
    else:
        STOCKexcelentescalelabel.configure(text="")
        pass

def filter_and_update_treeviewescale(event):

    try:
        excel_file_path = 'stock.xlsx'
        df_res = pd.read_excel(excel_file_path)

        # Get the text from the entry for filtering
        filter_text = STOCKexcelentescale.get().upper().strip()

        # Convert 'AKE' column to strings
        df_res['DESTINATION'] = df_res['DESTINATION'].astype(str)

        # Apply the filter condition based on the 'AKE' column
        filter_condition = (df_res['DESTINATION'].str.contains(filter_text, case=False, na=False))

        # Delete existing items in the Treeview
        for item in DASHTREE.get_children():
            DASHTREE.delete(item)
        # Configure tags before inserting items
        DASHTREE.tag_configure('oddrow', background='white')
        DASHTREE.tag_configure('evenrow', background='#e2faf8')
        # Iterate through each row in the DataFrame, apply the filter condition, and insert into Treeview
        for index, row in df_res[filter_condition].iterrows():
            date_res = row['DATE']
            ake_res = row['AKE']
            flight_res = row['FLIGHT']
            destination = row['DESTINATION']
            # Determine the tag based on the row index
            tag3 = 'evenrow' if index % 2 == 0 else 'oddrow'

            DASHTREE.insert("", "end", values=(date_res, destination,flight_res, ake_res), tags=(tag3,))



            
    except Exception as e:
        print(f"Error: {e}")

#---- filter by ake -----------------
def filter_and_update_treeview(event):

    try:
        excel_file_path = 'stock.xlsx'
        df_res = pd.read_excel(excel_file_path)

        # Get the text from the entry for filtering
        filter_text = STOCKexcelent.get().upper().strip()

        # Convert 'AKE' column to strings
        df_res['AKE'] = df_res['AKE'].astype(str)

        # Apply the filter condition based on the 'AKE' column
        filter_condition = (df_res['AKE'].str.contains(filter_text, case=False, na=False))

        # Delete existing items in the Treeview
        for item in DASHTREE.get_children():
            DASHTREE.delete(item)
        # Configure tags before inserting items
        DASHTREE.tag_configure('oddrow', background='white')
        DASHTREE.tag_configure('evenrow', background='#e2faf8')
        # Iterate through each row in the DataFrame, apply the filter condition, and insert into Treeview
        for index, row in df_res[filter_condition].iterrows():
            date_res = row['DATE']
            ake_res = row['AKE']
            flight_res = row['FLIGHT']
            destination = row['DESTINATION']
            # Determine the tag based on the row index
            tag4 = 'evenrow' if index % 2 == 0 else 'oddrow'
            
            DASHTREE.insert("", "end", values=(date_res, destination,flight_res, ake_res), tags=(tag4,))

    except Exception as e:
        print(f"Error: {e}")


def filter_and_HISTORY_treeviewwBYAKE(event):

    excel_file_path = 'Historique.xlsx' #RED
    df_res = pd.read_excel(excel_file_path)

    # Get the text from the entry for filtering
    filter_text = historiqueake.get().upper().strip()

    # Convert the 'AKE' column to strings for filtering
    df_res['AKE'] = df_res['AKE'].astype(str)

    # Apply the filter condition based on the 'AKE' column
    filter_condition = (df_res['AKE'].str.contains(filter_text, case=False, na=False))

    # Delete existing items in the Treeview
    for item in DASHTREE2.get_children():
        DASHTREE2.delete(item)
# Configure row styles outside the loop
    DASHTREE2.tag_configure('oddrow', background='white')
    DASHTREE2.tag_configure('evenrow', background='light green')
    # Iterate through each row in the DataFrame, apply the filter condition, and insert into Treeview
    for index, row in df_res[filter_condition].iterrows():
        date_res = row['DATE']
        ake_res = row['AKE']
        flight_res = row['FLIGHT']
        destination = row['DESTINATION']
        tag33 = 'evenrow' if index % 2 == 0 else 'oddrow'

        DASHTREE2.insert("", "end", values=(date_res, destination,flight_res, ake_res), tags=(tag33,))



def filter_and_update_treevieww(event):

    excel_file_path = 'Historique.xlsx'
    df_res = pd.read_excel(excel_file_path)

    # Get the text from the entry for filtering
    filter_text = STOCKexcelentt.get().upper().strip()

    # Apply the filter condition based on the 'AKE' column
    filter_condition = (df_res['DESTINATION'].str.contains(filter_text, case=False, na=False))

    # Delete existing items in the Treeview
    for item in DASHTREE2.get_children():
        DASHTREE2.delete(item)
# Configure row styles outside the loop
    DASHTREE2.tag_configure('oddrow', background='white')
    DASHTREE2.tag_configure('evenrow', background='light green')
    # Iterate through each row in the DataFrame, apply the filter condition, and insert into Treeview
    for index, row in df_res[filter_condition].iterrows():
        date_res = row['DATE']
        ake_res = row['AKE']
        flight_res = row['FLIGHT']
        destination = row['DESTINATION']
        tag33 = 'evenrow' if index % 2 == 0 else 'oddrow'

        DASHTREE2.insert("", "end", values=(date_res, destination,flight_res, ake_res), tags=(tag33,))



def SearchfilterDATE(*args):
    resetallentry()
    database()
    try:        
        kword=DATEFILTER.get().upper().strip()
        column='DATE'
        Scrolledtreeview1.delete(*Scrolledtreeview1.get_children())
        conn = sqlite3.connect("DATABASE/ULD.db",detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM AKE WHERE {} LIKE '%{}%'".format(column, kword))
        fetch = cursor.fetchall()
        global count
        count=0
        for data in fetch:
            if count % 2==0:
                Scrolledtreeview1.insert('', 'end', values=(data), tags = ('oddrow'))    
            else:
                Scrolledtreeview1.insert('', 'end', values=(data), tags = ('evenrow'))
            count+=1

        cursor.close()
        conn.close()
    except:
        pass


def SearchfilterFLIGHT(*args):
    resetallentry()
    database()
    try:        
        kword=FLIGHTFILTER.get().upper().strip()
        column='FLIGHT'
        Scrolledtreeview1.delete(*Scrolledtreeview1.get_children())
        conn = sqlite3.connect("DATABASE/ULD.db",detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM AKE WHERE {} LIKE '%{}%'".format(column, kword))
        fetch = cursor.fetchall()
        global count
        count=0
        for data in fetch:
            if count % 2==0:
                Scrolledtreeview1.insert('', 'end', values=(data), tags = ('oddrow'))    
            else:
                Scrolledtreeview1.insert('', 'end', values=(data), tags = ('evenrow'))
            count+=1

        cursor.close()
        conn.close()
    except:
        pass

def SearchfilterDEPART(*args):
    resetallentry()
    database()
    try:        
        kword=DEPARTFILTER.get().upper().strip()
        column='DEPART'
        Scrolledtreeview1.delete(*Scrolledtreeview1.get_children())
        conn = sqlite3.connect("DATABASE/ULD.db",detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM AKE WHERE {} LIKE '%{}%'".format(column, kword))
        fetch = cursor.fetchall()
        global count
        count=0
        for data in fetch:
            if count % 2==0:
                Scrolledtreeview1.insert('', 'end', values=(data), tags = ('oddrow'))    
            else:
                Scrolledtreeview1.insert('', 'end', values=(data), tags = ('evenrow'))
            count+=1

        cursor.close()
        conn.close()
    except:
        pass

def SearchfilterDESTINATION(*args):
    resetallentry()
    database()
    try:        
        kword=DESTINATIONFILTER.get().upper().strip()
        column='DESTINATION'
        Scrolledtreeview1.delete(*Scrolledtreeview1.get_children())
        conn = sqlite3.connect("DATABASE/ULD.db",detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM AKE WHERE {} LIKE '%{}%'".format(column, kword))
        fetch = cursor.fetchall()
        global count
        count=0
        for data in fetch:
            if count % 2==0:
                Scrolledtreeview1.insert('', 'end', values=(data), tags = ('oddrow'))    
            else:
                Scrolledtreeview1.insert('', 'end', values=(data), tags = ('evenrow'))
            count+=1

        cursor.close()
        conn.close()
    except:
        pass

def SearchfilterAKE(*args):
    resetallentry()
    database()
    try:        
        kword = AKEFILTER.get().upper().strip()
        columns = ['AKE1', 'AKE2', 'AKE3', 'AKE4', 'AKE5', 'AKE6', 'AKE7', 'AKE8', 'AKE9', 'AKE10', 'AKE11', 'AKE12', 'AKE13', 'AKE14', 'AKE15']
        Scrolledtreeview1.delete(*Scrolledtreeview1.get_children())
        conn = sqlite3.connect("DATABASE/ULD.db", detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = conn.cursor()

        # Iterate through columns and use OR condition to search for the keyword
        query = "SELECT * FROM AKE WHERE {} LIKE '%{}%'".format(columns[0], kword)
        for column in columns[1:]:
            query += " OR {} LIKE '%{}%'".format(column, kword)

        cursor.execute(query)

        fetch = cursor.fetchall()
        global count
        count = 0
        for data in fetch:
            if count % 2 == 0:
                Scrolledtreeview1.insert('', 'end', values=(data), tags=('oddrow'))
            else:
                Scrolledtreeview1.insert('', 'end', values=(data), tags=('evenrow'))
            count += 1

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")


def lookup2():

    try:
        stock()
    except:
        pass
    try:
        history()
    except:
        pass

    try:
        lookupstock()
    except:
        pass    
    try:
        lookup()
    except:
        pass
    try:
        lookupDEPART()
    except:
        pass
    try:
        ake1()
    except:
        pass
    try:
        ake2()
    except:
        pass
    try:
        ake3()
    except:
        pass
    try:
        ake4()
    except:
        pass
    try:
        ake5()
    except:
        pass
    try:
        ake6()
    except:
        pass
    try:
        ake7()
    except:
        pass
    try:
        ake8()
    except:
        pass
    try:
        ake9()
    except:
        pass
    try:
        ake10()
    except:
        pass
    try:
        ake11()
    except:
        pass
    try:
        ake12()
    except:
        pass
    try:
        ake13()
    except:
        pass
    try:
        ake14()
    except:
        pass
    
    try:
        ake15()
    except:
        pass

    
    
def ake15():    
    
    
    # Load Excel file into DataFrame
    df = pd.read_excel("stock.xlsx")

    # Specify the destination value you want to look up
    destination_value = AKE15ENT.get().upper().strip()
    if destination_value.strip():
        # Perform vertical lookup
        result = df.loc[df['AKE'].astype(str) == str(destination_value), 'DESTINATION'].iloc[0]



        # Print the result

        AKE15RES.configure(text=result)
    else:
        AKE15RES.configure(text="")
        pass


    
def ake14():    
    
    
    # Load Excel file into DataFrame
    df = pd.read_excel("stock.xlsx")

    # Specify the destination value you want to look up
    destination_value = AKE14ENT.get().upper().strip()
    if destination_value.strip():
        # Perform vertical lookup
        result = df.loc[df['AKE'].astype(str) == str(destination_value), 'DESTINATION'].iloc[0]


        AKE14RES.configure(text=result)
    else:
        AKE14RES.configure(text="")
        pass


def ake13():    
    
    
    # Load Excel file into DataFrame
    df = pd.read_excel("stock.xlsx")

    # Specify the destination value you want to look up
    destination_value = AKE13ENT.get().upper().strip()
    if destination_value.strip():
        # Perform vertical lookup
        result = df.loc[df['AKE'].astype(str) == str(destination_value), 'DESTINATION'].iloc[0]


        AKE13RES.configure(text=result)
    else:
        AKE13RES.configure(text="")
        pass


def ake12():    
    
    
    # Load Excel file into DataFrame
    df = pd.read_excel("stock.xlsx")

    # Specify the destination value you want to look up
    destination_value = AKE12ENT.get().upper().strip()
    if destination_value.strip():
        # Perform vertical lookup
        result = df.loc[df['AKE'].astype(str) == str(destination_value), 'DESTINATION'].iloc[0]

        AKE12RES.configure(text=result)
    else:
        AKE12RES.configure(text="")
        pass



def ake11():    
    
    
    # Load Excel file into DataFrame
    df = pd.read_excel("stock.xlsx")

    # Specify the destination value you want to look up
    destination_value = AKE11ENT.get().upper().strip()
    if destination_value.strip():
        # Perform vertical lookup
        result = df.loc[df['AKE'].astype(str) == str(destination_value), 'DESTINATION'].iloc[0]

        AKE11RES.configure(text=result)
    else:
        AKE11RES.configure(text="")
        pass

    
def ake10():    
    
    
    # Load Excel file into DataFrame
    df = pd.read_excel("stock.xlsx")

    # Specify the destination value you want to look up
    destination_value = AKE10ENT.get().upper().strip()
    if destination_value.strip():
        # Perform vertical lookup
        result = df.loc[df['AKE'].astype(str) == str(destination_value), 'DESTINATION'].iloc[0]

        AKE10RES.configure(text=result)
    else:
        AKE10RES.configure(text="")
        pass



def ake9():    
    
    
    # Load Excel file into DataFrame
    df = pd.read_excel("stock.xlsx")

    # Specify the destination value you want to look up
    destination_value = AKE9ENT.get().upper().strip()
    if destination_value.strip():
        # Perform vertical lookup
        result = df.loc[df['AKE'].astype(str) == str(destination_value), 'DESTINATION'].iloc[0]

        AKE9RES.configure(text=result)
    else:
        AKE9RES.configure(text="")
        pass


def ake8():    
    
    
    # Load Excel file into DataFrame
    df = pd.read_excel("stock.xlsx")

    # Specify the destination value you want to look up
    destination_value = AKE8ENT.get().upper().strip()
    if destination_value.strip():
        # Perform vertical lookup
        result = df.loc[df['AKE'].astype(str) == str(destination_value), 'DESTINATION'].iloc[0]

        AKE8RES.configure(text=result)
    else:
        AKE8RES.configure(text="")
        pass

def ake7():    
    
    
    # Load Excel file into DataFrame
    df = pd.read_excel("stock.xlsx")

    # Specify the destination value you want to look up
    destination_value = AKE7ENT.get().upper().strip()
    if destination_value.strip():
        # Perform vertical lookup
        result = df.loc[df['AKE'].astype(str) == str(destination_value), 'DESTINATION'].iloc[0]

        AKE7RES.configure(text=result)
    else:
        AKE7RES.configure(text="")
        pass


def ake6():    
    
    
    # Load Excel file into DataFrame
    df = pd.read_excel("stock.xlsx")

    # Specify the destination value you want to look up
    destination_value = AKE6ENT.get().upper().strip()
    if destination_value.strip():
        # Perform vertical lookup
        result = df.loc[df['AKE'].astype(str) == str(destination_value), 'DESTINATION'].iloc[0]

        AKE6RES.configure(text=result)
    else:
        AKE6RES.configure(text="")
        pass



def ake5():    
    
    
    # Load Excel file into DataFrame
    df = pd.read_excel("stock.xlsx")

    # Specify the destination value you want to look up
    destination_value = AKE5ENT.get().upper().strip()
    if destination_value.strip():
        # Perform vertical lookup
        result = df.loc[df['AKE'].astype(str) == str(destination_value), 'DESTINATION'].iloc[0]

        AKE5RES.configure(text=result)
    else:
        AKE5RES.configure(text="")
        pass


def ake4():    
    
    
    # Load Excel file into DataFrame
    df = pd.read_excel("stock.xlsx")

    # Specify the destination value you want to look up
    destination_value = AKE4ENT.get().upper().strip()
    if destination_value.strip():
        # Perform vertical lookup
        result = df.loc[df['AKE'].astype(str) == str(destination_value), 'DESTINATION'].iloc[0]


        AKE4RES.configure(text=result)
    else:
        AKE4RES.configure(text="")
        pass

    
def ake3():    
    
    
    # Load Excel file into DataFrame
    df = pd.read_excel("stock.xlsx")

    # Specify the destination value you want to look up
    destination_value = AKE3ENT.get().upper().strip()
    if destination_value.strip():
        # Perform vertical lookup
        result = df.loc[df['AKE'].astype(str) == str(destination_value), 'DESTINATION'].iloc[0]


        AKE3RES.configure(text=result)
    else:
        AKE3RES.configure(text="")
        pass

def ake2():    
    
    
    # Load Excel file into DataFrame
    df = pd.read_excel("stock.xlsx")

    # Specify the destination value you want to look up
    destination_value = AKE2ENT.get().upper().strip()
    if destination_value.strip():
        # Perform vertical lookup
        result = df.loc[df['AKE'].astype(str) == str(destination_value), 'DESTINATION'].iloc[0]


        AKE2RES.configure(text=result)
    else:
        AKE2RES.configure(text="")
        pass
def ake1():    
    
    
    # Load Excel file into DataFrame
    df = pd.read_excel("stock.xlsx")

    # Specify the destination value you want to look up
    destination_value = AKE1ENT.get().upper().strip()
    if destination_value.strip():
        # Perform vertical lookup
        result = df.loc[df['AKE'].astype(str) == str(destination_value), 'DESTINATION'].iloc[0]


        AKE1RES.configure(text=result)
    else:
        AKE1RES.configure(text="")
        pass



def lookup():
    
    
    # Load Excel file into DataFrame
    df = pd.read_excel("stock.xlsx")

    # Specify the destination value you want to look up
    destination_value = DESTINATIONENT.get().upper().strip()
    if destination_value.strip():
        # Perform vertical lookup
        result = df.loc[df['DESTINATION'] == destination_value, 'AKE']



        TLabel3_18RES.configure(text=len(result))
    else:
        TLabel3_18RES.configure(text="")
        pass

def lookupDEPART():
    
    
    # Load Excel file into DataFrame
    df = pd.read_excel("stock.xlsx")

    # Specify the destination value you want to look up
    destination_value = DEPARTENT.get().upper().strip()
    if destination_value.strip():
        # Perform vertical lookup
        result = df.loc[df['DESTINATION'] == destination_value, 'AKE']



        DEPARTRES.configure(text=len(result))
    else:
        DEPARTRES.configure(text="")
        pass



    
def excel_file():
            stat_scm=sqlite3.connect("DATABASE/ULD.db",detect_types=sqlite3.PARSE_DECLTYPES)
            df=pd.read_sql("SELECT  * FROM `AKE` ORDER BY `mem_id` DESC",stat_scm)

            # Converts the 'DATENC' column to datetime format.
            df['DATE'] = pd.to_datetime(df['DATE'], format='%d/%m/%Y')

            # Sorts the DataFrame by 'AKEENTT' and 'AKEENTT2' in ascending order and 'DATENC' in descending order.
            df = df.sort_values(by=['AKE1', 'AKE2', 'AKE3', 'AKE4', 'AKE5', 'AKE6', 'AKE7', 'AKE8', 'AKE9', 'AKE10', 'AKE11', 'AKE12', 'AKE13', 'AKE14', 'AKE15', 'DATE'], ascending=[True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, False])

            # Groups the DataFrame by 'DATENC' and 'AKEENTT' and 'AKEENTT2' and selects the first (most recent) occurrence for each group.
            df_grouped = df.groupby(['DATE','AKE1', 'AKE2', 'AKE3', 'AKE4', 'AKE5', 'AKE6', 'AKE7', 'AKE8', 'AKE9', 'AKE10', 'AKE11', 'AKE12', 'AKE13', 'AKE14', 'AKE15']).first().reset_index()

            # Create a new DataFrame with 'DATENC' and 'AKEEres' columns.
            df_res = pd.DataFrame(columns=['DATE', 'AKE', 'FLIGHT', 'DEPART','DESTINATION'])

            # Iterate through each row in the grouped DataFrame and populate the new DataFrame.
            for index, row in df_grouped.iterrows():
                date = row['DATE']
                akeentt = row['AKE1']
                akeentt2 = row['AKE2']
                akeentt3 = row['AKE3']
                akeentt4 = row['AKE4']
                akeentt5 = row['AKE5']
                akeentt6 = row['AKE6']
                akeentt7 = row['AKE7']
                akeentt8 = row['AKE8']
                akeentt9 = row['AKE9']
                akeentt10 = row['AKE10']
                akeentt11 = row['AKE11']
                akeentt12 = row['AKE12']
                akeentt13 = row['AKE13']
                akeentt14 = row['AKE14']
                akeentt15 = row['AKE15']
                flightent = row['FLIGHT']
                destentt = row['DESTINATION']
                depart = row['DEPART']

                # Check for non-empty 'AKEEres' before appending the row
                if pd.notna(akeentt) and akeentt != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt], 'FLIGHT': [flightent], 'DEPART': [depart], 'DESTINATION': [destentt]})], ignore_index=True)

                if pd.notna(akeentt2) and akeentt2 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt2], 'FLIGHT': [flightent], 'DEPART': [depart], 'DESTINATION': [destentt]})], ignore_index=True)


                if pd.notna(akeentt3) and akeentt3 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt3], 'FLIGHT': [flightent], 'DEPART': [depart], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt4) and akeentt4 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt4], 'FLIGHT': [flightent], 'DEPART': [depart], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt5) and akeentt5 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt5], 'FLIGHT': [flightent], 'DEPART': [depart], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt6) and akeentt6 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt6], 'FLIGHT': [flightent], 'DEPART': [depart], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt7) and akeentt7 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt7], 'FLIGHT': [flightent], 'DEPART': [depart], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt8) and akeentt8 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt8], 'FLIGHT': [flightent], 'DEPART': [depart], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt9) and akeentt9 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt9], 'FLIGHT': [flightent], 'DEPART': [depart], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt10) and akeentt10 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt10], 'FLIGHT': [flightent], 'DEPART': [depart], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt11) and akeentt11 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt11], 'FLIGHT': [flightent], 'DEPART': [depart], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt12) and akeentt12 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt12], 'FLIGHT': [flightent], 'DEPART': [depart], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt13) and akeentt13 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt13], 'FLIGHT': [flightent], 'DEPART': [depart], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt14) and akeentt14 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt14], 'FLIGHT': [flightent], 'DEPART': [depart], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt15) and akeentt15 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt15], 'FLIGHT': [flightent], 'DEPART': [depart], 'DESTINATION': [destentt]})], ignore_index=True)


  
            # Drop rows with NaN values
            df_res = df_res.dropna()

            # Group by 'AKEEres' and keep only the most recent entry for each group
            df_res = df_res.loc[df_res.groupby('AKE')['DATE'].idxmax()]
            try:   
            # Format the 'DATEres' column to display only day, month, and year
                df_res['DATE'] = df_res['DATE'].dt.strftime('%d/%m/%Y')
            except:
                pass

            
            # Save df_res to an Excel file
            excel_file_path = "excel.xlsx"  # Change this to your desired file path
            df_res.to_excel(excel_file_path, index=False)

            os.startfile('excel.xlsx')


def recap():
            global df_summary
            stat_scm=sqlite3.connect("DATABASE/ULD.db",detect_types=sqlite3.PARSE_DECLTYPES)
            df=pd.read_sql("SELECT  * FROM `AKE` ORDER BY `mem_id` DESC",stat_scm)

            # Converts the 'DATENC' column to datetime format.
            df['DATE'] = pd.to_datetime(df['DATE'], format='%d/%m/%Y')

            # Sorts the DataFrame by 'AKEENTT' and 'AKEENTT2' in ascending order and 'DATENC' in descending order.
            df = df.sort_values(by=['AKE1', 'AKE2', 'AKE3', 'AKE4', 'AKE5', 'AKE6', 'AKE7', 'AKE8', 'AKE9', 'AKE10', 'AKE11', 'AKE12', 'AKE13', 'AKE14', 'AKE15', 'DATE'], ascending=[True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, False])

            # Groups the DataFrame by 'DATENC' and 'AKEENTT' and 'AKEENTT2' and selects the first (most recent) occurrence for each group.
            df_grouped = df.groupby(['DATE','AKE1', 'AKE2', 'AKE3', 'AKE4', 'AKE5', 'AKE6', 'AKE7', 'AKE8', 'AKE9', 'AKE10', 'AKE11', 'AKE12', 'AKE13', 'AKE14', 'AKE15']).first().reset_index()

            # Create a new DataFrame with 'DATENC' and 'AKEEres' columns.
            df_res = pd.DataFrame(columns=['DATE', 'AKE', 'DESTINATION'])

            # Iterate through each row in the grouped DataFrame and populate the new DataFrame.
            for index, row in df_grouped.iterrows():
                date = row['DATE']
                akeentt = row['AKE1']
                akeentt2 = row['AKE2']
                akeentt3 = row['AKE3']
                akeentt4 = row['AKE4']
                akeentt5 = row['AKE5']
                akeentt6 = row['AKE6']
                akeentt7 = row['AKE7']
                akeentt8 = row['AKE8']
                akeentt9 = row['AKE9']
                akeentt10 = row['AKE10']
                akeentt11 = row['AKE11']
                akeentt12 = row['AKE12']
                akeentt13 = row['AKE13']
                akeentt14 = row['AKE14']
                akeentt15 = row['AKE15']
                destentt = row['DESTINATION']

                # Check for non-empty 'AKEEres' before appending the row
                if pd.notna(akeentt) and akeentt != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt], 'DESTINATION': [destentt]})], ignore_index=True)

                if pd.notna(akeentt2) and akeentt2 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt2], 'DESTINATION': [destentt]})], ignore_index=True)


                if pd.notna(akeentt3) and akeentt3 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt3], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt4) and akeentt4 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt4], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt5) and akeentt5 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt5], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt6) and akeentt6 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt6], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt7) and akeentt7 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt7], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt8) and akeentt8 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt8], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt9) and akeentt9 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt9], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt10) and akeentt10 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt10], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt11) and akeentt11 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt11], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt12) and akeentt12 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt12], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt13) and akeentt13 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt13], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt14) and akeentt14 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt14], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt15) and akeentt15 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt15], 'DESTINATION': [destentt]})], ignore_index=True)


  
            # Drop rows with NaN values
            df_res = df_res.dropna()

            # Group by 'AKEEres' and keep only the most recent entry for each group
            df_res = df_res.loc[df_res.groupby('AKE')['DATE'].idxmax()]
            try:   
            # Format the 'DATEres' column to display only day, month, and year
                df_res['DATE'] = df_res['DATE'].dt.strftime('%d/%m/%Y')
            except:
                pass

            
            # Save df_res to an Excel file
            excel_file_path = "recape.xlsx"  # Change this to your desired file path
            df_res.to_excel(excel_file_path, index=False)
            #os.startfile('recape.xlsx')


            # Path to the Excel file generated earlier
            excel_file_path = "stock.xlsx"

            # Read the Excel file into a pandas DataFrame
            df_read = pd.read_excel(excel_file_path)

            # Reorder the columns for the first printout
            df_read = df_read[['DATE', 'DESTINATION', 'AKE']]


            # Group by 'DESTINATION' and get the most recent 'DATE' and the count of occurrences
            df_summary = (
                df_read.groupby('DESTINATION')
                .agg(
                    DATE=('DATE', 'max'),  # Get the most recent date
                    OCCURRENCES=('DESTINATION', 'count')  # Count the occurrences
                )
                .reset_index()
            )

            # Reorder columns to display 'DATE', 'DESTINATION', and 'OCCURRENCES'
            df_summary = df_summary[['DATE', 'DESTINATION', 'OCCURRENCES']]
            

            # number total of ake
            total_occurrences = df_summary["OCCURRENCES"].sum()


            totalakeactivelabel.config(text=f"ACT:{total_occurrences}")
            totalakehslabel.config(text='HS:--')


            # Delete existing items in the Treeview
            for item in DASHTREE3.get_children():
                DASHTREE3.delete(item)

            # Configure Treeview row tags
            DASHTREE3.tag_configure('oddrow', background='white')
            DASHTREE3.tag_configure('evenrow', background='#e2faf8')
            DASHTREE3.tag_configure('low_occurrence', foreground='red', background='#ffe5e5')  # Light red background for low occurrences

            # Iterate through each row in the Summary DataFrame and insert into Treeview
            for index, row in df_summary.iterrows():
                date_res = row['DATE']
                destination = row['DESTINATION']
                occurrences = row['OCCURRENCES']
                
                # Determine the tag based on the 'OCCURRENCES' value
                if occurrences <= 1 :
                    tag5 = 'low_occurrence'  # Red for low occurrences
                else:
                    tag5 = 'evenrow' if index % 2 == 0 else 'oddrow'
                
                # Insert row into the Treeview
                DASHTREE3.insert("", "end", values=(date_res, destination, occurrences), tags=(tag5,))
                
def sumrary_excel():
            try:
                global df_summary
                # Rename columns
                df_summary = df_summary.rename(columns={
                'DESTINATION': 'ESCALE',
                'OCCURRENCES': 'NOMBRE AKE'
                })
                df_summary.to_excel('filtered_summary.xlsx', index=False)
                os.startfile('filtered_summary.xlsx')
            except:
                pass

def stock_excel():
            stat_scm=sqlite3.connect("DATABASE/ULD.db",detect_types=sqlite3.PARSE_DECLTYPES)
            df=pd.read_sql("SELECT  * FROM `AKE` ORDER BY `mem_id` DESC",stat_scm)

            # Converts the 'DATENC' column to datetime format.
            df['DATE'] = pd.to_datetime(df['DATE'], format='%d/%m/%Y')

##            # Sorts the DataFrame by 'AKEENTT' and 'AKEENTT2' in ascending order and 'DATENC' in descending order.
##            df = df.sort_values(by=['AKE1', 'AKE2', 'AKE3', 'AKE4', 'AKE5', 'AKE6', 'AKE7', 'AKE8', 'AKE9', 'AKE10', 'AKE11', 'AKE12', 'AKE13', 'AKE14', 'AKE15', 'DATE'], ascending=[True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, False])
##
##            # Groups the DataFrame by 'DATENC' and 'AKEENTT' and 'AKEENTT2' and selects the first (most recent) occurrence for each group.
##            df_grouped = df.groupby(['DATE','AKE1', 'AKE2', 'AKE3', 'AKE4', 'AKE5', 'AKE6', 'AKE7', 'AKE8', 'AKE9', 'AKE10', 'AKE11', 'AKE12', 'AKE13', 'AKE14', 'AKE15']).first().reset_index()


            # Sorts the DataFrame by 'AKEENTT' and 'AKEENTT2' in ascending order and 'DATENC' in descending order.
            df = df.sort_values(by=[ 'DATE', 'mem_id'], ascending=[False, False])

            # Groups the DataFrame by 'DATENC' and 'AKEENTT' and 'AKEENTT2' and selects the first (most recent) occurrence for each group.
            df_grouped = df.drop_duplicates(
    subset=['DATE', 'AKE1', 'AKE2', 'AKE3', 'AKE4', 'AKE5', 'AKE6',
            'AKE7', 'AKE8', 'AKE9', 'AKE10', 'AKE11', 'AKE12',
            'AKE13', 'AKE14', 'AKE15'],
    keep='first'  # keeps the row with lowest DATE and mem_id, due to your sorting
).reset_index(drop=True)

            # Create a new DataFrame with 'DATENC' and 'AKEEres' columns.
            df_res = pd.DataFrame(columns=['DATE', 'AKE', 'FLIGHT', 'DESTINATION'])

            # Iterate through each row in the grouped DataFrame and populate the new DataFrame.
            for index, row in df_grouped.iterrows():
                date = row['DATE']
                akeentt = row['AKE1']
                akeentt2 = row['AKE2']
                akeentt3 = row['AKE3']
                akeentt4 = row['AKE4']
                akeentt5 = row['AKE5']
                akeentt6 = row['AKE6']
                akeentt7 = row['AKE7']
                akeentt8 = row['AKE8']
                akeentt9 = row['AKE9']
                akeentt10 = row['AKE10']
                akeentt11 = row['AKE11']
                akeentt12 = row['AKE12']
                akeentt13 = row['AKE13']
                akeentt14 = row['AKE14']
                akeentt15 = row['AKE15']
                flightent = row['FLIGHT']
                destentt = row['DESTINATION']

                # Check for non-empty 'AKEEres' before appending the row
                if pd.notna(akeentt) and akeentt != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)

                if pd.notna(akeentt2) and akeentt2 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt2], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)


                if pd.notna(akeentt3) and akeentt3 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt3], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt4) and akeentt4 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt4], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt5) and akeentt5 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt5], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt6) and akeentt6 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt6], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt7) and akeentt7 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt7], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt8) and akeentt8 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt8], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt9) and akeentt9 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt9], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt10) and akeentt10 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt10], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt11) and akeentt11 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt11], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt12) and akeentt12 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt12], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt13) and akeentt13 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt13], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt14) and akeentt14 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt14], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt15) and akeentt15 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt15], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)


  
            # Drop rows with NaN values
            df_res = df_res.dropna()

            # Group by 'AKEEres' and keep only the most recent entry for each group
            df_res = df_res.loc[df_res.groupby('AKE')['DATE'].idxmax()]
            try:   
            # Format the 'DATEres' column to display only day, month, and year
                df_res['DATE'] = df_res['DATE'].dt.strftime('%d/%m/%Y')
            except:
                pass

            # Delete existing items in the Treeview
            for item in DASHTREE.get_children():
                DASHTREE.delete(item)
            # Configure tags before inserting items
            DASHTREE.tag_configure('oddrow', background='white')
            DASHTREE.tag_configure('evenrow', background='#e2faf8') 
            # Iterate through each row in the DataFrame and insert into Treeview
            for index, row in df_res.iterrows():
                date_res = row['DATE']
                ake_res = row['AKE']
                flight_res = row['FLIGHT']
                destination = row['DESTINATION']
                tag5 = 'evenrow' if index % 2 == 0 else 'oddrow'
                DASHTREE.insert("", "end", values=(date_res,destination ,flight_res,ake_res ), tags=(tag5,))

            
            # Save df_res to an Excel file
            excel_file_path = "stock.xlsx"  # Change this to your desired file path
            df_res.to_excel(excel_file_path, index=False)
            os.startfile('stock.xlsx')

            



def stock():
            stat_scm=sqlite3.connect("DATABASE/ULD.db",detect_types=sqlite3.PARSE_DECLTYPES)
            df=pd.read_sql("SELECT  * FROM `AKE` ORDER BY `mem_id` DESC",stat_scm)

            # Converts the 'DATENC' column to datetime format.
            df['DATE'] = pd.to_datetime(df['DATE'], format='%d/%m/%Y')



##            # Sorts the DataFrame by 'AKEENTT' and 'AKEENTT2' in ascending order and 'DATENC' in descending order.
##            df = df.sort_values(by=['AKE1', 'AKE2', 'AKE3', 'AKE4', 'AKE5', 'AKE6', 'AKE7', 'AKE8', 'AKE9', 'AKE10', 'AKE11', 'AKE12', 'AKE13', 'AKE14', 'AKE15', 'DATE'], ascending=[True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, False])
##
##            # Groups the DataFrame by 'DATENC' and 'AKEENTT' and 'AKEENTT2' and selects the first (most recent) occurrence for each group.
##            df_grouped = df.groupby(['DATE','AKE1', 'AKE2', 'AKE3', 'AKE4', 'AKE5', 'AKE6', 'AKE7', 'AKE8', 'AKE9', 'AKE10', 'AKE11', 'AKE12', 'AKE13', 'AKE14', 'AKE15']).first().reset_index()




            # Sorts the DataFrame by 'AKEENTT' and 'AKEENTT2' in ascending order and 'DATENC' in descending order.
            df = df.sort_values(by=[ 'DATE', 'mem_id'], ascending=[False, False])

            # Groups the DataFrame by 'DATENC' and 'AKEENTT' and 'AKEENTT2' and selects the first (most recent) occurrence for each group.
            df_grouped = df.drop_duplicates(
    subset=['DATE', 'AKE1', 'AKE2', 'AKE3', 'AKE4', 'AKE5', 'AKE6',
            'AKE7', 'AKE8', 'AKE9', 'AKE10', 'AKE11', 'AKE12',
            'AKE13', 'AKE14', 'AKE15'],
    keep='first'  # keeps the row with lowest DATE and mem_id, due to your sorting
).reset_index(drop=True)

            print(df)
            print(df_grouped)
            # Create a new DataFrame with 'DATENC' and 'AKEEres' columns.
            df_res = pd.DataFrame(columns=['DATE', 'AKE', 'FLIGHT', 'DESTINATION'])

            # Iterate through each row in the grouped DataFrame and populate the new DataFrame.
            for index, row in df_grouped.iterrows():
                date = row['DATE']
                akeentt = row['AKE1']
                akeentt2 = row['AKE2']
                akeentt3 = row['AKE3']
                akeentt4 = row['AKE4']
                akeentt5 = row['AKE5']
                akeentt6 = row['AKE6']
                akeentt7 = row['AKE7']
                akeentt8 = row['AKE8']
                akeentt9 = row['AKE9']
                akeentt10 = row['AKE10']
                akeentt11 = row['AKE11']
                akeentt12 = row['AKE12']
                akeentt13 = row['AKE13']
                akeentt14 = row['AKE14']
                akeentt15 = row['AKE15']
                flightent = row['FLIGHT']
                destentt = row['DESTINATION']

                # Check for non-empty 'AKEEres' before appending the row
                if pd.notna(akeentt) and akeentt != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)

                if pd.notna(akeentt2) and akeentt2 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt2], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)


                if pd.notna(akeentt3) and akeentt3 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt3], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt4) and akeentt4 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt4], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt5) and akeentt5 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt5], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt6) and akeentt6 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt6], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt7) and akeentt7 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt7], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt8) and akeentt8 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt8], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt9) and akeentt9 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt9], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt10) and akeentt10 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt10], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt11) and akeentt11 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt11], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt12) and akeentt12 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt12], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt13) and akeentt13 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt13], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt14) and akeentt14 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt14], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt15) and akeentt15 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt15], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)


  
            # Drop rows with NaN values
            df_res = df_res.dropna()
            # Group by 'AKEEres' and keep only the most recent entry for each group
            df_res = df_res.loc[df_res.groupby('AKE')['DATE'].idxmax()]

 
            # Format the 'DATEres' column to display only day, month, and year
            try:
                df_res['DATE'] = df_res['DATE'].dt.strftime('%d/%m/%Y')
            except:
                pass

            # Delete existing items in the Treeview
            for item in DASHTREE.get_children():
                DASHTREE .delete(item)
                # Configure tags before inserting items
            DASHTREE.tag_configure('oddrow', background='white')
            DASHTREE.tag_configure('evenrow', background='#e2faf8')

            #Iterate through each row in the DataFrame and insert into Treeview
            for index, row in df_res.iterrows():
                date_res = row['DATE']
                ake_res = row['AKE']
                flight_res = row['FLIGHT']
                destination = row['DESTINATION']
                tag = 'evenrow' if index % 2 == 0 else 'oddrow'
                DASHTREE.insert("", "end", values=(date_res,destination,flight_res ,ake_res ), tags=(tag,))

            
            # Save df_res to an Excel file
            excel_file_path = "stock.xlsx"  # Change this to your desired file path
            df_res.to_excel(excel_file_path, index=False)


    

def history_excel():
            stat_scm=sqlite3.connect("DATABASE/ULD.db",detect_types=sqlite3.PARSE_DECLTYPES)
            df=pd.read_sql("SELECT  * FROM `AKE` ORDER BY `mem_id` DESC",stat_scm)

            # Converts the 'DATENC' column to datetime format.
            df['DATE'] = pd.to_datetime(df['DATE'], format='%d/%m/%Y')

            # Sorts the DataFrame by 'AKEENTT' and 'AKEENTT2' in ascending order and 'DATENC' in descending order.
            df = df.sort_values(by=['AKE1', 'AKE2', 'AKE3', 'AKE4', 'AKE5', 'AKE6', 'AKE7', 'AKE8', 'AKE9', 'AKE10', 'AKE11', 'AKE12', 'AKE13', 'AKE14', 'AKE15', 'DATE'], ascending=[True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, False])

            # Groups the DataFrame by 'DATENC' and 'AKEENTT' and 'AKEENTT2' and selects the first (most recent) occurrence for each group.
            df_grouped = df.groupby(['DATE','AKE1', 'AKE2', 'AKE3', 'AKE4', 'AKE5', 'AKE6', 'AKE7', 'AKE8', 'AKE9', 'AKE10', 'AKE11', 'AKE12', 'AKE13', 'AKE14', 'AKE15']).first().reset_index()

            # Create a new DataFrame with 'DATENC' and 'AKEEres' columns.
            df_res = pd.DataFrame(columns=['DATE', 'AKE', 'FLIGHT', 'DESTINATION'])

            # Iterate through each row in the grouped DataFrame and populate the new DataFrame.
            for index, row in df_grouped.iterrows():
                date = row['DATE']
                akeentt = row['AKE1']
                akeentt2 = row['AKE2']
                akeentt3 = row['AKE3']
                akeentt4 = row['AKE4']
                akeentt5 = row['AKE5']
                akeentt6 = row['AKE6']
                akeentt7 = row['AKE7']
                akeentt8 = row['AKE8']
                akeentt9 = row['AKE9']
                akeentt10 = row['AKE10']
                akeentt11 = row['AKE11']
                akeentt12 = row['AKE12']
                akeentt13 = row['AKE13']
                akeentt14 = row['AKE14']
                akeentt15 = row['AKE15']
                flightent = row['FLIGHT']
                destentt = row['DESTINATION']

                # Check for non-empty 'AKEEres' before appending the row
                if pd.notna(akeentt) and akeentt != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)

                if pd.notna(akeentt2) and akeentt2 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt2], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)

                if pd.notna(akeentt3) and akeentt3 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt3], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt4) and akeentt4 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt4], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt5) and akeentt5 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt5], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt6) and akeentt6 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt6], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt7) and akeentt7 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt7], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt8) and akeentt8 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt8], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt9) and akeentt9 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt9], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt10) and akeentt10 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt10], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt11) and akeentt11 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt11], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt12) and akeentt12 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt12], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt13) and akeentt13 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt13], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt14) and akeentt14 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt14], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt15) and akeentt15 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt15], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)


  
            # Drop rows with NaN values
            df_res = df_res.dropna()
            try:
            # Format the 'DATEres' column to display only day, month, and year
                df_res['DATE'] = df_res['DATE'].dt.strftime('%d/%m/%Y')
            except:
                pass
            # Save df_res to an Excel file
            excel_file_path = "Historique.xlsx"  # Change this to your desired file path
            df_res.to_excel(excel_file_path, index=False)
            os.startfile('Historique.xlsx')

def history():
            stat_scm=sqlite3.connect("DATABASE/ULD.db",detect_types=sqlite3.PARSE_DECLTYPES)
            df=pd.read_sql("SELECT  * FROM `AKE` ORDER BY `mem_id` DESC",stat_scm)

            # Converts the 'DATENC' column to datetime format.
            df['DATE'] = pd.to_datetime(df['DATE'], format='%d/%m/%Y')

            # Sorts the DataFrame by 'AKEENTT' and 'AKEENTT2' in ascending order and 'DATENC' in descending order.
            df = df.sort_values(by=['AKE1', 'AKE2', 'AKE3', 'AKE4', 'AKE5', 'AKE6', 'AKE7', 'AKE8', 'AKE9', 'AKE10', 'AKE11', 'AKE12', 'AKE13', 'AKE14', 'AKE15', 'DATE'], ascending=[True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, False])

            # Groups the DataFrame by 'DATENC' and 'AKEENTT' and 'AKEENTT2' and selects the first (most recent) occurrence for each group.
            df_grouped = df.groupby(['DATE','AKE1', 'AKE2', 'AKE3', 'AKE4', 'AKE5', 'AKE6', 'AKE7', 'AKE8', 'AKE9', 'AKE10', 'AKE11', 'AKE12', 'AKE13', 'AKE14', 'AKE15']).first().reset_index()

            # Create a new DataFrame with 'DATENC' and 'AKEEres' columns.
            df_res = pd.DataFrame(columns=['DATE', 'AKE', 'FLIGHT', 'DESTINATION'])

            # Iterate through each row in the grouped DataFrame and populate the new DataFrame.
            for index, row in df_grouped.iterrows():
                date = row['DATE']
                akeentt = row['AKE1']
                akeentt2 = row['AKE2']
                akeentt3 = row['AKE3']
                akeentt4 = row['AKE4']
                akeentt5 = row['AKE5']
                akeentt6 = row['AKE6']
                akeentt7 = row['AKE7']
                akeentt8 = row['AKE8']
                akeentt9 = row['AKE9']
                akeentt10 = row['AKE10']
                akeentt11 = row['AKE11']
                akeentt12 = row['AKE12']
                akeentt13 = row['AKE13']
                akeentt14 = row['AKE14']
                akeentt15 = row['AKE15']
                flightent = row['FLIGHT']
                destentt = row['DESTINATION']

                # Check for non-empty 'AKEEres' before appending the row
                if pd.notna(akeentt) and akeentt != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)

                if pd.notna(akeentt2) and akeentt2 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt2], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)

                if pd.notna(akeentt3) and akeentt3 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt3], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt4) and akeentt4 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt4], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt5) and akeentt5 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt5], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt6) and akeentt6 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt6], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt7) and akeentt7 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt7], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt8) and akeentt8 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt8], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt9) and akeentt9 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt9], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt10) and akeentt10 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt10], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt11) and akeentt11 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt11], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt12) and akeentt12 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt12], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt13) and akeentt13 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt13], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt14) and akeentt14 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt14], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)
                if pd.notna(akeentt15) and akeentt15 != "":
                    df_res = pd.concat([df_res, pd.DataFrame({'DATE': [date], 'AKE': [akeentt15], 'FLIGHT': [flightent], 'DESTINATION': [destentt]})], ignore_index=True)


  
            # Drop rows with NaN values
            df_res = df_res.dropna()
            try:
            # Format the 'DATEres' column to display only day, month, and year
                df_res['DATE'] = df_res['DATE'].dt.strftime('%d/%m/%Y')
            except:
                pass
            # Save df_res to an Excel file


            # Delete existing items in the Treeview
            for item in DASHTREE2.get_children():
                DASHTREE2.delete(item)
            # Configure tags before inserting items
            DASHTREE2.tag_configure('oddrow', background='white')
            DASHTREE2.tag_configure('evenrow', background='#e3ffe8')
            #Iterate through each row in the DataFrame and insert into Treeview
            for index, row in df_res.iterrows():
                date_res = row['DATE']
                ake_res = row['AKE']
                flight_res = row['FLIGHT']
                destination = row['DESTINATION']
                
                # Determine the tag based on the row index
                tag2 = 'evenrow' if index % 2 == 0 else 'oddrow'
                
                DASHTREE2.insert("", "end", values=(date_res,destination,flight_res ,ake_res ), tags=(tag2,))



            excel_file_path = "Historique.xlsx"  # Change this to your desired file path
            df_res.to_excel(excel_file_path, index=False)


   
def resetfilter():
    
    DATEFILTER.delete(0,END)
    FLIGHTFILTER.delete(0,END)
    DEPARTFILTER.delete(0,END)
    DESTINATIONFILTER.delete(0,END)
    AKEFILTER.delete(0,END)
    database()

def resetallentry():
    
    DATEENT.delete(0,END)
    FLIGHTENT.delete(0,END)
    DEPARTENT.delete(0,END)
    DESTINATIONENT.delete(0,END)
    AKE1ENT.delete(0,END)
    AKE2ENT.delete(0,END)
    AKE3ENT.delete(0,END)
    AKE4ENT.delete(0,END)
    AKE5ENT.delete(0,END)
    AKE6ENT.delete(0,END)
    AKE7ENT.delete(0,END)
    AKE8ENT.delete(0,END)
    AKE9ENT.delete(0,END)
    AKE10ENT.delete(0,END)
    AKE11ENT.delete(0,END)
    AKE12ENT.delete(0,END)
    AKE13ENT.delete(0,END)
    AKE14ENT.delete(0,END)
    AKE15ENT.delete(0,END)
    TLabel3_18RES.configure(text="")
    DEPARTRES.configure(text="")
    AKE1RES.configure(text="")
    AKE2RES.configure(text="")
    AKE3RES.configure(text="")
    AKE4RES.configure(text="")
    AKE5RES.configure(text="")
    AKE6RES.configure(text="")
    AKE7RES.configure(text="")
    AKE8RES.configure(text="")
    AKE9RES.configure(text="")
    AKE10RES.configure(text="")
    AKE11RES.configure(text="")
    AKE12RES.configure(text="")
    AKE13RES.configure(text="")
    AKE14RES.configure(text="")
    AKE15RES.configure(text="")
    STOCKexcelent.delete(0,END)
    STOCKexcelentt.delete(0,END)
    historiqueake.delete(0,END)
    STOCKexcelentescale.delete(0,END)
    STOCKexcelentescalelabel.configure(text="")
    database()
    try:
        stock()
    except:
        pass
    try:
        history()
    except:
        pass

    try:
        recap()
    except:
        pass



def database():

    Scrolledtreeview1.delete(*Scrolledtreeview1.get_children())
    database_fiche = sqlite3.connect("DATABASE/ULD.db",detect_types=sqlite3.PARSE_DECLTYPES)
    
    cursor = database_fiche.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS `AKE` (mem_id INTEGER NOT NULL  PRIMARY KEY AUTOINCREMENT,DATE TEXT,FLIGHT TEXT,DEPART TEXT,\
    DESTINATION TEXT,AKE1 TEXT,AKE2 TEXT,AKE3 TEXT,AKE4 TEXT,AKE5 TEXT,\
    AKE6 TEXT,AKE7 TEXT,AKE8 TEXT,AKE9 TEXT,AKE10 TEXT,AKE11 TEXT,AKE12 TEXT,AKE13 TEXT,AKE14 TEXT,AKE15 TEXT)")
    cursor.execute("SELECT * FROM `AKE` ORDER BY `mem_id` DESC")
    fetch = cursor.fetchall()
    global count
    count=0
    for data in fetch:
        if count % 2==0:
            Scrolledtreeview1.insert('', 'end', values=(data), tags = ('oddrow'))    
        else:
            Scrolledtreeview1.insert('', 'end', values=(data), tags = ('evenrow'))
        count+=1
    cursor.close()
##    try:
##        stock()
##    except:
##        pass
##    try:
##        history()
##    except:
##        pass
##
##    try:
##        recap()
##    except:
##        pass
    
def AddData():

    if  DATEENT.get() == "":
        result = tkMessageBox.showwarning('', 'SVP Completer les Information du Produit', icon="warning")
    else:

        Scrolledtreeview1.delete(*Scrolledtreeview1.get_children())
        conn = sqlite3.connect("DATABASE/ULD.db")
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM AKE WHERE AKE1=? and DATE=? and FLIGHT=? and DESTINATION=? ' , (str(AKE1ENT.get().upper()),(str(DATEENT.get().strip())),str(FLIGHTENT.get().upper().strip()),str(DESTINATIONENT.get().upper().strip())))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO `AKE` (DATE, \
                       FLIGHT,DEPART , DESTINATION,AKE1,AKE2,AKE3,AKE4,AKE5,AKE6,AKE7,AKE8,AKE9,AKE10,AKE11,AKE12,AKE13,AKE14,AKE15 )VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",\
                           (str(DATEENT.get().strip()),str(FLIGHTENT.get().upper().strip()),str(DEPARTENT.get().upper().strip()),str(DESTINATIONENT.get().upper().strip()),\
                            str(AKE1ENT.get().upper().strip()),str(AKE2ENT.get().upper().strip()),str(AKE3ENT.get().upper().strip()),str(AKE4ENT.get().upper().strip()),\
                            str(AKE5ENT.get().upper().strip()),str(AKE6ENT.get().upper().strip()),str(AKE7ENT.get().upper().strip()),str(AKE8ENT.get().upper().strip()),\
                            str(AKE9ENT.get().upper().strip()),str(AKE10ENT.get().upper().strip()),str(AKE11ENT.get().upper().strip()),str(AKE12ENT.get().upper().strip()),\
                            str(AKE13ENT.get().upper().strip()),str(AKE14ENT.get().upper().strip()),str(AKE15ENT.get().upper().strip())))
            conn.commit()
            cursor.execute("SELECT * FROM `AKE` ORDER BY `mem_id` DESC")
            fetch = cursor.fetchall()
            global count
            count=0
            for data in fetch:
                if count % 2==0:
                    Scrolledtreeview1.insert('', 'end', values=(data), tags = ('oddrow'))
                else:
                    Scrolledtreeview1.insert('', 'end', values=(data), tags = ('evenrow'))
                count+=1 
                child_id = Scrolledtreeview1.get_children()[0]
                Scrolledtreeview1.focus(child_id)
                Scrolledtreeview1.selection_set(child_id)

##                try:
##                    stock()
##                except:
##                    pass
##                try:
##                    history()
##                except:
##                    pass
##
##                
##                # Log the data insertion
##                #logging.info(f"Data inserted: {data}")
##                try:
##                    stock()
##                except:
##                    pass
##                try:
##                    history()
##                except:
##                    pass
##
##                try:
##                    recap()
##                except:
##                    pass
##               

        else:
            result = tkMessageBox.showwarning('', 'Data exist already', icon="warning")
            database()
            #return
            child_id = Scrolledtreeview1.get_children()[0]
            Scrolledtreeview1.focus(child_id)
            Scrolledtreeview1.selection_set(child_id)

def OnSelected(event):
    #resetentry()
    
    if not Scrolledtreeview1.selection():
        pass
        #result = tkMessageBox.showwarning('', 'Please Select Something First- on selected!', icon="warning")
    else:

        global mem_id 
        curItem = Scrolledtreeview1.focus()
        contents =(Scrolledtreeview1.item(curItem))
        selecteditem = contents['values']
        DATEENT.delete(0,END)
        FLIGHTENT.delete(0,END)
        DEPARTENT.delete(0,END)
        DESTINATIONENT.delete(0,END)
        AKE1ENT.delete(0,END)
        AKE2ENT.delete(0,END)
        AKE3ENT.delete(0,END)
        AKE4ENT.delete(0,END)
        AKE5ENT.delete(0,END)
        AKE6ENT.delete(0,END)
        AKE7ENT.delete(0,END)
        AKE8ENT.delete(0,END)
        AKE9ENT.delete(0,END)
        AKE10ENT.delete(0,END)
        AKE11ENT.delete(0,END)
        AKE12ENT.delete(0,END)
        AKE13ENT.delete(0,END)
        AKE14ENT.delete(0,END)
        AKE15ENT.delete(0,END)



        mem_id = selecteditem[0]
        DATEENT.insert(END,selecteditem[1])
        FLIGHTENT.insert(END,selecteditem[2])
        DEPARTENT.insert(END,selecteditem[3])
        DESTINATIONENT.insert(END,selecteditem[4])
        AKE1ENT.insert(END,selecteditem[5])
        AKE2ENT.insert(END,selecteditem[6])
        AKE3ENT.insert(END,selecteditem[7])
        AKE4ENT.insert(END,selecteditem[8])
        AKE5ENT.insert(END,selecteditem[9])
        AKE6ENT.insert(END,selecteditem[10])
        AKE7ENT.insert(END,selecteditem[11])
        AKE8ENT.insert(END,selecteditem[12])
        AKE9ENT.insert(END,selecteditem[13])
        AKE10ENT.insert(END,selecteditem[14])
        AKE11ENT.insert(END,selecteditem[15])
        AKE12ENT.insert(END,selecteditem[16])
        AKE13ENT.insert(END,selecteditem[17])
        AKE14ENT.insert(END,selecteditem[18])
        AKE15ENT.insert(END,selecteditem[19])

        
def DeleteData():
    if not Scrolledtreeview1.selection():
       result = tkMessageBox.showwarning('', 'Please Select Something First!', icon="warning")
    else:
        result = tkMessageBox.askquestion('', 'Are you sure you want to delete this record?', icon="warning")
        if result == 'yes':
            curItem = Scrolledtreeview1.focus()
            contents =(Scrolledtreeview1.item(curItem))
            selecteditem = contents['values']
            Scrolledtreeview1.delete(curItem)
            conn = sqlite3.connect("DATABASE/ULD.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM `AKE` WHERE `mem_id` = %d" % selecteditem[0])
            conn.commit()
            cursor.close()
            conn.close()
            #resetentry()
            try:
                child_id = Scrolledtreeview1.get_children()[0]
                Scrolledtreeview1.focus(child_id)
                Scrolledtreeview1.selection_set(child_id)
            except:
                pass
            try:
                stock()
            except:
                pass
            try:
                history()
            except:
                pass


def UpdateData():

    if DATEENT.get() == "" or AKE1ENT.get()=="":
       result = tkMessageBox.showwarning('', 'Please Complete The Required Field-UPDATE', icon="warning")
    else:
        result = tkMessageBox.askquestion('', 'êtes-vous sûr de vouloir mettre à jour les informations?-UPDATE', icon="warning")
    if result == 'yes':
        Scrolledtreeview1.delete(*Scrolledtreeview1.get_children())
        conn = sqlite3.connect("DATABASE/ULD.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE `AKE` SET `DATE` = ?, `FLIGHT` = ?,  DEPART  = ?,DESTINATION  = ?,AKE1  = ?,AKE2  = ?,AKE3  = ?,AKE4  = ?,AKE5  = ?,\
        AKE6  = ?,AKE7  = ?,AKE8  = ?,AKE9  = ?,AKE10  = ?,AKE11  = ?,AKE12  = ?,AKE13  = ?,AKE14  = ?,AKE15  = ? WHERE `mem_id` = ?",
                       (str(DATEENT.get().strip()),str(FLIGHTENT.get().upper().strip()),str(DEPARTENT.get().upper().strip()),str(DESTINATIONENT.get().upper().strip()),\
                        str(AKE1ENT.get().upper().strip()),\
                        str(AKE2ENT.get().upper().strip()),\
                        str(AKE3ENT.get().upper().strip()),\
                        str(AKE4ENT.get().upper().strip()),\
                        str(AKE5ENT.get().upper().strip()),\
                        str(AKE6ENT.get().upper().strip()),\
                        str(AKE7ENT.get().upper().strip()),\
                        str(AKE8ENT.get().upper().strip()),\
                        str(AKE9ENT.get().upper().strip()),\
                        str(AKE10ENT.get().upper().strip()),\
                        str(AKE11ENT.get().upper().strip()),\
                        str(AKE12ENT.get().upper().strip()),\
                        str(AKE13ENT.get().upper().strip()),\
                        str(AKE14ENT.get().upper().strip()),\
                        str(AKE15ENT.get().upper().strip()),int(mem_id)))
        conn.commit()
        cursor.execute("SELECT * FROM `AKE` ORDER BY `mem_id` DESC")
        fetch = cursor.fetchall()
        global count
        count=0
        for data in fetch:
            if count % 2==0:
                Scrolledtreeview1.insert('', 'end', values=(data), tags = ('oddrow'))
            else:
                Scrolledtreeview1.insert('', 'end', values=(data), tags = ('evenrow'))
            count+=1
            child_id = Scrolledtreeview1.get_children()[0]
            Scrolledtreeview1.focus(child_id)
            Scrolledtreeview1.selection_set(child_id)

        try:
            stock()
        except:
            pass
        try:
            history()
        except:
            pass



_bgcolor = '#d9d9d9'  # X11 color: 'gray85'
_fgcolor = '#000000'  # X11 color: 'black'
_compcolor = '#d9d9d9' # X11 color: 'gray85'
_ana1color = '#d9d9d9' # X11 color: 'gray85'
_ana2color = '#ececec' # Closest X11 color: 'gray92'
font9 = "-family {Segoe UI} -size 12 -weight normal -slant "  \
    "roman -underline 0 -overstrike 0"

top=Tk()
top.geometry("1920x1017+130+107")
top.title("New Toplevel")
top.configure(background="white")
# adding window geometry
width_value=top.winfo_screenwidth()
height_value = top.winfo_screenheight()
top.geometry("%dx%d+0+0" % (width_value , height_value))


#style.configure("Blue.TButton", background="blue")
style = ttk.Style()
style.theme_use('clam')#winnative
#style.configure('Blue.TButton', background = 'grey', foreground = 'white', width = 20, borderwidth=1, focusthickness=3, focuscolor='none')
style.map('TButton', background=[('active','light blue')])
style.configure("Red.TLabel", background="#ececec")



FILTERBYDATE=StringVar()
FILTERBYAKE=StringVar()
FILTERBYFLIGHT=StringVar()
FILTERBYDEPART=StringVar()
FILTERBYDESTINATION=StringVar()
filter_var=StringVar()

TFrame1 = Frame(top)
TFrame1.place(relx=0.0, rely=0.0, relheight=0.998, relwidth=0.997)
TFrame1.configure(relief='groove')
TFrame1.configure(borderwidth="2")
TFrame1.configure(relief="groove")
TFrame1.configure(bg="#ffffff")

TOPFRAME = Frame(TFrame1)
TOPFRAME.place(relx=0.0, rely=0.0, relheight=0.054, relwidth=1.0)
TOPFRAME.configure(relief='groove')
TOPFRAME.configure(borderwidth="2")
TOPFRAME.configure(relief="groove")
TOPFRAME.configure(bg="#90897A")
TOPFRAME.configure(bd=0)

_img0 = tk.PhotoImage(file='image/reset2.png')


RESETBTN = ttk.Button(TOPFRAME, style="Blue.TButton")
RESETBTN.configure(takefocus="")
RESETBTN.configure(text='''RESET''')
RESETBTN.configure(image=_img0)
RESETBTN.configure(compound='left')
RESETBTN.configure(command=resetallentry)
RESETBTN.pack(side='left', padx=0, pady=0)

_img1 = tk.PhotoImage(file="image/ajt.png")
ADDBTN = ttk.Button(TOPFRAME)
ADDBTN.configure(takefocus="")
ADDBTN.configure(text='''ADD''')
ADDBTN.configure(image=_img1)
ADDBTN.configure(compound='left')
ADDBTN.configure(command=AddData)
ADDBTN.pack(side='left', padx=0, pady=0)

_img2 = tk.PhotoImage(file="image/update.png")
UPDATEBTN = ttk.Button(TOPFRAME)
UPDATEBTN.configure(takefocus="")
UPDATEBTN.configure(text='''UPDATE''')
UPDATEBTN.configure(image=_img2)
UPDATEBTN.configure(compound='left')
UPDATEBTN.configure(command=UpdateData)
UPDATEBTN.pack(side='left', padx=0, pady=0)

_img3 = tk.PhotoImage(file="image/delete.png")
DELETEBTN = ttk.Button(TOPFRAME)
DELETEBTN.configure(takefocus="")
DELETEBTN.configure(text='''DELETE''')
DELETEBTN.configure(image=_img3)
DELETEBTN.configure(compound='left')
DELETEBTN.configure(command=DeleteData)
DELETEBTN.pack(side='left', padx=0, pady=0)


_img4 = tk.PhotoImage(file="image/Excel.png")
EXCELBTN = ttk.Button(TOPFRAME)
EXCELBTN.configure(takefocus="")
EXCELBTN.configure(text='''EXCEL''')
EXCELBTN.configure(image=_img4)
EXCELBTN.configure(compound='left')
EXCELBTN.configure(command=excel_file)
EXCELBTN.pack(side='right', padx=0, pady=0)

_img5 = tk.PhotoImage(file="image/hl.png")
##HISTORYBTN = ttk.Button(TOPFRAME)
##HISTORYBTN.place(relx=0.843, rely=0.0, height=30, width=100)
##HISTORYBTN.configure(takefocus="")
##HISTORYBTN.configure(text='''HISTORY''')
##HISTORYBTN.configure(image=_img5)
##HISTORYBTN.configure(compound='left')
##HISTORYBTN.configure(command=history)

DATEENT = ttk.Entry(TFrame1)
DATEENT.place(relx=0.016, rely=0.110, relheight=0.031
        , relwidth=0.066)
DATEENT.configure(takefocus="")
DATEENT.configure(cursor="ibeam")
DATEENT.configure()

button_6 = Button(TFrame1,borderwidth=2,highlightthickness=0,command=get_today_date,relief="raised",image=_img5)
button_6.place(relx=0.066,rely=0.110, relheight=0.031, relwidth=0.016)


FLIGHTENT = ttk.Entry(TFrame1)
FLIGHTENT.place(relx=0.089, rely=0.110, relheight=0.031
        , relwidth=0.066)
FLIGHTENT.configure(takefocus="")
FLIGHTENT.configure(cursor="ibeam")

DEPARTENT = ttk.Entry(TFrame1)
DEPARTENT.place(relx=0.162, rely=0.110, relheight=0.031
        , relwidth=0.066)
DEPARTENT.configure(takefocus="")
DEPARTENT.configure(cursor="ibeam")

DESTINATIONENT = ttk.Entry(TFrame1)
DESTINATIONENT.place(relx=0.235, rely=0.110, relheight=0.031
        , relwidth=0.066)
DESTINATIONENT.configure(takefocus="")
DESTINATIONENT.configure(cursor="ibeam")


TLabel3_18RES = ttk.Label(TFrame1,style="Red.TLabel")
TLabel3_18RES.place(relx=0.275, rely=0.069, height=25, width=50)
TLabel3_18RES.configure(foreground="#000000")
TLabel3_18RES.configure(font="-family {Segoe UI} -size 10")
TLabel3_18RES.configure(relief="flat")
TLabel3_18RES.configure(background=('white'))

AKE1ENT = ttk.Entry(TFrame1)
AKE1ENT.place(relx=0.016, rely=0.177, relheight=0.031
        , relwidth=0.066)
AKE1ENT.configure(takefocus="")
AKE1ENT.configure(cursor="ibeam")
AKE1ENT.configure()

AKE2ENT = ttk.Entry(TFrame1)
AKE2ENT.place(relx=0.089, rely=0.177, relheight=0.031
        , relwidth=0.066)
AKE2ENT.configure(takefocus="")
AKE2ENT.configure(cursor="ibeam")

AKE3ENT = ttk.Entry(TFrame1)
AKE3ENT.place(relx=0.162, rely=0.177, relheight=0.031
        , relwidth=0.066)
AKE3ENT.configure(takefocus="")
AKE3ENT.configure(cursor="ibeam")

AKE4ENT = ttk.Entry(TFrame1)
AKE4ENT.place(relx=0.235, rely=0.177, relheight=0.031
        , relwidth=0.066)
AKE4ENT.configure(takefocus="")
AKE4ENT.configure(cursor="ibeam")


AKE5ENT = ttk.Entry(TFrame1)
AKE5ENT.place(relx=0.308, rely=0.177, relheight=0.031
        , relwidth=0.066)
AKE5ENT.configure(takefocus="")
AKE5ENT.configure(cursor="ibeam")


AKE6ENT = ttk.Entry(TFrame1)
AKE6ENT.place(relx=0.016, rely=0.246, relheight=0.031
        , relwidth=0.066)
AKE6ENT.configure(takefocus="")
AKE6ENT.configure(cursor="ibeam")
AKE6ENT.configure()

AKE7ENT = ttk.Entry(TFrame1)
AKE7ENT.place(relx=0.089, rely=0.246, relheight=0.031
        , relwidth=0.066)
AKE7ENT.configure(takefocus="")
AKE7ENT.configure(cursor="ibeam")

AKE8ENT = ttk.Entry(TFrame1)
AKE8ENT.place(relx=0.162, rely=0.246, relheight=0.031
        , relwidth=0.066)
AKE8ENT.configure(takefocus="")
AKE8ENT.configure(cursor="ibeam")

AKE9ENT = ttk.Entry(TFrame1)
AKE9ENT.place(relx=0.235, rely=0.246, relheight=0.031
        , relwidth=0.066)
AKE9ENT.configure(takefocus="")
AKE9ENT.configure(cursor="ibeam")


AKE10ENT = ttk.Entry(TFrame1)
AKE10ENT.place(relx=0.308, rely=0.246, relheight=0.031
        , relwidth=0.066)
AKE10ENT.configure(takefocus="")
AKE10ENT.configure(cursor="ibeam")

AKE11ENT = ttk.Entry(TFrame1)
AKE11ENT.place(relx=0.016, rely=0.315, relheight=0.031
        , relwidth=0.066)
AKE11ENT.configure(takefocus="")
AKE11ENT.configure(cursor="ibeam")
AKE11ENT.configure()

AKE12ENT = ttk.Entry(TFrame1)
AKE12ENT.place(relx=0.089, rely=0.315, relheight=0.031
        , relwidth=0.066)
AKE12ENT.configure(takefocus="")
AKE12ENT.configure(cursor="ibeam")

AKE13ENT = ttk.Entry(TFrame1)
AKE13ENT.place(relx=0.162, rely=0.315, relheight=0.031
        , relwidth=0.066)
AKE13ENT.configure(takefocus="")
AKE13ENT.configure(cursor="ibeam")

AKE14ENT = ttk.Entry(TFrame1)
AKE14ENT.place(relx=0.235, rely=0.315, relheight=0.031
        , relwidth=0.066)
AKE14ENT.configure(takefocus="")
AKE14ENT.configure(cursor="ibeam")

AKE15ENT = ttk.Entry(TFrame1)
AKE15ENT.place(relx=0.308, rely=0.315, relheight=0.031
        , relwidth=0.066)
AKE15ENT.configure(takefocus="")
AKE15ENT.configure(cursor="ibeam")



global _images
_images = (

 tk.PhotoImage("img_close", data='''R0lGODlhDAAMAIQUADIyMjc3Nzk5OT09PT
         8/P0JCQkVFRU1NTU5OTlFRUVZWVmBgYGF hYWlpaXt7e6CgoLm5ucLCwszMzNbW
         1v//////////////////////////////////// ///////////yH5BAEKAB8ALA
         AAAAAMAAwAAAUt4CeOZGmaA5mSyQCIwhCUSwEIxHHW+ fkxBgPiBDwshCWHQfc5
         KkoNUtRHpYYAADs= '''),

 tk.PhotoImage("img_closeactive", data='''R0lGODlhDAAMAIQcALwuEtIzFL46
         INY0Fdk2FsQ8IdhAI9pAIttCJNlKLtpLL9pMMMNTP cVTPdpZQOBbQd60rN+1rf
         Czp+zLxPbMxPLX0vHY0/fY0/rm4vvx8Pvy8fzy8P//////// ///////yH5BAEK
         AB8ALAAAAAAMAAwAAAVHYLQQZEkukWKuxEgg1EPCcilx24NcHGYWFhx P0zANBE
         GOhhFYGSocTsax2imDOdNtiez9JszjpEg4EAaA5jlNUEASLFICEgIAOw== '''),

 tk.PhotoImage("img_closepressed", data='''R0lGODlhDAAMAIQeAJ8nD64qELE
         rELMsEqIyG6cyG7U1HLY2HrY3HrhBKrlCK6pGM7lD LKtHM7pKNL5MNtiViNaon
         +GqoNSyq9WzrNyyqtuzq+O0que/t+bIwubJw+vJw+vTz+zT z////////yH5BAE
         KAB8ALAAAAAAMAAwAAAVJIMUMZEkylGKuwzgc0kPCcgl123NcHWYW Fs6Gp2mYB
         IRgR7MIrAwVDifjWO2WwZzpxkxyfKVCpImMGAeIgQDgVLMHikmCRUpMQgA7 ''')
)

style.element_create("close", "image", "img_close",
       ("active", "pressed", "!disabled", "img_closepressed"),
       ("active", "alternate", "!disabled",
       "img_closeactive"), border=8, sticky='')

style.layout("ClosetabNotebook", [("ClosetabNotebook.client",
                             {"sticky": "nswe"})])
style.layout("ClosetabNotebook.Tab", [
    ("ClosetabNotebook.tab",
      { "sticky": "nswe",
        "children": [
            ("ClosetabNotebook.padding", {
                "side": "top",
                "sticky": "nswe",
                "children": [
                    ("ClosetabNotebook.focus", {
                        "side": "top",
                        "sticky": "nswe",
                        "children": [
                            ("ClosetabNotebook.label", {"side":
                              "left", "sticky": ''}),
                            ("ClosetabNotebook.close", {"side":
                                "left", "sticky": ''}),]})]})]})])

PNOTEBOOK = "ClosetabNotebook" 

style.configure('TNotebook.Tab', background='white')
style.configure('TNotebook.Tab', foreground=_fgcolor)
style.map('TNotebook.Tab', background=
    [('selected', _compcolor), ('active',_ana2color)])

PNotebook1 = ttk.Notebook(TFrame1)
PNotebook1.place(relx=0.700, rely=0.059, relheight=0.327
        , relwidth=0.300)
PNotebook1.configure(takefocus="")
PNotebook1.configure(style=PNOTEBOOK)

PNotebook1_t0 = tk.Frame(PNotebook1)
PNotebook1.add(PNotebook1_t0, padding=3)
PNotebook1.tab(0, text="STOCK",compound="none",underline="-1",)
PNotebook1_t0.configure(background="#A29C90")
PNotebook1_t0.configure(highlightbackground="#D3D3D3")
PNotebook1_t0.configure(highlightcolor="black")

columns=("", "Col1", "Col2","Col3","Col4")


style.configure('Treeview.Heading',  font=font9)

DASHTREE = ttk.Treeview(PNotebook1_t0, columns=columns)
DASHTREE.place(relx=0.015, rely=0.153, relheight=0.817
        , relwidth=0.947)

# build_treeview_support starting.
DASHTREE.heading("#0",text="IjD")
DASHTREE.heading("#0",anchor="center")
DASHTREE.column("#0",width="0")
DASHTREE.column("#0",minwidth="0")
DASHTREE.column("#0",stretch="0")
DASHTREE.column("#0",anchor="c")
DASHTREE.heading("#1",text="DATE")
DASHTREE.heading("#1",anchor="center")
DASHTREE.column("#1",width="120")
DASHTREE.column("#1",minwidth="20")
DASHTREE.column("#1",stretch="1")
DASHTREE.column("#1",anchor="c")

DASHTREE.heading("#2",text="ESCALE")
DASHTREE.heading("#2",anchor="center")
DASHTREE.column("#2",width="120")
DASHTREE.column("#2",minwidth="20")
DASHTREE.column("#2",stretch="1")
DASHTREE.column("#2",anchor="c")

DASHTREE.heading("#3",text="FLIGHT")
DASHTREE.heading("#3",anchor="center")
DASHTREE.column("#3",width="120")
DASHTREE.column("#3",minwidth="20")
DASHTREE.column("#3",stretch="1")
DASHTREE.column("#3",anchor="c")

DASHTREE.heading("#4",text="AKE")
DASHTREE.heading("#4",anchor="center")
DASHTREE.column("#4",width="120")
DASHTREE.column("#4",minwidth="20")
DASHTREE.column("#4",stretch="1")
DASHTREE.column("#4",anchor="c")

DASHTREE.heading("#5",text="AKE")
DASHTREE.heading("#5",anchor="center")
DASHTREE.column("#5",width="0")
DASHTREE.column("#5",minwidth="0")
DASHTREE.column("#5",stretch="0")
DASHTREE.column("#5",anchor="c")


DASHTREE.tag_configure('oddrow', background='white')
DASHTREE.tag_configure('evenrow', background='#ebecf0')


#--------------------------------------------------------------
STOCKBTN = ttk.Button(PNotebook1_t0)
STOCKBTN.configure(takefocus="")
STOCKBTN.configure(text='''Charger''',command=stock,image=_img5)
STOCKBTN.configure(compound='left')
STOCKBTN.place(relx=0.0, rely=0.0, relheight=0.14, relwidth=0.194)

STOCKexcelBTN = ttk.Button(PNotebook1_t0)
STOCKexcelBTN.configure(takefocus="")
STOCKexcelBTN.configure(text='''Excel''',command=stock_excel,image=_img4)
STOCKexcelBTN.configure(compound='left')
STOCKexcelBTN.place(relx=0.2, rely=0.0, relheight=0.14, relwidth=0.198)

STOCKexcelentescale= ttk.Entry(PNotebook1_t0)
STOCKexcelentescale.place(relx=0.42, rely=0.03, relheight=0.1, relwidth=0.15)


STOCKexcelent = ttk.Entry(PNotebook1_t0)
STOCKexcelent.place(relx=0.72, rely=0.03, relheight=0.1, relwidth=0.15)


STOCKexcelentescalelabel= tk.Label(PNotebook1_t0,text="",font='arial 17',bg='#D3D3D3',background='#A29C90')
STOCKexcelentescalelabel.place(relx=0.62, rely=-0.01)

STOCKexcelentescalelabel= tk.Label(PNotebook1_t0,text="",font='arial 17',bg='#D3D3D3',background='#A29C90')
STOCKexcelentescalelabel.place(relx=0.62, rely=-0.01)




#---------------------------h/s-------------------------------
PNotebook1_t2 = tk.Frame(PNotebook1)
PNotebook1.add(PNotebook1_t2, padding=3)
PNotebook1.tab(1, text="AKE HORS ",compound="none",underline="-1",)
PNotebook1_t2.configure(background="#A29C90")
PNotebook1_t2.configure(highlightbackground="#D3D3D3")
PNotebook1_t2.configure(highlightcolor="black")

columns=("", "Col1", "Col2","Col3")


style.configure('Treeview.Heading',  font=font9)

HSTREE = ttk.Treeview(PNotebook1_t2, columns=columns)
HSTREE.place(relx=0.015, rely=0.153, relheight=0.817
        , relwidth=0.947)



# build_treeview_support starting.
HSTREE.heading("#0",text="IjD")
HSTREE.heading("#0",anchor="center")
HSTREE.column("#0",width="0")
HSTREE.column("#0",minwidth="0")
HSTREE.column("#0",stretch="0")
HSTREE.column("#0",anchor="c")
HSTREE.heading("#1",text="DATE")
HSTREE.heading("#1",anchor="center")
HSTREE.column("#1",width="80")
HSTREE.column("#1",minwidth="20")
HSTREE.column("#1",stretch="1")
HSTREE.column("#1",anchor="c")

HSTREE.heading("#2",text="ESCALE")
HSTREE.heading("#2",anchor="center")
HSTREE.column("#2",width="80")
HSTREE.column("#2",minwidth="20")
HSTREE.column("#2",stretch="1")
HSTREE.column("#2",anchor="c")

HSTREE.heading("#3",text="AKE")
HSTREE.heading("#3",anchor="center")
HSTREE.column("#3",width="80")
HSTREE.column("#3",minwidth="20")
HSTREE.column("#3",stretch="1")
HSTREE.column("#3",anchor="c")

HSTREE.heading("#4",text="STATUT")
HSTREE.heading("#4",anchor="center")
HSTREE.column("#4",width="80")
HSTREE.column("#4",minwidth="20")
HSTREE.column("#4",stretch="1")
HSTREE.column("#4",anchor="c")


HSTREE.tag_configure('oddrow', background='white')
HSTREE.tag_configure('evenrow', background='#ebecf0')

HSBTN = ttk.Button(PNotebook1_t2)
HSBTN.configure(takefocus="")
HSBTN.configure(text='''Charger''',command='',image=_img5)
HSBTN.configure(compound='left')
HSBTN.place(relx=0.0, rely=0.0, relheight=0.14, relwidth=0.194)

STOCKexcelBTN = ttk.Button(PNotebook1_t2)
STOCKexcelBTN.configure(takefocus="")
STOCKexcelBTN.configure(text='''Excel''',command='',image=_img4)
STOCKexcelBTN.configure(compound='left')
STOCKexcelBTN.place(relx=0.2, rely=0.0, relheight=0.14, relwidth=0.198)

ESCALEHS= ttk.Entry(PNotebook1_t2)
ESCALEHS.place(relx=0.42, rely=0.03, relheight=0.1, relwidth=0.15)


AKEHS = ttk.Entry(PNotebook1_t2)
AKEHS.place(relx=0.72, rely=0.03, relheight=0.1, relwidth=0.15)


#---------------------------------------------------------------------------------------------


#--------------------------------------RECAP-----------------------------------


PNotebook1 = ttk.Notebook(TFrame1)
PNotebook1.place(relx=0.393, rely=0.06, relheight=0.325
        , relwidth=0.300)
PNotebook1.configure(takefocus="")
PNotebook1.configure(style=PNOTEBOOK)

PNotebook1_t0 = tk.Frame(PNotebook1)
PNotebook1.add(PNotebook1_t0, padding=3)
PNotebook1.tab(0, text="RECAP",compound="none",underline="-1",)
PNotebook1_t0.configure(background="#A29C90")
PNotebook1_t0.configure(highlightbackground="#D3D3D3")
PNotebook1_t0.configure(highlightcolor="black")

columns=("", "Col1", "Col2","Col3")

style.configure('Treeview.Heading',  font=font9)
DASHTREE3 = ttk.Treeview(PNotebook1_t0, columns=columns)
DASHTREE3.place(relx=0.015, rely=0.153, relheight=0.817
        , relwidth=0.947)

DASHTREE3.tag_configure('oddrow', background='white')
DASHTREE3.tag_configure('evenrow', background='red')


# build_treeview_support starting.
DASHTREE3.heading("#0",text="IjD")
DASHTREE3.heading("#0",anchor="center")
DASHTREE3.column("#0",width="0")
DASHTREE3.column("#0",minwidth="0")
DASHTREE3.column("#0",stretch="0")
DASHTREE3.column("#0",anchor="c")
DASHTREE3.heading("#1",text="DATE")
DASHTREE3.heading("#1",anchor="center")
DASHTREE3.column("#1",width="120")
DASHTREE3.column("#1",minwidth="20")
DASHTREE3.column("#1",stretch="1")
DASHTREE3.column("#1",anchor="c")

DASHTREE3.heading("#2",text="ESCALE")
DASHTREE3.heading("#2",anchor="center")
DASHTREE3.column("#2",width="120")
DASHTREE3.column("#2",minwidth="20")
DASHTREE3.column("#2",stretch="1")
DASHTREE3.column("#2",anchor="c")

DASHTREE3.heading("#3",text="AKE")
DASHTREE3.heading("#3",anchor="center")
DASHTREE3.column("#3",width="120")
DASHTREE3.column("#3",minwidth="20")
DASHTREE3.column("#3",stretch="1")
DASHTREE3.column("#3",anchor="c")

DASHTREE3.heading("#4",text="AKE")
DASHTREE3.heading("#4",anchor="center")
DASHTREE3.column("#4",width="0")
DASHTREE3.column("#4",minwidth="0")
DASHTREE3.column("#4",stretch="0")
DASHTREE3.column("#4",anchor="c")




##recapresetBTNe = ttk.Button(PNotebook1_t0)
##recapresetBTNe.configure(takefocus="")
##recapresetBTNe.configure(text='''Charger''',command='',image=_img5)
##recapresetBTNe.configure(compound='left')
##recapresetBTNe.place(relx=0.0, rely=0.0, relheight=0.14, relwidth=0.194)
##
recapexcelbtn = ttk.Button(PNotebook1_t0)
recapexcelbtn.configure(takefocus="")
recapexcelbtn.configure(text='''Excel''',command=sumrary_excel,image=_img4)
recapexcelbtn.configure(compound='left')
recapexcelbtn.place(relx=0.0, rely=0.0, relheight=0.11, relwidth=0.144)
##
##STOCKexcelentte = ttk.Entry(PNotebook1_t0)
##STOCKexcelentte.place(relx=0.42, rely=0.03, relheight=0.1, relwidth=0.15)
##
##nbreakefsearchent = ttk.Entry(PNotebook1_t0)
##nbreakefsearchent.place(relx=0.72, rely=0.03, relheight=0.1, relwidth=0.15)
##



# Define custom styles for the labels
style = ttk.Style()
style.configure("Serviceable.TLabel", font=("bruce forever", 24, "bold"), foreground="green", background="#90897A", relief="flat")
style.configure("Unserviceable.TLabel", font=("bruce forever", 24, "bold"), foreground="red", background="#90897A", relief="flat")

### Unserviceable AKE Label
totalakehslabel = ttk.Label(TOPFRAME, style="Unserviceable.TLabel", text="")
totalakehslabel.pack(side='right', padx=30)


# Serviceable AKE Label
totalakeactivelabel = ttk.Label(TOPFRAME, style="Serviceable.TLabel", text="")
totalakeactivelabel.pack(side='right', padx=10)


#-------------------------------------------------------------------------

#-------------------------------------------HISTORIQUE-------------------------------------------------
PNotebook4 = ttk.Notebook(TFrame1)
PNotebook4.place(relx=0.700, rely=0.395, relheight=0.3
        , relwidth=0.300)
PNotebook4.configure(takefocus="")
PNotebook4.configure(style=PNOTEBOOK)

PNotebook1_t1 = tk.Frame(PNotebook4)
PNotebook4.add(PNotebook1_t1, padding=3)
PNotebook4.tab(0, text="HISTORIQUE AKE",compound="none",underline="-1",)
PNotebook1_t1.configure(background="#A29C90")
PNotebook1_t1.configure(highlightbackground="#D3D3D3")
PNotebook1_t1.configure(highlightcolor="black")



columns=("", "Col1", "Col2","Col3","Col4")

style.configure('Treeview.Heading',  font=font9)
DASHTREE2 = ttk.Treeview(PNotebook1_t1, columns=columns)
DASHTREE2.place(relx=0.015, rely=0.153, relheight=0.817
        , relwidth=0.947)

DASHTREE2.tag_configure('oddrow', background='white')
DASHTREE2.tag_configure('evenrow', background='red')


# build_treeview_support starting.
DASHTREE2.heading("#0",text="IjD")
DASHTREE2.heading("#0",anchor="center")
DASHTREE2.column("#0",width="0")
DASHTREE2.column("#0",minwidth="0")
DASHTREE2.column("#0",stretch="0")
DASHTREE2.column("#0",anchor="c")
DASHTREE2.heading("#1",text="DATE")
DASHTREE2.heading("#1",anchor="center")
DASHTREE2.column("#1",width="120")
DASHTREE2.column("#1",minwidth="20")
DASHTREE2.column("#1",stretch="1")
DASHTREE2.column("#1",anchor="c")

DASHTREE2.heading("#2",text="ESCALE")
DASHTREE2.heading("#2",anchor="center")
DASHTREE2.column("#2",width="120")
DASHTREE2.column("#2",minwidth="20")
DASHTREE2.column("#2",stretch="1")
DASHTREE2.column("#2",anchor="c")

DASHTREE2.heading("#3",text="FLIGHT")
DASHTREE2.heading("#3",anchor="center")
DASHTREE2.column("#3",width="120")
DASHTREE2.column("#3",minwidth="20")
DASHTREE2.column("#3",stretch="1")
DASHTREE2.column("#3",anchor="c")

DASHTREE2.heading("#4",text="AKE")
DASHTREE2.heading("#4",anchor="center")
DASHTREE2.column("#4",width="120")
DASHTREE2.column("#4",minwidth="100")
DASHTREE2.column("#4",stretch="1")
DASHTREE2.column("#4",anchor="c")

DASHTREE2.heading("#5",text="AKE")
DASHTREE2.heading("#5",anchor="center")
DASHTREE2.column("#5",width="0")
DASHTREE2.column("#5",minwidth="0")
DASHTREE2.column("#5",stretch="0")
DASHTREE2.column("#5",anchor="c")


histobtnBTN = ttk.Button(PNotebook1_t1)
histobtnBTN.configure(takefocus="")
histobtnBTN.configure(text='''Charger''',command=history,image=_img5)
histobtnBTN.configure(compound='left')
histobtnBTN.place(relx=0.0, rely=0.0, relheight=0.14, relwidth=0.194)

STOCKexcelBTN = ttk.Button(PNotebook1_t1)
STOCKexcelBTN.configure(takefocus="")
STOCKexcelBTN.configure(text='''Excel''',command=history_excel,image=_img4)
STOCKexcelBTN.configure(compound='left')
STOCKexcelBTN.place(relx=0.2, rely=0.0, relheight=0.14, relwidth=0.198)

STOCKexcelentt = ttk.Entry(PNotebook1_t1)
STOCKexcelentt.place(relx=0.42, rely=0.03, relheight=0.1, relwidth=0.15)

historiqueake = ttk.Entry(PNotebook1_t1)
historiqueake.place(relx=0.72, rely=0.03, relheight=0.1, relwidth=0.15)
#-----------------------------programme--------------------------

PNotebook3 = ttk.Notebook(TFrame1)
PNotebook3.place(relx=0.700, rely=0.699, relheight=0.300
        , relwidth=0.300)
PNotebook3.configure(takefocus="")
PNotebook3.configure(style=PNOTEBOOK)

PNotebook1_t0 = tk.Frame(PNotebook3)
PNotebook3.add(PNotebook1_t0, padding=3)
PNotebook3.tab(0, text="PROGRAMME",compound="none",underline="-1",)
PNotebook1_t0.configure(background="#A29C90")
PNotebook1_t0.configure(highlightbackground="#D3D3D3")
PNotebook1_t0.configure(highlightcolor="black")



style.configure('Treeview.Heading',  font=font9)
style.map("Treeview", background=[("selected", "#0078D7")])
PROGTREE = ttk.Treeview(PNotebook1_t0)
PROGTREE.place(relx=0.015, rely=0.153, relheight=0.817
        , relwidth=0.947)

PROGTREE.tag_configure('oddrow', background='white')
PROGTREE.tag_configure('evenrow', background='#ebecf0')


#--------------------------------------------------------------
try:
    LOADPROGBTN = ttk.Button(PNotebook1_t0)
    LOADPROGBTN.configure(takefocus="")
    LOADPROGBTN.configure(text='''Charger''',image=_img5,command=process_flight_data)
    LOADPROGBTN.configure(compound='left')
    LOADPROGBTN.place(relx=0.0, rely=0.02, relheight=0.11, relwidth=0.144)
except:
    pass
try:
    EXCELPROG = ttk.Button(PNotebook1_t0)
    EXCELPROG.configure(takefocus="")
    EXCELPROG.configure(text='''Excel''',command=open_programme_excel,image=_img4)
    EXCELPROG.configure(compound='left')
    EXCELPROG.place(relx=0.2, rely=0.02, relheight=0.11, relwidth=0.148)
except:
    pass

filter_entry = tk.Entry(PNotebook1_t0, textvariable=filter_var)
filter_entry.place(relx=0.7, rely=0.02, relheight=0.11, relwidth=0.148)
filter_entry.bind("<KeyRelease>", lambda event: filter_treeview())  # Update on key release



#------------------------fin de programme------------------------------------------------------------------------













TREEFRAME = Frame(TFrame1)
TREEFRAME.place(relx=0.01, rely=0.394, relheight=0.606
        , relwidth=0.6845)
TREEFRAME.configure(relief='groove')
TREEFRAME.configure(bg='#A29C90')
TREEFRAME.configure(borderwidth="2")
TREEFRAME.configure(relief="groove")
columns=("", "Col1", "Col2","Col3","Col4","Col5","Col6","Col7","Col8","Col9","Col10","Co12","Co13","Co14","Co15","Co16","Co17","Co18","Co19","Co20")
Scrolledtreeview1 = ttk.Treeview(TREEFRAME, columns=columns)
Scrolledtreeview1.place(relx=0.005, rely=0.098, relheight=0.889
        , relwidth=0.992)


Scrolledtreeview1.heading("#0",text="id")
Scrolledtreeview1.heading("#0",anchor="center")
Scrolledtreeview1.column("#0",width="0")
Scrolledtreeview1.column("#0",minwidth="0")
Scrolledtreeview1.column("#0",stretch="0")

Scrolledtreeview1.heading("#1",text="ID")
Scrolledtreeview1.heading("#1",anchor="center")
Scrolledtreeview1.column("#1",width="0")
Scrolledtreeview1.column("#1",minwidth="0")
Scrolledtreeview1.column("#1",stretch="0")

Scrolledtreeview1.heading("#2",text="DATE")
Scrolledtreeview1.heading("#2",anchor="center")
Scrolledtreeview1.column("#2",width="100")
Scrolledtreeview1.column("#2",minwidth="20")
Scrolledtreeview1.column("#2",stretch="1")
Scrolledtreeview1.column("#2",anchor="c")

Scrolledtreeview1.heading("#3",text="FLIGHT")
Scrolledtreeview1.heading("#3",anchor="center")
Scrolledtreeview1.column("#3",width="100")
Scrolledtreeview1.column("#3",minwidth="20")
Scrolledtreeview1.column("#3",stretch="1")
Scrolledtreeview1.column("#3",anchor="c")

Scrolledtreeview1.heading("#4",text="DEPART")
Scrolledtreeview1.heading("#4",anchor="center")
Scrolledtreeview1.column("#4",width="100")
Scrolledtreeview1.column("#4",minwidth="20")
Scrolledtreeview1.column("#4",stretch="1")
Scrolledtreeview1.column("#4",anchor="c")

Scrolledtreeview1.heading("#5",text="DEST")
Scrolledtreeview1.heading("#5",anchor="center")
Scrolledtreeview1.column("#5",width="80")
Scrolledtreeview1.column("#5",minwidth="20")
Scrolledtreeview1.column("#5",stretch="1")
Scrolledtreeview1.column("#5",anchor="c")

Scrolledtreeview1.heading("#6",text="AKE1")
Scrolledtreeview1.heading("#6",anchor="center")
Scrolledtreeview1.column("#6",width="60")
Scrolledtreeview1.column("#6",minwidth="20")
Scrolledtreeview1.column("#6",stretch="1")
Scrolledtreeview1.column("#6",anchor="c")

Scrolledtreeview1.heading("#7",text="AKE2")
Scrolledtreeview1.heading("#7",anchor="center")
Scrolledtreeview1.column("#7",width="60")
Scrolledtreeview1.column("#7",minwidth="20")
Scrolledtreeview1.column("#7",stretch="1")
Scrolledtreeview1.column("#7",anchor="c")
Scrolledtreeview1.heading("#8",text="AKE3")
Scrolledtreeview1.heading("#8",anchor="center")
Scrolledtreeview1.column("#8",width="60")
Scrolledtreeview1.column("#8",minwidth="20")
Scrolledtreeview1.column("#8",stretch="1")
Scrolledtreeview1.column("#8",anchor="c")

Scrolledtreeview1.heading("#9",text="AKE4")
Scrolledtreeview1.heading("#9",anchor="center")
Scrolledtreeview1.column("#9",width="60")
Scrolledtreeview1.column("#9",minwidth="20")
Scrolledtreeview1.column("#9",stretch="1")
Scrolledtreeview1.column("#9",anchor="c")

Scrolledtreeview1.heading("#10",text="AKE5")
Scrolledtreeview1.heading("#10",anchor="center")
Scrolledtreeview1.column("#10",width="60")
Scrolledtreeview1.column("#10",minwidth="20")
Scrolledtreeview1.column("#10",stretch="1")
Scrolledtreeview1.column("#10",anchor="c")

Scrolledtreeview1.heading("#11",text="AKE6")
Scrolledtreeview1.heading("#11",anchor="center")
Scrolledtreeview1.column("#11",width="60")
Scrolledtreeview1.column("#11",minwidth="20")
Scrolledtreeview1.column("#11",stretch="1")
Scrolledtreeview1.column("#11",anchor="c")

Scrolledtreeview1.heading("#12",text="AKE7")
Scrolledtreeview1.heading("#12",anchor="center")
Scrolledtreeview1.column("#12",width="60")
Scrolledtreeview1.column("#12",minwidth="20")
Scrolledtreeview1.column("#12",stretch="1")
Scrolledtreeview1.column("#12",anchor="c")

Scrolledtreeview1.heading("#13",text="AKE8")
Scrolledtreeview1.heading("#13",anchor="center")
Scrolledtreeview1.column("#13",width="60")
Scrolledtreeview1.column("#13",minwidth="20")
Scrolledtreeview1.column("#13",stretch="1")
Scrolledtreeview1.column("#13",anchor="c")

Scrolledtreeview1.heading("#14",text="AKE9")
Scrolledtreeview1.heading("#14",anchor="center")
Scrolledtreeview1.column("#14",width="60")
Scrolledtreeview1.column("#14",minwidth="20")
Scrolledtreeview1.column("#14",stretch="1")
Scrolledtreeview1.column("#14",anchor="c")

Scrolledtreeview1.heading("#15",text="AKE10")
Scrolledtreeview1.heading("#15",anchor="center")
Scrolledtreeview1.column("#15",width="60")
Scrolledtreeview1.column("#15",minwidth="20")
Scrolledtreeview1.column("#15",stretch="1")
Scrolledtreeview1.column("#15",anchor="c")

Scrolledtreeview1.heading("#16",text="AKE11")
Scrolledtreeview1.heading("#16",anchor="center")
Scrolledtreeview1.column("#16",width="60")
Scrolledtreeview1.column("#16",minwidth="20")
Scrolledtreeview1.column("#16",stretch="1")
Scrolledtreeview1.column("#16",anchor="c")

Scrolledtreeview1.heading("#17",text="AKE12")
Scrolledtreeview1.heading("#17",anchor="center")
Scrolledtreeview1.column("#17",width="60")
Scrolledtreeview1.column("#17",minwidth="20")
Scrolledtreeview1.column("#17",stretch="1")
Scrolledtreeview1.column("#17",anchor="c")

Scrolledtreeview1.heading("#18",text="AKE13")
Scrolledtreeview1.heading("#18",anchor="center")
Scrolledtreeview1.column("#18",width="60")
Scrolledtreeview1.column("#18",minwidth="20")
Scrolledtreeview1.column("#18",stretch="1")
Scrolledtreeview1.column("#18",anchor="c")

Scrolledtreeview1.heading("#19",text="AKE14")
Scrolledtreeview1.heading("#19",anchor="center")
Scrolledtreeview1.column("#19",width="60")
Scrolledtreeview1.column("#19",minwidth="20")
Scrolledtreeview1.column("#19",stretch="1")
Scrolledtreeview1.column("#19",anchor="c")

Scrolledtreeview1.heading("#20",text="AKE15")
Scrolledtreeview1.heading("#20",anchor="center")
Scrolledtreeview1.column("#20",width="60")
Scrolledtreeview1.column("#20",minwidth="20")
Scrolledtreeview1.column("#20",stretch="1")
Scrolledtreeview1.column("#20",anchor="c")

Scrolledtreeview1.tag_configure('oddrow', background='white')
Scrolledtreeview1.tag_configure('evenrow', background='#ebecf0')





DATEFILTER = ttk.Entry(TREEFRAME)
DATEFILTER.place(relx=0.011, rely=0.033, relheight=0.054
        , relwidth=0.0651)
DATEFILTER.configure(takefocus="")
DATEFILTER.configure(cursor="ibeam")
DATEFILTER.configure(textvariable=FILTERBYDATE)

FLIGHTFILTER = ttk.Entry(TREEFRAME)
FLIGHTFILTER.place(relx=0.0903, rely=0.033, relheight=0.054
        , relwidth=0.0651)
FLIGHTFILTER.configure(takefocus="")
FLIGHTFILTER.configure(cursor="ibeam",textvariable=FILTERBYFLIGHT)

DEPARTFILTER = ttk.Entry(TREEFRAME)
DEPARTFILTER.place(relx=0.1686, rely=0.033, relheight=0.054
        , relwidth=0.0651)
DEPARTFILTER.configure(takefocus="")
DEPARTFILTER.configure(cursor="ibeam",textvariable=FILTERBYDEPART)

DESTINATIONFILTER = ttk.Entry(TREEFRAME)
DESTINATIONFILTER.place(relx=0.2449, rely=0.033, relheight=0.054
        , relwidth=0.0511)
DESTINATIONFILTER.configure(takefocus="")
DESTINATIONFILTER.configure(cursor="ibeam",textvariable=FILTERBYDESTINATION)

AKEFILTER = ttk.Entry(TREEFRAME)
AKEFILTER.place(relx=0.302, rely=0.033, relheight=0.054
        , relwidth=0.040)
AKEFILTER.configure(takefocus="")
AKEFILTER.configure(cursor="ibeam",textvariable=FILTERBYAKE)


_img6 = tk.PhotoImage(file="image/filter.png")
TButton1 = ttk.Button(TREEFRAME)
TButton1.place(relx=0.35, rely=0.018, height=30, width=30)
TButton1.configure(takefocus="")
TButton1.configure(text='''Tbutton''')
TButton1.configure(image=_img6)
TButton1.configure(command=resetfilter)

TLabel3 = ttk.Label(TFrame1,style="Red.TLabel")
TLabel3.place(relx=0.016, rely=0.069, height=20, width=41)

TLabel3.configure(foreground="#000000")
TLabel3.configure(background="white")
TLabel3.configure(font=font9)
TLabel3.configure(relief="flat")
TLabel3.configure(text='''DATE''')

TLabel3_17 = ttk.Label(TFrame1,style="Red.TLabel")
TLabel3_17.place(relx=0.089, rely=0.069, height=25, width=55)

TLabel3_17.configure(foreground="#000000")
TLabel3_17.configure(font="-family {Segoe UI} -size 12")
TLabel3_17.configure(relief="flat")
TLabel3_17.configure(text='''FLIGHT''')
TLabel3_17.configure(background="white")

TLabel3_18 = ttk.Label(TFrame1,style="Red.TLabel")
TLabel3_18.place(relx=0.162, rely=0.069, height=20, width=70)
TLabel3_18.configure(foreground="#000000")
TLabel3_18.configure(font="-family {Segoe UI} -size 12")
TLabel3_18.configure(relief="flat")
TLabel3_18.configure(text='''DEPART''')
TLabel3_18.configure(background="white")

DEPARTRES = ttk.Label(TFrame1,style="Red.TLabel")
DEPARTRES.place(relx=0.2, rely=0.072, height=20, width=45)

DEPARTRES.configure(foreground="#000000")
DEPARTRES.configure(font="-family {Segoe UI} -size 10")
DEPARTRES.configure(relief="flat")
DEPARTRES.configure(background="white")

TLabel3_18 = ttk.Label(TFrame1,style="Red.TLabel")
TLabel3_18.place(relx=0.235, rely=0.069, height=20, width=50)
TLabel3_18.configure(foreground="#000000")
TLabel3_18.configure(font="-family {Segoe UI} -size 12")
TLabel3_18.configure(relief="flat")
TLabel3_18.configure(text='''DEST''')
TLabel3_18.configure(background="white")



TLabel3_18 = ttk.Label(TFrame1,style="Red.TLabel")
TLabel3_18.place(relx=0.235, rely=0.142, height=20, width=45)
TLabel3_18.configure(foreground="#000000")
TLabel3_18.configure(font="-family {Segoe UI} -size 12")
TLabel3_18.configure(relief="flat")
TLabel3_18.configure(text='''AKE4''')
TLabel3_18.configure(background="white")

AKE4RES = ttk.Label(TFrame1,style="Red.TLabel")
AKE4RES.place(relx=0.269, rely=0.142, height=20, width=45)
AKE4RES.configure(foreground="#000000")
AKE4RES.configure(font="-family {Segoe UI} -size 10")
AKE4RES.configure(relief="flat")
AKE4RES.configure(background="white")


TLabel3_18 = ttk.Label(TFrame1,style="Red.TLabel")
TLabel3_18.place(relx=0.162, rely=0.142, height=20, width=45)
TLabel3_18.configure(foreground="#000000")
TLabel3_18.configure(font="-family {Segoe UI} -size 12")
TLabel3_18.configure(relief="flat")
TLabel3_18.configure(text='''AKE3''')
TLabel3_18.configure(background="white")

AKE3RES = ttk.Label(TFrame1,style="Red.TLabel")
AKE3RES.place(relx=0.196, rely=0.142, height=20, width=45)
AKE3RES.configure(foreground="#000000")
AKE3RES.configure(font="-family {Segoe UI} -size 10")
AKE3RES.configure(relief="flat")
AKE3RES.configure(background="white")


TLabel3_18 = ttk.Label(TFrame1,style="Red.TLabel")
TLabel3_18.place(relx=0.089, rely=0.142, height=20, width=45)
TLabel3_18.configure(foreground="#000000")
TLabel3_18.configure(font="-family {Segoe UI} -size 12")
TLabel3_18.configure(relief="flat")
TLabel3_18.configure(text='''AKE2''')
TLabel3_18.configure(background="white")



AKE2RES = ttk.Label(TFrame1,style="Red.TLabel")
AKE2RES.place(relx=0.127, rely=0.142, height=20, width=45)
AKE2RES.configure(foreground="#000000")
AKE2RES.configure(font="-family {Segoe UI} -size 10")
AKE2RES.configure(relief="flat")
AKE2RES.configure(background="white")


TLabel3_18 = ttk.Label(TFrame1,style="Red.TLabel")
TLabel3_18.place(relx=0.016, rely=0.142, height=20, width=45)
TLabel3_18.configure(foreground="#000000")
TLabel3_18.configure(font="-family {Segoe UI} -size 12")
TLabel3_18.configure(relief="flat")
TLabel3_18.configure(text='''AKE1''')
TLabel3_18.configure(background="white")


AKE1RES = ttk.Label(TFrame1,style="Red.TLabel")
AKE1RES.place(relx=0.046, rely=0.142, height=20, width=45)
AKE1RES.configure(foreground="#000000")
AKE1RES.configure(font="-family {Segoe UI} -size 10")
AKE1RES.configure(relief="flat")
AKE1RES.configure(background="white")

TLabel3_16 = ttk.Label(TFrame1,style="Red.TLabel")
TLabel3_16.place(relx=0.308, rely=0.142, height=20, width=45)
TLabel3_16.configure(foreground="#000000")
TLabel3_16.configure(font="-family {Segoe UI} -size 12")
TLabel3_16.configure(relief="flat")
TLabel3_16.configure(text='''AKE5''')
TLabel3_16.configure(background="white")

AKE5RES = ttk.Label(TFrame1,style="Red.TLabel")
AKE5RES.place(relx=0.341, rely=0.142, height=20, width=45)
AKE5RES.configure(foreground="#000000")
AKE5RES.configure(font="-family {Segoe UI} -size 10")
AKE5RES.configure(relief="flat")
AKE5RES.configure(background="white")



TLabel3_18 = ttk.Label(TFrame1,style="Red.TLabel")
TLabel3_18.place(relx=0.016, rely=0.209, height=20, width=45)
TLabel3_18.configure(foreground="#000000")
TLabel3_18.configure(font="-family {Segoe UI} -size 12")
TLabel3_18.configure(relief="flat")
TLabel3_18.configure(text='''AKE6''')
TLabel3_18.configure(background="white")


AKE6RES = ttk.Label(TFrame1,style="Red.TLabel")
AKE6RES.place(relx=0.046, rely=0.209, height=20, width=45)
AKE6RES.configure(foreground="#000000")
AKE6RES.configure(font="-family {Segoe UI} -size 12")
AKE6RES.configure(relief="flat")
AKE6RES.configure(background="white")



TLabel3_18 = ttk.Label(TFrame1,style="Red.TLabel")
TLabel3_18.place(relx=0.089, rely=0.209, height=20, width=45)
TLabel3_18.configure(foreground="#000000")
TLabel3_18.configure(font="-family {Segoe UI} -size 12")
TLabel3_18.configure(relief="flat")
TLabel3_18.configure(text='''AKE7''')
TLabel3_18.configure(background="white")


AKE7RES = ttk.Label(TFrame1,style="Red.TLabel")
AKE7RES.place(relx=0.119, rely=0.209, height=20, width=45)
AKE7RES.configure(foreground="#000000")
AKE7RES.configure(font="-family {Segoe UI} -size 12")
AKE7RES.configure(relief="flat")
AKE7RES.configure(background="white")



TLabel3_18 = ttk.Label(TFrame1,style="Red.TLabel")
TLabel3_18.place(relx=0.162, rely=0.209, height=20, width=45)
TLabel3_18.configure(foreground="#000000")
TLabel3_18.configure(font="-family {Segoe UI} -size 12")
TLabel3_18.configure(relief="flat")
TLabel3_18.configure(text='''AKE8''')
TLabel3_18.configure(background="white")


AKE8RES = ttk.Label(TFrame1,style="Red.TLabel")
AKE8RES.place(relx=0.192, rely=0.209, height=20, width=45)
AKE8RES.configure(foreground="#000000")
AKE8RES.configure(font="-family {Segoe UI} -size 12")
AKE8RES.configure(relief="flat")
AKE8RES.configure(background="white")


TLabel3_18 = ttk.Label(TFrame1,style="Red.TLabel")
TLabel3_18.place(relx=0.235, rely=0.209, height=25, width=45)
TLabel3_18.configure(foreground="#000000")
TLabel3_18.configure(font="-family {Segoe UI} -size 12")
TLabel3_18.configure(relief="flat")
TLabel3_18.configure(text='''AKE9''')
TLabel3_18.configure(background="white")


AKE9RES = ttk.Label(TFrame1,style="Red.TLabel")
AKE9RES.place(relx=0.265, rely=0.209, height=25, width=45)
AKE9RES.configure(foreground="#000000")
AKE9RES.configure(font="-family {Segoe UI} -size 12")
AKE9RES.configure(relief="flat")
AKE9RES.configure(background="white")


TLabel3_18 = ttk.Label(TFrame1,style="Red.TLabel")
TLabel3_18.place(relx=0.235, rely=0.278, height=20, width=55)
TLabel3_18.configure(foreground="#000000")
TLabel3_18.configure(font="-family {Segoe UI} -size 12")
TLabel3_18.configure(relief="flat")
TLabel3_18.configure(text='''AKE14''')
TLabel3_18.configure(background="white")


AKE14RES = ttk.Label(TFrame1,style="Red.TLabel")
AKE14RES.place(relx=0.27, rely=0.278, height=20, width=55)
AKE14RES.configure(foreground="#000000")
AKE14RES.configure(font="-family {Segoe UI} -size 10")
AKE14RES.configure(relief="flat")
AKE14RES.configure(background="white")

TLabel3_18 = ttk.Label(TFrame1,style="Red.TLabel")
TLabel3_18.place(relx=0.162, rely=0.278, height=20, width=55)
TLabel3_18.configure(foreground="#000000")
TLabel3_18.configure(font="-family {Segoe UI} -size 12")
TLabel3_18.configure(relief="flat")
TLabel3_18.configure(text='''AKE13''')
TLabel3_18.configure(background="white")


AKE13RES = ttk.Label(TFrame1,style="Red.TLabel")
AKE13RES.place(relx=0.197, rely=0.278, height=20, width=55)
AKE13RES.configure(foreground="#000000")
AKE13RES.configure(font="-family {Segoe UI} -size 10")
AKE13RES.configure(relief="flat")
AKE13RES.configure(background="white")



TLabel3_18 = ttk.Label(TFrame1,style="Red.TLabel")
TLabel3_18.place(relx=0.089, rely=0.278, height=20, width=55)
TLabel3_18.configure(foreground="#000000")
TLabel3_18.configure(font="-family {Segoe UI} -size 12")
TLabel3_18.configure(relief="flat")
TLabel3_18.configure(text='''AKE12''')
TLabel3_18.configure(background="white")


AKE12RES = ttk.Label(TFrame1,style="Red.TLabel")
AKE12RES.place(relx=0.124, rely=0.278, height=20, width=40)
AKE12RES.configure(foreground="#000000")
AKE12RES.configure(font="-family {Segoe UI} -size 10")
AKE12RES.configure(relief="flat")
AKE12RES.configure(background="white")



TLabel3_18 = ttk.Label(TFrame1,style="Red.TLabel")
TLabel3_18.place(relx=0.016, rely=0.278, height=20, width=65)
TLabel3_18.configure(foreground="#000000")
TLabel3_18.configure(font="-family {Segoe UI} -size 12")
TLabel3_18.configure(relief="flat")
TLabel3_18.configure(text='''AKE11''')
TLabel3_18.configure(background="white")


AKE11RES = ttk.Label(TFrame1,style="Red.TLabel")
AKE11RES.place(relx=0.05, rely=0.278, height=20, width=50)
AKE11RES.configure(foreground="#000000")
AKE11RES.configure(font="-family {Segoe UI} -size 10")
AKE11RES.configure(relief="flat")
AKE11RES.configure(background="white")



TLabel3_14 = ttk.Label(TFrame1,style="Red.TLabel")
TLabel3_14.place(relx=0.31, rely=0.209, height=20, width=60)
TLabel3_14.configure(foreground="#000000")
TLabel3_14.configure(font="-family {Segoe UI} -size 12")
TLabel3_14.configure(relief="flat")
TLabel3_14.configure(text='''AKE10''')
TLabel3_14.configure(background="white")


AKE10RES = ttk.Label(TFrame1,style="Red.TLabel")
AKE10RES.place(relx=0.35, rely=0.209, height=20, width=45)
AKE10RES.configure(foreground="#000000")
AKE10RES.configure(font="-family {Segoe UI} -size 10")
AKE10RES.configure(relief="flat")
AKE10RES.configure(background="white")


TLabel3_15 = ttk.Label(TFrame1,style="Red.TLabel")
TLabel3_15.place(relx=0.308, rely=0.279, height=20, width=55)
TLabel3_15.configure(foreground="#000000")
TLabel3_15.configure(font="-family {Segoe UI} -size 12")
TLabel3_15.configure(relief="flat")
TLabel3_15.configure(text='''AKE15''')
TLabel3_15.configure(background="white")


AKE15RES = ttk.Label(TFrame1,style="Red.TLabel")
AKE15RES.place(relx=0.345, rely=0.279, height=20, width=55)
AKE15RES.configure(foreground="#000000")
AKE15RES.configure(font="-family {Segoe UI} -size 10")
AKE15RES.configure(relief="flat")
AKE15RES.configure(background="white")

top.bind('<Tab>',lambda event:lookup2())
top.bind('<Escape>',lambda event:resetallentry())
Scrolledtreeview1.bind("<<TreeviewSelect>>", OnSelected)
database()

FILTERBYDATE.trace(mode="w",callback=SearchfilterDATE)
FILTERBYFLIGHT.trace(mode="w",callback=SearchfilterFLIGHT)
FILTERBYDEPART.trace(mode="w",callback=SearchfilterDEPART)
FILTERBYDESTINATION.trace(mode="w",callback=SearchfilterDESTINATION)
FILTERBYAKE.trace(mode="w",callback=SearchfilterAKE)



STOCKexcelentescale.bind('<KeyRelease>', filter_and_update_treeviewescale)
STOCKexcelent.bind('<KeyRelease>', filter_and_update_treeview)
STOCKexcelentt.bind('<KeyRelease>', filter_and_update_treevieww)
historiqueake.bind('<KeyRelease>', filter_and_HISTORY_treeviewwBYAKE)

try:
    STOCKexcelentescale.bind('<KeyRelease>', lookupstock)
except:
    pass
try:
    stock()
except:
    pass
try:
    history()
except:
    pass
try:
    process_flight_data()
    print('process_flight_data automaticly')
except:
    print('there is a probleme when trying to process_flight_data automaticly')
    pass

try:
    recap()
except:
    pass


top.state('zoomed')





top.mainloop()

