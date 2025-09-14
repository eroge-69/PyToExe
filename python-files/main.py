import FreeSimpleGUI as sg
from openpyxl import load_workbook
from tkcalendar import Calendar
import pandas as pd
from pathlib import Path
from datetime import datetime, date
from tkinter import ttk
import tkinter as tk
import matplotlib.pyplot as plt
import Excel_other_open
#import subprocess

dd, bb = plt.subplots(figsize=(5, 3))
sg.theme('DarkGrey1')
#sg.theme("DarkGrey")  # Fully white theme
sg.set_options(font=('Arial', 10))
#sg.set_options(font=('Aptos Narrow',11),background_color='#2b2b2b') #242424

current_dir = Path(__file__).parent if '__file__' in locals() else Path.cwd()
Task_Mngr_excel_file_path = current_dir.parent.parent / "Office_folder" / "Tracker_(Task_Manager).xlsx"
stock_Mrkt_excel_file_path = current_dir.parent.parent / "Personal_folder" / "@St_Mrkt_Dev" /  "Trading Jounral.xlsm"

#Task_Mngr_excel_file_path = (current_dir.parent.parent / "Office_folder" / "Tracker_(Task_Manager).xlsx").resolve()
icon_Dev_png_path = current_dir.parent.parent / "Dev_Py_code" / "icons" /"dev_1.ico" 

excel_file = Task_Mngr_excel_file_path # Customer List
df = pd.read_excel(excel_file,sheet_name = "Tracker_Report")
third_column_data = df.iloc[:, 2].tolist()  # 3rd column
fourth_column_data = df.iloc[:, 3].tolist()  # 4th column

# Function to show the popup search window
def popup_search(data_list, title):
    """Display a popup for searching and selecting from a list."""
    popup_layout = [
        [sg.Text("Search:"), sg.Input(key="popup_search", enable_events=True)],
        [sg.Listbox(values=data_list, size=(40, 10), key="popup_listbox", enable_events=True)],
        [sg.Button("Close")]
    ]
    popup_window = sg.Window(title, popup_layout, modal=True, keep_on_top=True)

    selected_value = None
    while True:
        popup_event, popup_values = popup_window.read()
        if popup_event in (sg.WINDOW_CLOSED, "Close"):
            break
        # Filter listbox based on search
        if popup_event == "popup_search":
            search_query = popup_values["popup_search"].lower()
            filtered_data = [item for item in data_list if search_query in str(item).lower()]
            popup_window["popup_listbox"].update(values=filtered_data)
        # Capture selected value
        if popup_event == "popup_listbox":
            selected = popup_values["popup_listbox"]
            if selected:  # Ensure there's a selection
                selected_value = selected[0]
                break
    popup_window.close()
    return selected_value

# Load Excel data with `data_only=True` to retrieve formula values
def Table_update():
    excel_file=Task_Mngr_excel_file_path
    wb = load_workbook(excel_file, data_only=True)
    ws = wb['Tracker_Report']
    data_list = []
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i == 0:
            continue  # Skip header row
        processed_row = []
        for cell in row:
            if isinstance(cell, datetime):
                #processed_row.append(cell.date())  # Only date part
                processed_row.append(cell.strftime("%d-%m-%Y"))  # Format: DD-MM-YYYY
            elif cell is None:
                processed_row.append("")  # Replace None with empty string
            else:
                processed_row.append(cell)
        data_list.append(processed_row)
    return data_list
data_list = Table_update()
td_data = data_list

#Next Action Date
def Next_Action_Date_get_row_colors(data_list):
    row_colors = []
    today = date.today()  # ✅ no conflict
    for i, row in enumerate(data_list):
        try:
            cell_date = datetime.strptime(str(row[6]), '%d-%m-%Y').date()
            if today >= cell_date and str(row[2]).strip().upper() != "CLOSED":
                row_colors.append((i, '#2373af'))
            else:
                row_colors.append((i, None))
        except ValueError:
            row_colors.append((i, None))
    return row_colors

def apply_row_colors_by_date(data_list, search_term):
    row_colors = []
    try:
        # Convert entered string (e.g. "20-08-2025") to date object
        ref_date = datetime.strptime(search_term, '%d-%m-%Y').date()
    except ValueError:
        ref_date = date.today()  # fallback to today if input invalid
    for i, row in enumerate(data_list):
        try:
            cell_date = datetime.strptime(str(row[6]), '%d-%m-%Y').date()
            if ref_date >= cell_date and str(row[2]).strip().upper() != "CLOSED":
                row_colors.append((i, '#2373af'))  # highlight
            else:
                row_colors.append((i, None))       # no highlight
        except ValueError:
            row_colors.append((i, None))           # invalid date in row
    return row_colors

status_options = ['Critical','Top Priority','Low','Follow-Up','Closed']
status_radio_buttons = [sg.Radio(text=status,change_submits=True,enable_events=True,group_id='-cstatus-', key=f'-{status}-', ) for status in status_options]

options_ck = ['Critical','Top Priority','Low','Follow-Up','Closed']
checkboxes = [sg.Checkbox(option1,default=(option1 in ['Critical', 'Follow-Up','Top Priority']), key=option1) for option1 in options_ck]

Task_Mnger_Headings = ['S.No.','Start Date', 'Priority/Status', 'Customer Name', 'Query Classification', 'Query Details', 'N-Act Date', 'Channel #' , 'Contact Person','Remark']
Task_Mngr_col_widths_fix = [3, 11, 11, 20, 16, 75, 10, 11, 15,]

menu_def_Status = [['&                 -', ['&Critical', '&Follow-Up', '&Top Priority', '&Low', '&Closed']]]


def filter_data_srch(search_term=None,data_list=None):
    if data_list is None or not data_list:
        return []  # Return an empty list if data_list is None or empty
    if search_term is None:
        return data_list  # Return the original data if no search term is provided
    filtered_data = []
    #for row_index, row in enumerate(data_list[1:], start=1):  # Start from the second row
    for row_index, row in enumerate(data_list):  # Start from the second row
        if search_term.lower() in ' '.join([str(cell).lower() for cell in row]):
            #if search_term.lower() in str(row[6]).lower(): #  Row wise data
            filtered_data.append(row)
    return filtered_data
#--------------------------------------------
def clear_input(window):
    for key in window:
        if key != '-TABLE-' and values['-CHECKBOX-'] == False:
            window[key]('')
    return None

def clear_input_task_Add_window(task_window):
    for key in Task_Mnger_Headings:
        if key in task_window.AllKeysDict:   # avoid missing key errors
            task_window[key].update("")
        else:
            print(f"⚠ Key not found in layout: {key}")
#------Calender inside the layout---------
def _parse_tkcalendar_date(s: str) -> datetime:
    # Handle common formats from tkcalendar: "m/d/yy", "d/m/yy", and "m/d/yyyy"
    for fmt in ("%m/%d/%y", "%d/%m/%y", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    # Fallback: try splitting and normalizing
    parts = s.replace("-", "/").split("/")
    if len(parts) == 3:
        m, d, y = parts
        if len(y) == 2:
            y = "20" + y
        return datetime(int(y), int(m), int(d))
    raise ValueError(f"Unrecognized date format: {s}")

login_layout = [
    [sg.HSeparator(color=sg.theme),sg.Text('User Name'), sg.Input(key='name'),sg.HSeparator(color=sg.theme)],
    [sg.HSeparator(color=sg.theme),sg.Text('Password  '), sg.Input('',key='pass', password_char='*' ),sg.HSeparator(color=sg.theme)],
    [sg.HSeparator(color=sg.theme),sg.Button('Sign In',bind_return_key=True), sg.Button('Exit'),sg.HSeparator(color=sg.theme)]]

dashboard_layout = [
                [      
            sg.Button('OFFICE', key='-offsheet-', button_color=('white', 'Green'), size=(10, 2)),
            sg.Button('St. M', key='-sm-', button_color=('white', 'Green'), size=(10, 2)),
            sg.Button('Common Folder', key='-comfolder-', button_color=('white', 'Green'), size=(15, 2)),
            sg.Button('PO_Records', key='-Trkr-', button_color=('white', 'Green'), size=(12, 2)),
            sg.Text(' ', font=('calibri', 40), key='-TIME-'),
            sg.Text("Tracker DashBoard", expand_x=True, justification="center",
                    font=("Helvetica", 10), relief=sg.RELIEF_RIDGE),
            sg.HorizontalSeparator(),
            sg.Cancel('Close', button_color=('white', 'black')),
            sg.Button('Logout'),
            sg.Button('English', button_color=('white', 'Green')),],
            
    
    [sg.HorizontalSeparator(color='purple')],
    
    [sg.Text('#',font='bold')] +[radio_button for radio_button in status_radio_buttons]+[sg.Text('   | |   ',font='bold')] + checkboxes + [sg.Button('MULTIFILTER')],
    [sg.Text(Task_Mnger_Headings[4]),sg.OptionMenu(values=['New Opportunity','Product Info./Training','Nomination', 'Material','Technical Query/ Support','Feedback/ Complaint'],size=(20,1), default_value='',key="-QueryTypeFltr-"),sg.Button('<-Flt-')]+[sg.Button('ADD TASK'),sg.Button('UpdateTable'),sg.Button('Action Date'),
            sg.Input(key='-cust_Action_date-',size=(10,1),enable_events=True),sg.CalendarButton("_User_Action_Date", close_when_date_chosen=True, target='-cust_Action_date-', button_color=('white', 'green'), font=('MS Sans Serif', 10,), format=('%d-%m-%Y')),
            sg.Text('Search'), sg.Input(key='-inSearch-', size=(20, 10),enable_events=True),
            sg.Checkbox('Single Click', key='-CHECKBOX-'),
            sg.Button('EditRow'),sg.Input(size=5,key='-inDelete-'),sg.Button('Delete Row')],
    [sg.HorizontalSeparator(color='purple'),sg.Text(' Today Important Task '),sg.HorizontalSeparator(color='purple')],
    [sg.Table(
            values=data_list,   # {data_list}
            headings=Task_Mnger_Headings,
            col_widths=Task_Mngr_col_widths_fix,
            num_rows=10,
            auto_size_columns=False,
            display_row_numbers=False,
            justification='left',
            row_height=28,
            font=('Calibri', 12),
            key='-TABLE-',
            enable_events=True,
            enable_click_events=True,
            selected_row_colors='red on yellow',
            #alternating_row_color='#2a2d2e',
            #background_color='#2a2d2e',
            #text_color='white',
            header_text_color='Black',
            #header_background_color='#2a2d2e',
            header_font=None,
            vertical_scroll_only=False,
            expand_y=True,
            #expand_x=True,
        )],


    [sg.Column([
        [sg.Column(
                [
                        [sg.Text(Task_Mnger_Headings[0],size=(8,1)),sg.Input(key=Task_Mnger_Headings[0],size=(15,1),disabled=True)],
                        [sg.Text(Task_Mnger_Headings[1],size=(8,1)),sg.Input(key=Task_Mnger_Headings[1],size=(15,1),disabled=True)],                        
                        [sg.Text(Task_Mnger_Headings[7],size=(8,1)),sg.Input(key=Task_Mnger_Headings[7],size=(15,1),disabled=True)],
                        [sg.Text(Task_Mnger_Headings[8],size=(8,1)),sg.Input(key=Task_Mnger_Headings[8],size=(15,1),disabled=True)],
                  ],
                #background_color="lightblue",
                element_justification="left",
                vertical_alignment="left",
                expand_y=True,
                expand_x=True,
            ),
            sg.Column(
                [ 
                        [sg.Text(Task_Mnger_Headings[3],size=(17,1)),sg.Input(key=Task_Mnger_Headings[3],size=(25,1),disabled=True)],
                        [sg.Text(Task_Mnger_Headings[4],size=(17,1)),sg.Input(key=Task_Mnger_Headings[4],size=(25,1),disabled=True)],
                        [sg.Text(Task_Mnger_Headings[9],size=(6,1)),sg.Multiline(size=(35,6),key=Task_Mnger_Headings[9])],
                          
                  ],
                #background_color="lightyellow",
                element_justification="left",
                vertical_alignment="left",
                expand_y=True,
                expand_x=True,
                
            ),
            sg.Column(
                [
                        
                    [sg.Text(Task_Mnger_Headings[5],size=(10,1)),sg.Multiline(size=(50,9),key=Task_Mnger_Headings[5],justification='center',autoscroll = True)],
                        
                ],
                #background_color="lightgreen",
                element_justification="left",
                vertical_alignment="left",
                expand_y=True,
                expand_x=True,
            ),
                sg.Column(
                [
                #[sg.Text('',size=(12,1))],
                [sg.Text(Task_Mnger_Headings[6],size=(12,1)),sg.Input(key=Task_Mnger_Headings[6],size=(15,3),disabled=True,justification='center')],
                [sg.Text('',size=(12,1))],
                [sg.Text(Task_Mnger_Headings[2],size=(12,1)),sg.OptionMenu(values=['Critical','Top Priority','Low', 'Follow-Up','Closed'],size=(10,1), default_value='',key=Task_Mnger_Headings[2],)],
                [sg.Text('',size=(12,1))],
                [sg.Text('Update',size=(12,1)),sg.Button('-Task_Update-',button_color=('white', 'Green'),size=(15,1))]
                ],
                #background_color="lightgreen", 
                element_justification="left",
                vertical_alignment="left",
                expand_y=True,
                expand_x=True,
            ),
            sg.Column(
                [[sg.Canvas(key="-CANVAS/calendar-")],],
                #background_color="lightgreen", 
                element_justification="left",
                vertical_alignment="left",
                expand_y=True,
                expand_x=True,
            ),
        ]
    ],
    #expand_y=True,
    #expand_x=True,
    justification="left",
    #scrollable=True,
    #vertical_scroll_only=False,
    key="-MAIN-COLUMN-",
)]]

office_layout = [
    [sg.Text('Welcome')],
    [sg.Text('What do you want to do-- - Mr.dev')],
    [sg.Button('Submit'), sg.Button('Logout')]
]

tab_group = [
    [sg.Tab("Login", login_layout, key="LOGWIN-1")],
    [sg.Tab("Dashboard", dashboard_layout, key="DESHBWIN-2")],
    [sg.Tab("Office", office_layout, key="OFFICEWIN-3")]]

layout = [
    [sg.TabGroup(tab_group, key='TABGROUP',expand_x=True,expand_y=True)],  
]

window = sg.Window("Dashboard", layout,margins=(0,0), resizable=True, finalize=True,icon=icon_Dev_png_path)
ttk.Style().layout('TNotebook.Tab', [])    # Hide tab bar
window.Maximize()
#sg.theme('GrayGrayGray')

# Option Menu Event Enable---------------------------------------------------
# Get the variable name linked to the OptionMenu
var_name_1 = window["-QueryTypeFltr-"].Widget.cget("textvariable")
# Create a tk.StringVar object tied to that name
var_obj_1 = tk.StringVar(name=var_name_1)
# Add a trace to detect changes
def on_option_change_1(*args):
    window.write_event_value("-QueryType_Changed-", var_obj_1.get())
var_obj_1.trace("w", on_option_change_1)  # "w" means write/change
#-----------------------------------------------------------------------------
#Calendar inside the Layout------------------------------------------------
# Embed tkcalendar inside the Canvas
parent = window["-CANVAS/calendar-"].Widget
cal = Calendar(parent, selectmode="day")
cal.pack(expand=True, fill="both")

# On selection, post event back to PSG loop (do NOT popup here)
def on_date_selected(event):
    window.write_event_value("-CAL_SELECTED-", cal.get_date())

cal.bind("<<CalendarSelected>>", on_date_selected)
#--------------------------------------------------------------

while True:
    event, values = window.read()
    #event, values = window.read(timeout=1000)
    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break
    for status in status_options:
        if event == f'-{status}-':
            window[f'-{status}-'].update(text_color='#ffff00')
            selected_status = status
            window['-TABLE-'].update(values=Table_update())
            window['-TABLE-'].update(row_colors=[(i, sg.theme_background_color()) for i in range(len(Table_update()))])
            srch=(status)
            filtered_data = filter_data_srch(search_term=srch, data_list=Table_update())
            td_data=filtered_data
            window['-TABLE-'].update(values=filtered_data)
        else:
            window[f'-{status}-'].update(text_color='white')

    if event == 'Clear':
        clear_input(window)
    
    if event == "Sign In":
        if values['name'] == '' and values['pass'] == '':
            window['DESHBWIN-2'].select()
        elif values['name'] != '' or values['pass'] != '':
            sg.popup('User Name, Password incorrect!')
    if event == "Logout":
        window['LOGWIN-1'].select()

#Dev2_Excel_Open----------------------------------------------------
    if event == '-offsheet-':  ## Office sheet Open
        Excel_other_open.officesheet_repot()
    if event == '-sm-':  ## Stock sheet Open
        Excel_other_open.stock_analysis()
    if event == '-Trkr-':  ## Tracker Sheet open
        Excel_other_open.trackersheet()
    if event == '-comfolder-':  ## Open Common Folder
        Excel_other_open.commonfolder_open()
#-------------------------------------------------------------------
    if event == "-QueryType-":
            srch="-QueryType-"
            filtered_data = filter_data_srch(search_term=srch, data_list=Table_update())
            td_data=filtered_data
            window['-TABLE-'].update(values=filtered_data)

# Calendar Inside the layout--date pick
    if event == "-CAL_SELECTED-":
            date_str = values["-CAL_SELECTED-"]  # e.g. "8/21/25" or "21/8/25"
            try:
                dt = _parse_tkcalendar_date(date_str)
                pretty = dt.strftime("%d-%m-%Y")
                window[Task_Mnger_Headings[6]].update(pretty)
            except Exception:
                pretty = date_str  # fallback, show raw string
            #sg.popup(f"You selected: {pretty}", keep_on_top=True,background_color="blue",text_color="white",title="Date Selected")  # works fine now

# Next Action Date...
    if event == 'Action Date':
        #window['-TABLE-'].update(values=Table_update(data_list), row_colors=[(i, sg.theme_background_color()) for i in range(len(Table_update(data_list)))]) # Update
        #row_colors = Dev3_srch_filter.Next_Action_Date_get_row_colors(Table_update(data_list))
        td_data = Table_update()  # or however you load your table data
        row_colors = Next_Action_Date_get_row_colors(td_data)
        window['-TABLE-'].update(values=td_data, row_colors=row_colors)
#------------
    if event == '-cust_Action_date-': 
        search_term = values['-cust_Action_date-']
        td_data = Table_update()  # or however you load your table data
        row_colors = apply_row_colors_by_date(td_data, search_term)
        window['-TABLE-'].update(values=td_data, row_colors=row_colors)

#Table Update
    if event == 'UpdateTable':
        window['-inSearch-']('')
        window['-cust_Action_date-']('')
        #updated_data = Table_update()
        window['-TABLE-'].update(values=Table_update())
        td_data= values=Table_update()
    
# ---Filter
    if event == '-inSearch-':
       search_term = values['-inSearch-']
       filtered_data = filter_data_srch(search_term=search_term, data_list=Table_update())
       td_data=filtered_data
       window['-TABLE-'].update(values=filtered_data)

# ---Multi-Filter
    if event in ('MULTIFILTER', '-INPUT-RETURN-'):
        window['-TABLE-'].update(values=Table_update())
        selected_options = [option1 for option1 in options_ck if values[option1]]
        result_multifiler = [option1 for option1 in selected_options] 
        #filtered_data= [row for row in test if row[2] in ['OPEN', 'HOLD']]
        #filtered_data = [row for row in data_list if row[2] in result_multifiler]
        filtered_data = [row for row in Table_update() if row[2] in result_multifiler]
        window['-TABLE-'].update(values=filtered_data)  
        td_data=filtered_data
        #result = ', '.join(["'" + option1 + "'" for option1 in selected_options])
        #sg.popup(", ".join(result_multifiler),background_color='#6E2C00',auto_close=True,auto_close_duration=5)  # Popup the selected options

# Query Type Search-------------------------------------------------------------
    if event == "-QueryType_Changed-":
        QueryType_filtered = filter_data_srch(search_term=values["-QueryTypeFltr-"], data_list=Table_update())
        td_data=QueryType_filtered
        window['-TABLE-'].update(values=QueryType_filtered)

    if event == "<-Flt-":
        selected_Query_typ_1 = values.get("-QueryTypeFltr-", "")
        QueryType_filtered = filter_data_srch(search_term=selected_Query_typ_1, data_list=Table_update())
        td_data=QueryType_filtered
        window['-TABLE-'].update(values=QueryType_filtered)
#------------------------------------------------------------------------------------------

#Delete
    if event == '-TABLE-' and values['-TABLE-']:
        row = values['-TABLE-'][0]
        table_data = td_data or []

        # ✅ make sure row is within range
        if 0 <= row < len(table_data):
            selected_row = table_data[row]
            window['-inDelete-'].update(selected_row[0])

            for i, heading in enumerate(Task_Mnger_Headings[:10]):  # first 10 columns
                if i < len(selected_row):
                    window[heading].update(selected_row[i])
        else:
            print(f"⚠ Invalid row index {row}, table length = {len(table_data)}")
            window['-TABLE-'].update(select_rows=[])   # clear invalid selection



    if event == 'Delete Row':
        pin = values.get('-inDelete-', '').strip()
        if not pin:
            sg.popup('Please', 'Enter the PIN', background_color='black', keep_on_top=True)
        else:
            delete_Confirmation_pin=  sg.popup_get_text('Enter the PIN',title='Please',password_char='*',keep_on_top=True,background_color='black', text_color='white')
            
            if delete_Confirmation_pin != "1234":   # ✅ Correct syntax for NOT EQUAL
                sg.popup("Access Denied ❌", keep_on_top=True)
                #sys.exit()           
            if delete_Confirmation_pin == "1234":
                sg.popup("Access Granted ✅", keep_on_top=True)
                try:
                    wb = load_workbook(Task_Mngr_excel_file_path)
                    sheet = wb['Tracker_Report']

                    # Get the entered Row ID from input box
                    try:
                        row_id_to_delete = int(pin)
                    except ValueError:
                        sg.popup('Invalid ID', 'Please enter a numeric Row ID', keep_on_top=True)
                        wb.close()
                        continue

                    row_found = False
                    for row in sheet.iter_rows(min_row=2, max_row=sheet.max_row, min_col=1, max_col=1):
                        if row[0].value == row_id_to_delete:
                            sheet.delete_rows(row[0].row)
                            row_found = True
                            break

                    if row_found:
                        # Re-number serial numbers after deletion
                        for idx, cell in enumerate(sheet.iter_rows(min_row=2, min_col=1, max_col=1), start=1):
                            cell[0].value = idx
                        wb.save(Task_Mngr_excel_file_path)
                        wb.close()
                        # Refresh table
                        window['-TABLE-'].update(values=Table_update())
                        td_data= values=Table_update()
                        window['-inDelete-'].update('')  # clear input box
                        sg.popup('Success', f'Row ID {row_id_to_delete} deleted', keep_on_top=True)
                    else:
                        wb.close()
                        sg.popup('Not Found', f'Row ID {row_id_to_delete} not found', keep_on_top=True)
                except PermissionError:
                    sg.popup('File in use', 'File is being used by another user.\nPlease try again later.', keep_on_top=True)


#Tast Add  
    if event == 'ADD TASK':
            
            task_window  = sg.Window('New Row',  [
                        [sg.Text(Task_Mnger_Headings[0],size=(20,1)),sg.Input(key=Task_Mnger_Headings[0],disabled=True)],
                        [sg.Text(Task_Mnger_Headings[1],size=(20,1)),sg.Input(key=Task_Mnger_Headings[1],size=(20,1)),
                        sg.CalendarButton("Date Picker", close_when_date_chosen=True, target=Task_Mnger_Headings[1], button_color=('white', 'green'), font=('MS Sans Serif', 10,), format=('%d-%m-%Y'))],
                        [sg.Text(Task_Mnger_Headings[2],size=(20,1)),sg.OptionMenu(values=['Critical','Urgent', 'Follow-Up','Top Priority','Low','Closed'],size=(20,1), default_value='',key=Task_Mnger_Headings[2])],
                        [sg.Text(Task_Mnger_Headings[3],size=(20,1)),sg.Input(size=(25,1), key=Task_Mnger_Headings[3],enable_events=True ),sg.Button("Select Customer Name")],
                        [sg.Text(Task_Mnger_Headings[4],size=(20,1)),sg.OptionMenu(values=['New Opportunity','Product Info./Training','Nomination', 'Material','Technical Query/ Support','Feedback/ Complaint'],size=(20,1), default_value='',key=Task_Mnger_Headings[4])],
                        [sg.Text(Task_Mnger_Headings[5],size=(20,1)),sg.Multiline(size=(50,4),key=Task_Mnger_Headings[5])],
                        [sg.Text(Task_Mnger_Headings[6],size=(20,1)),sg.Input(key=Task_Mnger_Headings[6],size=(20,1)),
                        sg.CalendarButton("N-Action-Date", close_when_date_chosen=True, target=Task_Mnger_Headings[6], button_color=('white', 'green'), font=('MS Sans Serif', 10,), format=('%d-%m-%Y'))],
                        [sg.Text(Task_Mnger_Headings[7],size=(20,1)),sg.Input(size=(20,1),key=Task_Mnger_Headings[7])],
                        [sg.Text(Task_Mnger_Headings[8],size=(20,1)),sg.Input(size=(20,1),key=Task_Mnger_Headings[8])],
                        [],
                        [sg.Submit("Submit"), sg.Cancel(),]], background_color= 'DarkGrey', keep_on_top=True, finalize=True)
            while True:
                Nevent, Nvalues = task_window.read()
                print(1)
                if Nevent in (sg.WINDOW_CLOSED, "Cancel"):
                   task_window.close()
                   break
                
                elif Nevent == "Select Customer Name":
                    selected_value = popup_search(fourth_column_data, "Search 4th Column Data")
                    if selected_value:
                        task_window[Task_Mnger_Headings[3]].update(value=selected_value)  # ✅ works now

                elif Nevent == "Submit":
                    #if Nvalues[Task_Mnger_Headings[1]] == '' or Nvalues[Task_Mnger_Headings[2]] == '' or Nvalues[Task_Mnger_Headings[3]] == '' or Nvalues[Task_Mnger_Headings[4]] == '' or Nvalues[Task_Mnger_Headings[5]] == '' or Nvalues[Task_Mnger_Headings[6]] == '' or Nvalues[Task_Mnger_Headings[7]] == '' :
                    if any(Nvalues[Task_Mnger_Headings[i]] == '' for i in range(1, 7)):
                        sg.popup('Input is missing',keep_on_top=True)
                    else:
                        wb = load_workbook(Task_Mngr_excel_file_path)
                        sheet = wb["Tracker_Report"]
                        new_id_value = len(sheet['A'])

                        # Fill data to match the number of columns
                        data = [
                            new_id_value,
                            Nvalues.get(Task_Mnger_Headings[1], ""),
                            Nvalues.get(Task_Mnger_Headings[2], ""),
                            Nvalues.get(Task_Mnger_Headings[3], ""),
                            Nvalues.get(Task_Mnger_Headings[4], ""), 
                            Nvalues.get(Task_Mnger_Headings[5], ""),
                            Nvalues.get(Task_Mnger_Headings[6], ""),
                            Nvalues.get(Task_Mnger_Headings[7], ""),
                            Nvalues.get(Task_Mnger_Headings[8], ""),
                            ""  # 10th column placeholder
                        ]
                        row_values = list(data)
                        sheet.append(row_values)
                        wb.save(Task_Mngr_excel_file_path)
                        sg.popup('Data saved!', keep_on_top=True)
                        clear_input_task_Add_window(task_window)   
                        task_window.close()
                    #-Update Table
                        td_data = Table_update()
                        window['-TABLE-'].update(values=td_data, select_rows=[])
                        Table_update()
                        window['-TABLE-'].update(values=Table_update())
                        #window['-TABLE-'].update(values=td_data, select_rows=[0])

#Tast Edit 
    if event == 'EditRow' and len(values['-TABLE-']) > 0:
            rowID = values['-TABLE-'][0]+2
            td = td_data
            editRow = values['-TABLE-'][0]
            print(rowID)
            TableEdit_window  = sg.Window('New Row',  [
                        [sg.Text(Task_Mnger_Headings[0], size=(20,1)),sg.Input(td[editRow][0],key=Task_Mnger_Headings[0],disabled=True,background_color="black",text_color="white",disabled_readonly_background_color="#808080",disabled_readonly_text_color="white")],
                        [sg.Text(Task_Mnger_Headings[1],size=(20,1)),sg.Input(td[editRow][1],key=Task_Mnger_Headings[1],size=(20,1)),
                        sg.CalendarButton("Date Picker", close_when_date_chosen=True, target=Task_Mnger_Headings[1], button_color=('white', 'green'), font=('MS Sans Serif', 10,), format=('%d-%m-%Y'))],
                        [sg.Text(Task_Mnger_Headings[2],size=(20,1)),sg.Input(td[editRow][2],key=Task_Mnger_Headings[2],disabled=True,disabled_readonly_background_color="#808080",disabled_readonly_text_color="white"),
                         sg.OptionMenu(values=['Critical','Urgent', 'Follow-Up','Top Priority','Low','Closed'],size=(20,1), default_value='',key="-StatusUpdate-",pad=(10, 5))],
                        [sg.Text(Task_Mnger_Headings[3],size=(20,1)),sg.Input(td[editRow][3],size=(25,1), key=Task_Mnger_Headings[3],enable_events=True ),sg.Button("Select Customer Name")],
                        [sg.Text(Task_Mnger_Headings[4],size=(20,1)),sg.Input(td[editRow][4],key=Task_Mnger_Headings[4],disabled=True,disabled_readonly_background_color="#808080",disabled_readonly_text_color="white"),
                         sg.OptionMenu(values=['New Opportunity','Product Info./Training','Nomination', 'Material','Technical Query/ Support','Feedback/ Complaint'],size=(20,1), default_value='',key="-QueryType-"),sg.Submit("-Change-"),],
                        [sg.Text(Task_Mnger_Headings[5],size=(20,1)),sg.Multiline(td[editRow][5],size=(50,4),key=Task_Mnger_Headings[5])],
                        [sg.Text(Task_Mnger_Headings[6],size=(20,1)),sg.Input(td[editRow][6],key=Task_Mnger_Headings[6],size=(20,1)),
                        sg.CalendarButton("N-Action-Date", close_when_date_chosen=True, target=Task_Mnger_Headings[6], button_color=('white', 'green'), font=('MS Sans Serif', 10,), format=('%d-%m-%Y'))],
                        [sg.Text(Task_Mnger_Headings[7],size=(20,1)),sg.Input(td[editRow][7],size=(20,1),key=Task_Mnger_Headings[7])],
                        [sg.Text(Task_Mnger_Headings[8],size=(20,1)),sg.Input(td[editRow][8],size=(20,1),key=Task_Mnger_Headings[8])],
                        [],
                        [sg.Submit("Update"), sg.Button("Action_Date_Update"),sg.Exit(),]], background_color= 'DarkGrey', keep_on_top=True,finalize=True)

        # Option Menu Event Enable
            # Get the variable name linked to the OptionMenu
            var_name = TableEdit_window["-StatusUpdate-"].Widget.cget("textvariable")
            # Create a tk.StringVar object tied to that name
            var_obj = tk.StringVar(name=var_name)
            # Add a trace to detect changes
            def on_option_change(*args):
                TableEdit_window.write_event_value("-QueryType Changed-", var_obj.get()) 
            var_obj.trace("w", on_option_change)  # "w" means write/change
         #--------------------
            while True:
                Edtevent, Edtvalues = TableEdit_window .read()
                if Edtevent in (sg.WINDOW_CLOSED, "Exit"):
                   TableEdit_window.close()
                   break
                if Edtevent == "-QueryType Changed-":
                   #selected = Edtvalues.get("-StatusUpdate-", "")
                   TableEdit_window[Task_Mnger_Headings[2]].update(value=Edtvalues["-StatusUpdate-"]) #"-Change-"

                if Edtevent == "Select Customer Name":
                    selected_value = popup_search(fourth_column_data, "Search 4th Column Data")
                    if selected_value:
                        TableEdit_window[Task_Mnger_Headings[3]].update(value=selected_value)  # ✅ works now

                if Edtevent == "-Change-": 
                    selected_Query_typ = Edtvalues.get("-QueryType-", "")
                    TableEdit_window[Task_Mnger_Headings[4]].update(value=selected_Query_typ) #"-Change-"

                if Edtevent == "Update":
                    if Edtvalues[Task_Mnger_Headings[1]] == '' or Edtvalues[Task_Mnger_Headings[2]] == '' or Edtvalues[Task_Mnger_Headings[3]] == '' or Edtvalues[Task_Mnger_Headings[4]] == '' or Edtvalues[Task_Mnger_Headings[5]] == '' or Edtvalues[Task_Mnger_Headings[6]] == '' or Edtvalues[Task_Mnger_Headings[7]] == '' :
                        sg.popup('Input is missing',keep_on_top=True)
                    else:
                        wb = load_workbook(Task_Mngr_excel_file_path)
                        sheet = wb["Tracker_Report"]
                        
                        rowID=int(Edtvalues[Task_Mnger_Headings[0]])+1
                        print(rowID)
                        # Fill data to match the number of columns
                        edtdata = [
                            Edtvalues.get(Task_Mnger_Headings[0], ""),
                            Edtvalues.get(Task_Mnger_Headings[1], ""),
                            Edtvalues.get(Task_Mnger_Headings[2], ""),
                            Edtvalues.get(Task_Mnger_Headings[3], ""),
                            Edtvalues.get(Task_Mnger_Headings[4], ""), 
                            Edtvalues.get(Task_Mnger_Headings[5], ""),
                            Edtvalues.get(Task_Mnger_Headings[6], ""),
                            Edtvalues.get(Task_Mnger_Headings[7], ""),
                            Edtvalues.get(Task_Mnger_Headings[8], ""),
                            ""  # 10th column placeholder
                        ]
                        row_values = list(edtdata)
                        for col_num, value in enumerate(row_values, start=1):
                            sheet.cell(row=rowID, column=col_num, value=value)
                        wb.save(Task_Mngr_excel_file_path)
                        sg.popup('Data saved!', keep_on_top=True)
                        td_data = Table_update()
                        window['-TABLE-'].update(values=td_data, select_rows=[])
                        Table_update()
                        window['-TABLE-'].update(values=Table_update())
            TableEdit_window.close()

    #-----SO & Status & Remark Update
    if event == '-Task_Update-' and len(values['-TABLE-']) > 0:
        rowID = values['-TABLE-'][0]+2
        td = td_data
        editRow = values['-TABLE-'][0]
        required_fields = [1, 2, 3, 4, 5, 6, 7,  ] # Skip any headings
        if any(values[Task_Mnger_Headings[i]] == '' for i in required_fields):
        #if any(Nvalues[Task_Mnger_Headings[i]] == '' for i in range(1, 9)): # 1 to 7  
            sg.popup('Input is missing', keep_on_top=True)
        else:
            wb = load_workbook(Task_Mngr_excel_file_path)
            sheet = wb["Tracker_Report"]
            rowID=int(values[Task_Mnger_Headings[0]])+1
            print(rowID)
            update_data = [
                values.get(Task_Mnger_Headings[0], ""),
                values.get(Task_Mnger_Headings[1], ""),
                values.get(Task_Mnger_Headings[2], ""),
                values.get(Task_Mnger_Headings[3], ""),
                values.get(Task_Mnger_Headings[4], ""), 
                values.get(Task_Mnger_Headings[5], ""),
                values.get(Task_Mnger_Headings[6], ""),
                values.get(Task_Mnger_Headings[7], ""),
                values.get(Task_Mnger_Headings[8], ""),
                values.get(Task_Mnger_Headings[9], ""),
                ""  # 10th column placeholder
            ]
            row_values = list(update_data)
            for col_num, value in enumerate(row_values, start=1):
                sheet.cell(row=rowID, column=col_num, value=value)
            wb.save(Task_Mngr_excel_file_path)
            sg.popup('Data saved!', keep_on_top=True)
            td_data = Table_update()
            window['-TABLE-'].update(values=td_data, select_rows=[])
            Table_update()
            window['-TABLE-'].update(values=Table_update())

window.close()