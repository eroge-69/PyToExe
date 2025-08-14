import pandas as pd
import re
import datetime
import math
import tkinter
import customtkinter
from tkinter import ttk, filedialog, messagebox
import traceback


def select_file(entry_var):
    file_path = filedialog.askopenfilename(title=f"Select Input File")
    entry_var.set(file_path)

def select_output_path(entry_var):
    output_path = filedialog.askdirectory(title="Select Output Directory")
    entry_var.set(output_path)
    entry_var.set(output_path)

def convert_to_int(value):
    if isinstance(value, (int, float)):
        if math.isnan(value):
            return ''
        else:
            return str(int(value))
    elif isinstance(value, datetime.datetime):
        return str(value)
    else:
        try:
            return str(int(value))
        except ValueError:
            return str(value)

def extract_BP_No(text):
    matches = re.findall(r'(?:^|[^0-9])([1-5]\d{7})(?![0-9])', text)
    return ', '.join(matches)

def extract_billing_doc(text):
    # Extract the Billing Document No
    matches = re.findall(r'(?:^|[^0-9]|[^0-9]00)(9\d{7})(?![0-9])', text)
    return ', '.join(matches)

def extract_vss_order_doc(text):
    # Extract the VSS Order No
    matches = re.findall(r'(?:^|[^0-9])(2[2-3]\d{8})(?![0-9])', text)
    return ', '.join(matches)

def extract_new_id(text):
    # Extract the VSS Order No
    matches = re.findall(r'(?:^|[^0-9])(19\d{10}|20\d{10})(?![0-9])', text)
    return ', '.join(matches)

def extract_old_id(text):
    # Extract the VSS Order No
    matches = re.findall(r'(?:^|[^0-9])(\d{9}[VvXx])(?![0-9])', text)
    return ', '.join(matches)

def extract_sd_sales_order(text):
    # Extract the VSS Order No
    matches = re.findall(r'(?:^|[^0-9])((?:22|23|16)\d{6}|[93]\d{6})(?![0-9])', text)
    return ', '.join(matches)

def extract_cheque(text):
    # Extract the Billing Document No
    matches = re.findall(r'(?:^|[^0-9])(\d{6})(?![0-9])', text)
    return ', '.join(matches)

def extract_vehicle_no(text):
    # Match letter-based or digit-based vehicle numbers
    pattern = r'(?<![A-Za-z0-9])([A-Z]{2,3}[- ]?\d{4})(?!\d)|(?<!\d)(\d{2}-\d{4})(?!\d)'

    matches = re.findall(pattern, text)

    formatted = []
    for match in matches:
        # Each match is a tuple: (letters_type, digits_type)
        letters_type, digits_type = match

        if letters_type:
            cleaned = letters_type.replace(" ", "").replace("-", "")
            letters = re.match(r'[A-Z]{2,3}', cleaned).group()
            digits = cleaned[len(letters):]
            formatted.append(f"{letters}-{digits}")
        elif digits_type:
            formatted.append(digits_type)

    return ', '.join(formatted)

# Specify the columns you want to consider for extracting unique values
columns_to_consider = ['BP No', 'BP2', 'BP3', 'BP4',
                       'BP5', 'BP6', 'BP7', 'BP8']

def extract_unique(row):
    values = []
    for col in columns_to_consider:
        if pd.notnull(row[col]):  # Check if the value is not NaN
            # Convert the value to string before splitting
            values.extend(str(row[col]).split(', '))
    unique_values = set(values)
    return ', '.join(unique_values)

def remove_comma_space(text):
    if text.startswith(", "):
        text = text[2:]  # Remove ", " from the beginning
    if text.endswith(", "):
        text = text[:-2]  # Remove ", " from the end
    return text

def generate_report():
    try:
        input_file_path = entry_vars[0].get()
        id_file_path = entry_vars[1].get()
        vss_file_path = entry_vars[2].get()
        sd_file_path = entry_vars[3].get()
        billing_file_path = entry_vars[4].get()
        license_file_path = entry_vars[5].get()
        cheque_file_path = entry_vars[6].get()
        output_directory = entry_vars[7].get()

        input_df = pd.read_excel(input_file_path, sheet_name='2024-2025')
        # input_df = pd.read_excel("DM-COM (1000798461) - AFTER SALES.xlsx", sheet_name='2024-2025')
        id_df = pd.read_excel(id_file_path)
        vss_df = pd.read_excel(vss_file_path)
        sd_df = pd.read_excel(sd_file_path)
        billing_df = pd.read_excel(billing_file_path)
        license_plate_df = pd.read_excel(license_file_path)
        cheque_df = pd.read_excel(cheque_file_path)

        # input_df = pd.read_excel("DM-COM (1000798478) - RETAIL.xlsx", sheet_name='2024-2025')
        # # input_df = pd.read_excel("DM-COM (1000798461) - AFTER SALES.xlsx", sheet_name='2024-2025')
        # id_df = pd.read_excel("IDs.xlsx")
        # vss_df = pd.read_excel("VSS Sales Order.xlsx")
        # sd_df = pd.read_excel("SD Sales Order.xlsx")
        # billing_df = pd.read_excel("Invoice.xlsx")
        # license_plate_df = pd.read_excel("License Plate.xlsx")
        # cheque_df = pd.read_excel("Cheque No.xlsx")

        input_df['Description'] = input_df['Description'].apply(convert_to_int)
        input_df['BP No'] = input_df['Description'].apply(extract_BP_No).apply(convert_to_int)
        input_df['Old ID'] = input_df['Description'].apply(extract_old_id).apply(convert_to_int)
        input_df['New ID'] = input_df['Description'].apply(extract_new_id).apply(convert_to_int)
        input_df['VSS_Order_No'] = input_df['Description'].apply(extract_vss_order_doc).apply(convert_to_int)
        input_df['SD Salse Order'] = input_df['Description'].apply(extract_sd_sales_order).apply(convert_to_int)
        input_df['Billing_doc_No'] = input_df['Description'].apply(extract_billing_doc).apply(convert_to_int)
        input_df['Vehicle_No'] = input_df['Description'].apply(extract_vehicle_no).apply(convert_to_int)
        input_df['Cheque_No'] = input_df['Description'].apply(extract_cheque).apply(convert_to_int)

        id_df['Search Term 1'] = id_df['Search Term 1'].apply(convert_to_int)
        vss_df['Order'] = vss_df['Order'].apply(convert_to_int)
        sd_df['Sales Doc.'] = sd_df['Sales Doc.'].apply(convert_to_int)
        billing_df['Bill. Doc.'] = billing_df['Bill. Doc.'].apply(convert_to_int)
        license_plate_df['License Plate Number'] = license_plate_df['License Plate Number'].apply(convert_to_int)
        cheque_df['Text'] = cheque_df['Text'].apply(convert_to_int)
        cheque_df['Cheque_No'] = cheque_df['Text'].apply(extract_cheque).apply(convert_to_int)

        id_df = id_df.sort_values(by=['Search Term 1', 'Business Partner'], key=lambda x: x.isna())
        # Drop duplicates
        id_df = id_df.drop_duplicates(subset=['Search Term 1'], keep='first')
        # Filter out blank values in 'Search Term 1' before merging
        id_df = id_df[id_df['Search Term 1'].notna() & (id_df['Search Term 1'] != '')]
        # Rename a single column
        id_df = id_df.rename(columns={'Business Partner': 'BP2'})

        vss_df = vss_df.sort_values(by=['Order', 'Sold-To'], key=lambda x: x.isna())
        # Drop duplicates
        vss_df = vss_df.drop_duplicates(subset=['Order'], keep='first')
        # Rename a single column
        vss_df = vss_df.rename(columns={'Sold-To': 'BP4'})

        sd_df = sd_df.sort_values(by=['Sales Doc.', 'Sold-To'], key=lambda x: x.isna())
        # Drop duplicates
        sd_df = sd_df.drop_duplicates(subset=['Sales Doc.'], keep='first')
        # Rename a single column
        sd_df = sd_df.rename(columns={'Sold-To': 'BP5'})

        billing_df = billing_df.sort_values(by=['Bill. Doc.', 'Payer'], key=lambda x: x.isna())
        # Drop duplicates
        billing_df = billing_df.drop_duplicates(subset=['Bill. Doc.'], keep='first')
        # Rename a single column
        billing_df = billing_df.rename(columns={'Payer': 'BP6'})

        license_plate_df = license_plate_df.sort_values(by=['License Plate Number', 'Customer'], key=lambda x: x.isna())
        # Drop duplicates
        license_plate_df = license_plate_df.drop_duplicates(subset=['License Plate Number'], keep='first')
        # Filter out blank values in 'Search Term 1' before merging
        license_plate_df = license_plate_df[license_plate_df['License Plate Number'].notna() & (license_plate_df['License Plate Number'] != '')]
        # Rename a single column
        license_plate_df = license_plate_df.rename(columns={'Customer': 'BP7'})

        cheque_df = cheque_df.sort_values(by=['Cheque_No', 'Customer'], key=lambda x: x.isna())
        # Drop duplicates
        cheque_df = cheque_df.drop_duplicates(subset=['Cheque_No'], keep='first')
        # Filter out blank values in 'Search Term 1' before merging
        cheque_df = cheque_df[cheque_df['Cheque_No'].notna() & (cheque_df['Cheque_No'] != '')]
        # Rename a single column
        cheque_df = cheque_df.rename(columns={'Customer': 'BP8'})

        output_df = pd.merge(input_df, id_df, left_on=['Old ID'], right_on=['Search Term 1'], how='left')
        # Rename a single column
        id_df = id_df.rename(columns={'BP2': 'BP3'})
        output_df = pd.merge(output_df, id_df, left_on=['New ID'], right_on=['Search Term 1'], how='left')
        output_df = pd.merge(output_df, vss_df, left_on=['VSS_Order_No'], right_on=['Order'], how='left')
        output_df = pd.merge(output_df, sd_df, left_on=['SD Salse Order'], right_on=['Sales Doc.'], how='left')
        output_df = pd.merge(output_df, billing_df, left_on=['Billing_doc_No'], right_on=['Bill. Doc.'], how='left')
        output_df = pd.merge(output_df, license_plate_df, left_on=['Vehicle_No'], right_on=['License Plate Number'], how='left')
        output_df = pd.merge(output_df, cheque_df, left_on=['Cheque_No'], right_on=['Cheque_No'],
                             how='left')

        # input_df['Acc No'] = input_df['Description'].apply(acc_no)
        # Drop the columns
        output_df = output_df.drop(['Search Term 1_x', 'Search Term 2_x', 'Search Term 1_y', 'Search Term 2_y', 'Order', 'Item', 'Sales Doc.', 'Bill. Doc.', 'Sold-To', 'License Plate Number'], axis=1)

        # Extract unique values from specified columns
        output_df['Suggested BP No'] = output_df.apply(extract_unique, axis=1)
        output_df['Suggested BP No'] = output_df['Suggested BP No'].apply(remove_comma_space)
        # Drop a single column4
        output_df = output_df.drop(columns_to_consider, axis=1)

        # output_df.to_excel("Output RT.xlsx")

        file_name = f"{output_directory}/Suggested BP List.xlsx"

        with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
            output_df.to_excel(writer, sheet_name="Suggested BP List", index=False)

            # Get the xlsxwriter workbook and worksheet objects.
            workbook = writer.book
            worksheet = writer.sheets["Suggested BP List"]

            # Add formats.
            header_format = workbook.add_format(
                {
                    "bold": True,
                    "text_wrap": True,
                    "valign": "middle",
                    "align": "center",
                    "fg_color": "#833C0C",
                    "color": "#FFFFFF",
                    "border": 1,
                    "border_color": "#FFFFFF"
                }
            )

            body_format1 = workbook.add_format(
                {
                    "text_wrap": True,
                    "valign": "top",
                    "fg_color": "#D8E4BC",
                    "border": 1
                }
            )

            body_format2 = workbook.add_format(
                {
                    "text_wrap": True,
                    "valign": "top",
                    "fg_color": "#EBF1DE",
                    "border": 1
                }
            )
            # Set column widths based on content
            for col_num, value in enumerate(output_df.columns):
                worksheet.write(0, col_num, value, header_format)
                max_len = max(output_df[value].astype(str).apply(len).max(), len(value)) + 3
                worksheet.set_column(col_num, col_num, max_len)

            # Iterate through the rows and columns of the DataFrame (excluding headers)
            for row_num, row in enumerate(output_df.itertuples(), start=1):
                body_format = body_format1 if row_num % 2 == 1 else body_format2
                for col_num, value in enumerate(row[1:], start=0):
                    # worksheet.write(row_num, col_num, value, body_format)
                    if pd.notna(value):  # Check for NaN
                        worksheet.write(row_num, col_num, value, body_format)
                    else:
                        worksheet.write_blank(row_num, col_num, None, body_format)

        messagebox.showinfo("Successful", "Report Generated successfully!")

    except FileNotFoundError:
        messagebox.showerror("File Not Found", "Please select all input files.")

    except pd.errors.EmptyDataError:
        messagebox.showerror("Empty Data", "No data found in one or more input files.")

    except Exception as e:
        # messagebox.showerror("Error", f"An error occurred: {str(e)}")

        error_message = ''.join(traceback.format_exception(None, e, e.__traceback__))
        messagebox.showerror("Error", f"An error occurred:\n{error_message}")
        print(error_message)


customtkinter.set_appearance_mode("light")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green
customtkinter.deactivate_automatic_dpi_awareness()

app = customtkinter.CTk()  # create CTk window like you do with the Tk window
app.geometry("783x460")
app.title("Pattern Extractor")
app.resizable(width=False, height=False)

# Entry widgets to display selected file paths
entry_vars = [tkinter.StringVar() for _ in range(8)]

# Input File
input_file_label = customtkinter.CTkLabel(app, textvariable=entry_vars[0], text="", fg_color='#c9deff', anchor="w",
                                          width=600, height=30, corner_radius=8, wraplength=570)
input_file_label.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

input_fil_button = customtkinter.CTkButton(app, text="Input File", height=30, fg_color='#042f66', hover_color='#135ebf',
                                           font=("Helvetica", 15), command=lambda: select_file(entry_vars[0]))
input_fil_button.grid(row=0, column=2, padx=10, pady=10)

# Id File
id_file_label = customtkinter.CTkLabel(app, textvariable=entry_vars[1], text="", fg_color='#c9deff', anchor="w",
                                          width=600, height=30, corner_radius=8, wraplength=570)
id_file_label.grid(row=1, column=0, padx=10, pady=10, columnspan=2)

id_fil_button = customtkinter.CTkButton(app, text="Identification No", height=30, fg_color='#042f66', hover_color='#135ebf',
                                           font=("Helvetica", 15), command=lambda: select_file(entry_vars[1]))
id_fil_button.grid(row=1, column=2, padx=10, pady=10)

# VSS File
vss_file_label = customtkinter.CTkLabel(app, textvariable=entry_vars[2], text="", fg_color='#c9deff', anchor="w",
                                          width=600, height=30, corner_radius=8, wraplength=570)
vss_file_label.grid(row=2, column=0, padx=10, pady=10, columnspan=2)

vss_fil_button = customtkinter.CTkButton(app, text="VSS Order", height=30, fg_color='#042f66', hover_color='#135ebf',
                                           font=("Helvetica", 15), command=lambda: select_file(entry_vars[2]))
vss_fil_button.grid(row=2, column=2, padx=10, pady=10)

# SD File
sd_file_label = customtkinter.CTkLabel(app, textvariable=entry_vars[3], text="", fg_color='#c9deff', anchor="w",
                                          width=600, height=30, corner_radius=8, wraplength=570)
sd_file_label.grid(row=3, column=0, padx=10, pady=10, columnspan=2)

sd_fil_button = customtkinter.CTkButton(app, text="SD Sales Order", height=30, fg_color='#042f66', hover_color='#135ebf',
                                           font=("Helvetica", 15), command=lambda: select_file(entry_vars[3]))
sd_fil_button.grid(row=3, column=2, padx=10, pady=10)

# Billing File
bill_file_label = customtkinter.CTkLabel(app, textvariable=entry_vars[4], text="", fg_color='#c9deff', anchor="w",
                                          width=600, height=30, corner_radius=8, wraplength=570)
bill_file_label.grid(row=4, column=0, padx=10, pady=10, columnspan=2)

Bill_fil_button = customtkinter.CTkButton(app, text="Billing Document", height=30, fg_color='#042f66', hover_color='#135ebf',
                                           font=("Helvetica", 15), command=lambda: select_file(entry_vars[4]))
Bill_fil_button.grid(row=4, column=2, padx=10, pady=10)

# License Plate File
license_file_label = customtkinter.CTkLabel(app, textvariable=entry_vars[5], text="", fg_color='#c9deff', anchor="w",
                                          width=600, height=30, corner_radius=8, wraplength=570)
license_file_label.grid(row=5, column=0, padx=10, pady=10, columnspan=2)

license_fil_button = customtkinter.CTkButton(app, text="License Plate", height=30, fg_color='#042f66', hover_color='#135ebf',
                                           font=("Helvetica", 15), command=lambda: select_file(entry_vars[5]))
license_fil_button.grid(row=5, column=2, padx=10, pady=10)

# Cheque File
cheque_file_label = customtkinter.CTkLabel(app, textvariable=entry_vars[6], text="", fg_color='#c9deff', anchor="w",
                                          width=600, height=30, corner_radius=8, wraplength=570)
cheque_file_label.grid(row=6, column=0, padx=10, pady=10, columnspan=2)

cheque_fil_button = customtkinter.CTkButton(app, text="Cheque No", height=30, fg_color='#042f66', hover_color='#135ebf',
                                           font=("Helvetica", 15), command=lambda: select_file(entry_vars[6]))
cheque_fil_button.grid(row=6, column=2, padx=10, pady=10)

# Output Directory
output_file_label = customtkinter.CTkLabel(app, textvariable=entry_vars[7], text="", fg_color='#c9deff', anchor="w",
                                           width=600, corner_radius=8, wraplength=570)
output_file_label.grid(row=7, column=0, padx=10, pady=10, columnspan=2)

output_file_button = customtkinter.CTkButton(app, text="Output Directory", height=30, fg_color='#042f66',
                                             hover_color='#135ebf', font=("Helvetica", 15),
                                             command=lambda: select_output_path(entry_vars[7]))
output_file_button.grid(row=7, column=2, padx=10, pady=10)

# # Add checkboxes for report generation options
# check_vars = [tkinter.IntVar() for _ in range(4)]
# checkbox_texts = [
#     "Full Report",
#     "Retail",
#     "After Sales",
#     "Customer Wise"
# ]
#
# for i, text in enumerate(checkbox_texts):
#     checkbox = customtkinter.CTkCheckBox(app, text=text, variable=check_vars[i], font=("Helvetica", 14))
#     if i < 2:
#         checkbox.grid(row=3, column=0 + i, padx=10, pady=10, sticky="w")
#     else:
#         checkbox.grid(row=4, column=0 + i - 2, padx=10, pady=5, sticky="w")

generate_button = customtkinter.CTkButton(app, text="Generate Report", height=35, width=760, fg_color='#042f66',
                                          hover_color='#135ebf', font=("Helvetica", 15), command=generate_report)
generate_button.grid(row=8, column=0, columnspan=3, pady=10)

app.mainloop()