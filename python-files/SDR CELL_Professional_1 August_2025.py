#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import tkinter as tk
from tkinter import messagebox
import pandas as pd
import os
import math

def execute_code():
    # Display "Comparison in progress" message
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, "Comparison in progress... Please wait...\n")
    root.update()  # Force GUI update to show the message immediately
    
    cell1 = entry.get()

    if not cell1:
        messagebox.showwarning("Input Error", "Reference cell not found.")
        return

    file_path_SDR = r"D:/Python course/Comparison Tool/Professional/SDR cell input.csv"

    try:
        df = pd.read_csv(file_path_SDR)
        cell2_list = df.iloc[:, 0].dropna().astype(str).tolist()

        file_path_EUtranCellFDD = r"D:/Python course/Comparison Tool/Dumps/EUtranCellFDD.csv"
        output_file = r"D:/Python course/Comparison Tool/NRO Audit.xlsx"

        data_EUtranCellFDD = pd.read_csv(file_path_EUtranCellFDD, low_memory=False)
        reference_column = "userLabel"

        columns_to_exclude = [3, 4, 5, 6, 7, 8, 9, 10, 11]
        value_columns = [col for i, col in enumerate(data_EUtranCellFDD.columns) if i >= 3 and i not in columns_to_exclude]

        row1 = data_EUtranCellFDD[data_EUtranCellFDD[reference_column] == cell1]
        

        if row1.empty:
            print(f"Reference cell '{cell1}' not found in the dataset.")
        else:
            row1_values = row1[value_columns].iloc[0]

            comparison_dict = {
                "MO Name": [os.path.splitext(os.path.basename(file_path_EUtranCellFDD))[0]] * len(value_columns),
                "Parameter Name": value_columns,
                cell1: row1_values,
            }

            for cell2 in cell2_list:
                row2 = data_EUtranCellFDD[data_EUtranCellFDD[reference_column] == cell2]

                if row2.empty:
                    print(f"Cell '{cell2}' not found in the dataset.")
                    comparison_dict[cell2] = ["Not Found"] * len(value_columns)
                    comparison_dict[f"Match_{cell2}"] = ["Not Found"] * len(value_columns)
                else:
                    row2_values = row2[value_columns].iloc[0]
                    comparison_dict[cell2] = row2_values
                    comparison_dict[f"Match_{cell2}"] = row1_values == row2_values

            final_comparison_df = pd.DataFrame(comparison_dict)
            match_columns = [f"Match_{cell2}" for cell2 in cell2_list]
            final_comparison_df["Final_Match"] = final_comparison_df[match_columns].all(axis=1)
            final_comparison_df["Final_Match"] = final_comparison_df["Final_Match"].replace({True: "TRUE", False: "FALSE"})

            base_columns = ["MO Name", "Parameter Name"] + [cell1] + cell2_list + ["Final_Match"]
            final_columns = base_columns + match_columns
            final_comparison_df = final_comparison_df[final_columns]

            def handle_special_values(value):
                if pd.isna(value) or (isinstance(value, float) and (math.isinf(value) or math.isnan(value))):
                    return "N/A"
                return value

            with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
                final_comparison_df.to_excel(writer, sheet_name="Comparison Results", index=False)
                workbook = writer.book
                worksheet = writer.sheets["Comparison Results"]

                default_format = workbook.add_format()
                red_format = workbook.add_format({'font_color': 'red'})

                for col_idx, col in enumerate(final_comparison_df.columns[2:2 + len(cell2_list) + 1]):
                    for row_idx, value in enumerate(final_comparison_df[col]):
                        value_to_write = handle_special_values(value)
                        reference_value = final_comparison_df[cell1].iloc[row_idx]

                        if str(value) != str(reference_value):
                            worksheet.write(row_idx + 1, col_idx + 2, value_to_write, red_format)
                        else:
                            worksheet.write(row_idx + 1, col_idx + 2, value_to_write, default_format)

        # Second sheet: ECellEquipmentFunction
        file_path_ECellEquipmentFunction = r"D:/Python course/Comparison Tool/Dumps/ECellEquipmentFunction.csv"
        data_ECellEquipmentFunction = pd.read_csv(file_path_ECellEquipmentFunction, low_memory=False)

        ECell_dict = dict(zip(data_EUtranCellFDD['refECellEquipmentFunction'], data_EUtranCellFDD['userLabel']))
        data_ECellEquipmentFunction['userLabel'] = data_ECellEquipmentFunction['ldn'].map(ECell_dict)

        value_columns = [col for i, col in enumerate(data_ECellEquipmentFunction.columns) if i >= 20 and i not in columns_to_exclude]
        row1 = data_ECellEquipmentFunction[data_ECellEquipmentFunction[reference_column] == cell1]

        if row1.empty:
            print(f"Reference cell '{cell1}' not found in the dataset.")
        else:
            row1_values = row1[value_columns].iloc[0]

            comparison_dict = {
                "MO Name": [os.path.splitext(os.path.basename(file_path_ECellEquipmentFunction))[0]] * len(value_columns),
                "Parameter Name": value_columns,
                cell1: row1_values,
            }

            for cell2 in cell2_list:
                row2 = data_ECellEquipmentFunction[data_ECellEquipmentFunction[reference_column] == cell2]

                if row2.empty:
                    print(f"Cell '{cell2}' not found in the dataset.")
                    comparison_dict[cell2] = ["Not Found"] * len(value_columns)
                    comparison_dict[f"Match_{cell2}"] = ["Not Found"] * len(value_columns)
                else:
                    row2_values = row2[value_columns].iloc[0]
                    comparison_dict[cell2] = row2_values
                    comparison_dict[f"Match_{cell2}"] = row1_values == row2_values

            final_comparison_df = pd.DataFrame(comparison_dict)
            final_comparison_df["Final_Match"] = final_comparison_df[match_columns].all(axis=1)
            final_comparison_df["Final_Match"] = final_comparison_df["Final_Match"].replace({True: "TRUE", False: "FALSE"})

            def append_comparison_to_excel(df, file_path, sheet_name="Comparison Results"):
                if os.path.exists(file_path):
                    with pd.ExcelFile(file_path) as existing_file:
                        if sheet_name in existing_file.sheet_names:
                            existing_df = pd.read_excel(existing_file, sheet_name=sheet_name)
                            df = pd.concat([existing_df, df], ignore_index=True)

                with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    workbook = writer.book
                    worksheet = writer.sheets[sheet_name]

                    default_format = workbook.add_format()
                    red_format = workbook.add_format({'font_color': 'red'})

                    if cell1 in df.columns:
                        for col_idx, col in enumerate(df.columns[2:2 + len(cell2_list) + 1]):
                            for row_idx, value in enumerate(df[col]):
                                value_to_write = handle_special_values(value)
                                reference_value = handle_special_values(df[cell1].iloc[row_idx])

                                if str(value_to_write) != str(reference_value):
                                    worksheet.write(row_idx + 1, col_idx + 2, value_to_write, red_format)
                                else:
                                    worksheet.write(row_idx + 1, col_idx + 2, value_to_write, default_format)
                    else:
                        print(f"Column '{cell1}' not found in the dataframe. Skipping highlight process.")

            append_comparison_to_excel(final_comparison_df, output_file)

        # Third section: PowerControlDL
        file_path_PowerControlDL = r"D:/Python course/Comparison Tool/Dumps/PowerControlDL.csv"
        data_PowerControlDL = pd.read_csv(file_path_PowerControlDL, low_memory=False)
        data_PowerControlDL["ldn"] = data_PowerControlDL["ldn"].str.replace(r",PowerControlDL=1$", "", regex=True)

        ECell_dict = dict(zip(data_EUtranCellFDD['ldn'], data_EUtranCellFDD['userLabel']))
        data_PowerControlDL['userLabel'] = data_PowerControlDL['ldn'].map(ECell_dict)

        value_columns = [col for i, col in enumerate(data_PowerControlDL.columns) if i >= 5 and i not in [3, 4, 5]]
        row1 = data_PowerControlDL[data_PowerControlDL[reference_column] == cell1]

        if row1.empty:
            print(f"Reference cell '{cell1}' not found in the dataset.")
        else:
            row1_values = row1[value_columns].iloc[0]

            comparison_dict = {
                "MO Name": [os.path.splitext(os.path.basename(file_path_PowerControlDL))[0]] * len(value_columns),
                "Parameter Name": value_columns,
                cell1: row1_values,
            }

            for cell2 in cell2_list:
                row2 = data_PowerControlDL[data_PowerControlDL[reference_column] == cell2]

                if row2.empty:
                    print(f"Cell '{cell2}' not found in the dataset.")
                    comparison_dict[cell2] = ["Not Found"] * len(value_columns)
                    comparison_dict[f"Match_{cell2}"] = ["Not Found"] * len(value_columns)
                else:
                    row2_values = row2[value_columns].iloc[0]
                    comparison_dict[cell2] = row2_values
                    comparison_dict[f"Match_{cell2}"] = row1_values == row2_values

            final_comparison_df = pd.DataFrame(comparison_dict)
            final_comparison_df["Final_Match"] = final_comparison_df[match_columns].all(axis=1)
            final_comparison_df["Final_Match"] = final_comparison_df["Final_Match"].replace({True: "TRUE", False: "FALSE"})

            append_comparison_to_excel(final_comparison_df, output_file)
            
        # Fourth section: PowerControlUL
        file_path_PowerControlUL = r"D:/Python course/Comparison Tool/Dumps/PowerControlUL.csv"
        data_PowerControlUL = pd.read_csv(file_path_PowerControlUL, low_memory=False)
        data_PowerControlUL["ldn"] = data_PowerControlUL["ldn"].str.replace(r",PowerControlUL=1$", "", regex=True)

        ECell_dict = dict(zip(data_EUtranCellFDD['ldn'], data_EUtranCellFDD['userLabel']))
        data_PowerControlUL['userLabel'] = data_PowerControlUL['ldn'].map(ECell_dict)

        columns_to_exclude = [3, 4, 5]
        value_columns = [col for i, col in enumerate(data_PowerControlUL.columns) if i >= 5 and i not in columns_to_exclude]

        row1 = data_PowerControlUL[data_PowerControlUL[reference_column] == cell1]

        if row1.empty:
            print(f"Reference cell '{cell1}' not found in the dataset.")
        else:
            row1_values = row1[value_columns].iloc[0]

            comparison_dict = {
                "MO Name": [os.path.splitext(os.path.basename(file_path_PowerControlUL))[0]] * len(value_columns),
                "Parameter Name": value_columns,
                cell1: row1_values,
            }

            for cell2 in cell2_list:
                row2 = data_PowerControlUL[data_PowerControlUL[reference_column] == cell2]

                if row2.empty:
                    print(f"Cell '{cell2}' not found in the dataset.")
                    comparison_dict[cell2] = ["Not Found"] * len(value_columns)
                    comparison_dict[f"Match_{cell2}"] = ["Not Found"] * len(value_columns)
                else:
                    row2_values = row2[value_columns].iloc[0]
                    comparison_dict[cell2] = row2_values
                    comparison_dict[f"Match_{cell2}"] = row1_values == row2_values

            final_comparison_df = pd.DataFrame(comparison_dict)
            final_comparison_df["Final_Match"] = final_comparison_df[match_columns].all(axis=1)
            final_comparison_df["Final_Match"] = final_comparison_df["Final_Match"].replace({True: "TRUE", False: "FALSE"})

            append_comparison_to_excel(final_comparison_df, output_file)
            # Fifth section: EUtranCellMeasurement

        file_path_EUtranCellMeasurement_1 = r"D:/Python course/Comparison Tool/Dumps/EUtranCellMeasurement-001.csv"
        file_paths = [ r"D:/Python course/Comparison Tool/Dumps/EUtranCellMeasurement-001.csv",
        r"D:/Python course/Comparison Tool/Dumps/EUtranCellMeasurement-002.csv",
        r"D:/Python course/Comparison Tool/Dumps/EUtranCellMeasurement-003.csv"]

        # Read and concatenate all CSV files into a single DataFrame
        data_EUtranCellMeasurement = pd.concat([pd.read_csv(file) for file in file_paths], ignore_index=True)
        data_EUtranCellMeasurement["ldn"] = data_EUtranCellMeasurement["ldn"].str.replace(r",EUtranCellMeasurement=1$", "", regex=True)

        # Map 'userLabel' from EUtranCellFDD
        ECell_dict = dict(zip(data_EUtranCellFDD['ldn'], data_EUtranCellFDD['userLabel']))
        data_EUtranCellMeasurement['userLabel'] = data_EUtranCellMeasurement['ldn'].map(ECell_dict)

        # Identify value columns (exclude specific columns)
        columns_to_exclude = [3, 4, 5]
        value_columns = [col for i, col in enumerate(data_EUtranCellMeasurement.columns) if i >= 4 and i not in columns_to_exclude]

        # Filter reference cell row
        row1 = data_EUtranCellMeasurement[data_EUtranCellMeasurement[reference_column] == cell1]

        if row1.empty:
            print(f"Reference cell '{cell1}' not found in the dataset.")
        else:
            row1_values = row1[value_columns].iloc[0]

        comparison_dict = {"MO Name": [os.path.splitext(os.path.basename(file_path_EUtranCellMeasurement_1))[0]] * len(value_columns),
        "Parameter Name": value_columns,
        cell1: row1_values,  }

        for cell2 in cell2_list:
            row2 = data_EUtranCellMeasurement[data_EUtranCellMeasurement[reference_column] == cell2]
            if row2.empty:
                print(f"Cell '{cell2}' not found in the dataset.")
                comparison_dict[cell2] = ["Not Found"] * len(value_columns)
                comparison_dict[f"Match_{cell2}"] = ["Not Found"] * len(value_columns)
            else:
                row2_values = row2[value_columns].iloc[0]
                comparison_dict[cell2] = row2_values
                comparison_dict[f"Match_{cell2}"] = row1_values == row2_values
         
        final_comparison_df = pd.DataFrame(comparison_dict)
        final_comparison_df["Final_Match"] = final_comparison_df[match_columns].all(axis=1)
        final_comparison_df["Final_Match"] = final_comparison_df["Final_Match"].replace({True: "TRUE", False: "FALSE"})

        #append_comparison_to_excel(final_comparison_df, output_file)
        append_comparison_to_excel(final_comparison_df, output_file)
        
        # Sixh section: EUtranCellMeasurement
        file_path_EUtranReselection = r"D:/Python course/Comparison Tool/Dumps/EUtranReselection.csv"
        # Store the CSV file data as a dataframe
        data_EUtranReselection = pd.read_csv(file_path_EUtranReselection, low_memory=False)
        data_EUtranReselection["ldn"] = data_EUtranReselection["ldn"].str.replace(r",EUtranReselection=1$", "", regex=True)
        # Vlookup to add user label column to the data frame EUtranReselection
        ECell_dict = dict(zip(data_EUtranCellFDD['ldn'],data_EUtranCellFDD['userLabel']))
        data_EUtranReselection['userLabel']=data_EUtranReselection['ldn'].map(ECell_dict)
        # Identify value columns (columns after "E", index 5)
        value_columns = data_EUtranReselection.columns[5:]
        columns_to_exclude = [3,4,5]
        value_columns = [col for i, col in enumerate(data_EUtranReselection.columns) if i >= 5 and i not in columns_to_exclude]
        # Filter row for cell1
        row1 = data_EUtranReselection[data_EUtranReselection[reference_column] == cell1]
        
        # Ensure cell1 row is found
        if row1.empty:
            print(f"Reference cell '{cell1}' not found in the dataset.")
        else:
            row1_values = row1[value_columns].iloc[0]  # Extract values for cell1
        
            # Initialize a dictionary for storing comparison data
            comparison_dict = {
                "MO Name": [os.path.splitext(os.path.basename(file_path_EUtranReselection))[0]] * len(value_columns),
                "Parameter Name": value_columns,
                cell1: row1_values,  # Store cell1 values
            }
        
            # Iterate through each cell2 value and store results in separate columns
            for cell2 in cell2_list:
                row2 = data_EUtranReselection[data_EUtranReselection[reference_column] == cell2]
        
                # If cell2 is not found, fill with "Not Found"
                if row2.empty:
                    print(f"Cell '{cell2}' not found in the dataset.")
                    comparison_dict[cell2] = ["Not Found"] * len(value_columns)
                    comparison_dict[f"Match_{cell2}"] = ["Not Found"] * len(value_columns)
                else:
                    row2_values = row2[value_columns].iloc[0]  # Extract values for cell2
                    comparison_dict[cell2] = row2_values  # Store cell2 values
                    comparison_dict[f"Match_{cell2}"] = row1_values == row2_values  # Store match results
        
            # Convert dictionary to DataFrame
            final_comparison_df = pd.DataFrame(comparison_dict)
        
            # Add the Final_Match column
            #match_columns = [f"Match_{cell2}" for cell2 in cell2_list]  # Get all match columns
            final_comparison_df["Final_Match"] = final_comparison_df[match_columns].all(axis=1)  # Check if all match columns are True
            final_comparison_df["Final_Match"] = final_comparison_df["Final_Match"].replace({True: "TRUE", False: "FALSE"})  # Convert to "TRUE"/"FALSE"
            # Call the function to append the new comparison results to the Excel file
            append_comparison_to_excel(final_comparison_df, output_file)
            
        # Seventh section: Load MNGCELL
        # Define file paths            
        file_path_LoadMNGCell = r"D:/Python course/Comparison Tool/Dumps/LoadMNGCell.csv"
        # Store the CSV file data as a dataframe
        data_LoadMNGCell = pd.read_csv(file_path_LoadMNGCell, low_memory=False)            
        data_LoadMNGCell["ldn"] = data_LoadMNGCell["ldn"].str.replace(r",LoadMNGCell=1$", "", regex=True)
        # Vlookup to add user label column to the data frame LoadMNGCell
        ECell_dict = dict(zip(data_EUtranCellFDD['ldn'],data_EUtranCellFDD['userLabel']))
        data_LoadMNGCell['userLabel']=data_LoadMNGCell['ldn'].map(ECell_dict)
        # Identify value columns (columns after "E", index 5)
        value_columns = data_LoadMNGCell.columns[5:]
        columns_to_exclude = [3,4,5]
        value_columns = [col for i, col in enumerate(data_LoadMNGCell.columns) if i >= 5 and i not in columns_to_exclude]
        
        # Filter row for cell1
        row1 = data_LoadMNGCell[data_LoadMNGCell[reference_column] == cell1]
        
        # Ensure cell1 row is found
        if row1.empty:
            print(f"Reference cell '{cell1}' not found in the dataset.")
        else:
            row1_values = row1[value_columns].iloc[0]  # Extract values for cell1
        
            # Initialize a dictionary for storing comparison data
            comparison_dict = {
                "MO Name": [os.path.splitext(os.path.basename(file_path_LoadMNGCell))[0]] * len(value_columns),
                "Parameter Name": value_columns,
                cell1: row1_values,  # Store cell1 values
            }
        
            # Iterate through each cell2 value and store results in separate columns
            for cell2 in cell2_list:
                row2 = data_LoadMNGCell[data_LoadMNGCell[reference_column] == cell2]
        
                # If cell2 is not found, fill with "Not Found"
                if row2.empty:
                    print(f"Cell '{cell2}' not found in the dataset.")
                    comparison_dict[cell2] = ["Not Found"] * len(value_columns)
                    comparison_dict[f"Match_{cell2}"] = ["Not Found"] * len(value_columns)
                else:
                    row2_values = row2[value_columns].iloc[0]  # Extract values for cell2
                    comparison_dict[cell2] = row2_values  # Store cell2 values
                    comparison_dict[f"Match_{cell2}"] = row1_values == row2_values  # Store match results
        
            # Convert dictionary to DataFrame
            final_comparison_df = pd.DataFrame(comparison_dict)
            
            # Add the Final_Match column
            #match_columns = [f"Match_{cell2}" for cell2 in cell2_list]  # Get all match columns
            final_comparison_df["Final_Match"] = final_comparison_df[match_columns].all(axis=1)  # Check if all match columns are True
            final_comparison_df["Final_Match"] = final_comparison_df["Final_Match"].replace({True: "TRUE", False: "FALSE"})  # Convert to "TRUE"/"FALSE"
            # Call the function to append the new comparison results to the Excel file
            append_comparison_to_excel(final_comparison_df, output_file)
        # Define file paths
        
        file_path_LoadControlCell = r"D:/Python course/Comparison Tool/Dumps/LoadControlCell.csv"
        # Store the CSV file data as a dataframe
        data_LoadControlCell = pd.read_csv(file_path_LoadControlCell, low_memory=False)
        
        data_LoadControlCell["ldn"] = data_LoadControlCell["ldn"].str.replace(r",LoadControlCell=1$", "", regex=True)
        # Vlookup to add user label column to the data frame LoadControlCell
        ECell_dict = dict(zip(data_EUtranCellFDD['ldn'],data_EUtranCellFDD['userLabel']))
        data_LoadControlCell['userLabel']=data_LoadControlCell['ldn'].map(ECell_dict)
        
        # Identify value columns (columns after "E", index 5)
        value_columns = data_LoadControlCell.columns[5:]
        columns_to_exclude = [3,4,5]
        value_columns = [col for i, col in enumerate(data_LoadControlCell.columns) if i >= 5 and i not in columns_to_exclude]
        
        # Filter row for cell1
        row1 = data_LoadControlCell[data_LoadControlCell[reference_column] == cell1]
        
        # Ensure cell1 row is found
        if row1.empty:
            print(f"Reference cell '{cell1}' not found in the dataset.")
        else:
            row1_values = row1[value_columns].iloc[0]  # Extract values for cell1
        
            # Initialize a dictionary for storing comparison data
            comparison_dict = {
                "MO Name": [os.path.splitext(os.path.basename(file_path_LoadControlCell))[0]] * len(value_columns),
                "Parameter Name": value_columns,
                cell1: row1_values,  # Store cell1 values
            }
        
            # Iterate through each cell2 value and store results in separate columns
            for cell2 in cell2_list:
                row2 = data_LoadControlCell[data_LoadControlCell[reference_column] == cell2]
        
                # If cell2 is not found, fill with "Not Found"
                if row2.empty:
                    print(f"Cell '{cell2}' not found in the dataset.")
                    comparison_dict[cell2] = ["Not Found"] * len(value_columns)
                    comparison_dict[f"Match_{cell2}"] = ["Not Found"] * len(value_columns)
                else:
                    row2_values = row2[value_columns].iloc[0]  # Extract values for cell2
                    comparison_dict[cell2] = row2_values  # Store cell2 values
                    comparison_dict[f"Match_{cell2}"] = row1_values == row2_values  # Store match results
        
            # Convert dictionary to DataFrame
            final_comparison_df = pd.DataFrame(comparison_dict)
        
            # Add the Final_Match column
            #match_columns = [f"Match_{cell2}" for cell2 in cell2_list]  # Get all match columns
            final_comparison_df["Final_Match"] = final_comparison_df[match_columns].all(axis=1)  # Check if all match columns are True
            final_comparison_df["Final_Match"] = final_comparison_df["Final_Match"].replace({True: "TRUE", False: "FALSE"})  # Convert to "TRUE"/"FALSE"
            
            #Call the function to append the new comparison results to the Excel file
            append_comparison_to_excel(final_comparison_df, output_file)
        # Define file paths
        file_path_PhyChannel = r"D:/Python course/Comparison Tool/Dumps/PhyChannel.csv"
        # Store the CSV file data as a dataframe
        data_PhyChannel = pd.read_csv(file_path_PhyChannel, low_memory=False)
        
        
        # Remove "PhyChannel=1" from all rows in 'ldn' column
        data_PhyChannel["ldn"] = data_PhyChannel["ldn"].str.replace(r",PhyChannel=1$", "", regex=True)
        
        
        # Vlookup to add user label column to the data frame PhyChannel
        ECell_dict = dict(zip(data_EUtranCellFDD['ldn'],data_EUtranCellFDD['userLabel']))
        data_PhyChannel['userLabel']=data_PhyChannel['ldn'].map(ECell_dict)
        
        # Identify value columns (columns after "E", index 5)
        value_columns = data_PhyChannel.columns[5:]
        columns_to_exclude = [3,4,5]
        value_columns = [col for i, col in enumerate(data_PhyChannel.columns) if i >= 5 and i not in columns_to_exclude]
        
        # Filter row for cell1
        row1 = data_PhyChannel[data_PhyChannel[reference_column] == cell1]
        
        # Ensure cell1 row is found
        if row1.empty:
            print(f"Reference cell '{cell1}' not found in the dataset.")
        else:
            row1_values = row1[value_columns].iloc[0]  # Extract values for cell1
        
            # Initialize a dictionary for storing comparison data
            comparison_dict = {
                "MO Name": [os.path.splitext(os.path.basename(file_path_PhyChannel))[0]] * len(value_columns),
                "Parameter Name": value_columns,
                cell1: row1_values,  # Store cell1 values
            }
        
            # Iterate through each cell2 value and store results in separate columns
            for cell2 in cell2_list:
                row2 = data_PhyChannel[data_PhyChannel[reference_column] == cell2]
        
                # If cell2 is not found, fill with "Not Found"
                if row2.empty:
                    print(f"Cell '{cell2}' not found in the dataset.")
                    comparison_dict[cell2] = ["Not Found"] * len(value_columns)
                    comparison_dict[f"Match_{cell2}"] = ["Not Found"] * len(value_columns)
                else:
                    row2_values = row2[value_columns].iloc[0]  # Extract values for cell2
                    comparison_dict[cell2] = row2_values  # Store cell2 values
                    comparison_dict[f"Match_{cell2}"] = row1_values == row2_values  # Store match results
        
            # Convert dictionary to DataFrame
            final_comparison_df = pd.DataFrame(comparison_dict)
        
            # Add the Final_Match column
            #match_columns = [f"Match_{cell2}" for cell2 in cell2_list]  # Get all match columns
            final_comparison_df["Final_Match"] = final_comparison_df[match_columns].all(axis=1)  # Check if all match columns are True
            final_comparison_df["Final_Match"] = final_comparison_df["Final_Match"].replace({True: "TRUE", False: "FALSE"})  # Convert to "TRUE"/"FALSE" 
            # Call the function to append the new comparison results to the Excel file
            append_comparison_to_excel(final_comparison_df, output_file)
        # Define file paths
        
        file_path_SceneConfig = r"D:/Python course/Comparison Tool/Dumps/SceneConfig.csv"
        # Store the CSV file data as a dataframe
        data_SceneConfig = pd.read_csv(file_path_SceneConfig, low_memory=False)
        
        
        # Remove "SceneConfig=1" from all rows in 'ldn' column
        data_SceneConfig["ldn"] = data_SceneConfig["ldn"].str.replace(r",SceneConfig=1$", "", regex=True)
        
        
        # Vlookup to add user label column to the data frame SceneConfig
        ECell_dict = dict(zip(data_EUtranCellFDD['ldn'],data_EUtranCellFDD['userLabel']))
        data_SceneConfig['userLabel']=data_SceneConfig['ldn'].map(ECell_dict)
        
        # Identify value columns (columns after "E", index 5)
        value_columns = data_SceneConfig.columns[5:]
        columns_to_exclude = [3,4,5]
        value_columns = [col for i, col in enumerate(data_SceneConfig.columns) if i >= 5 and i not in columns_to_exclude]
        
        # Filter row for cell1
        row1 = data_SceneConfig[data_SceneConfig[reference_column] == cell1]
        
        # Ensure cell1 row is found
        if row1.empty:
            print(f"Reference cell '{cell1}' not found in the dataset.")
        else:
            row1_values = row1[value_columns].iloc[0]  # Extract values for cell1
        
            # Initialize a dictionary for storing comparison data
            comparison_dict = {
                "MO Name": [os.path.splitext(os.path.basename(file_path_SceneConfig))[0]] * len(value_columns),
                "Parameter Name": value_columns,
                cell1: row1_values,  # Store cell1 values
            }
        
            # Iterate through each cell2 value and store results in separate columns
            for cell2 in cell2_list:
                row2 = data_SceneConfig[data_SceneConfig[reference_column] == cell2]
        
                # If cell2 is not found, fill with "Not Found"
                if row2.empty:
                    print(f"Cell '{cell2}' not found in the dataset.")
                    comparison_dict[cell2] = ["Not Found"] * len(value_columns)
                    comparison_dict[f"Match_{cell2}"] = ["Not Found"] * len(value_columns)
                else:
                    row2_values = row2[value_columns].iloc[0]  # Extract values for cell2
                    comparison_dict[cell2] = row2_values  # Store cell2 values
                    comparison_dict[f"Match_{cell2}"] = row1_values == row2_values  # Store match results
        
            # Convert dictionary to DataFrame
            final_comparison_df = pd.DataFrame(comparison_dict)
        
            # Add the Final_Match column
            #match_columns = [f"Match_{cell2}" for cell2 in cell2_list]  # Get all match columns
            final_comparison_df["Final_Match"] = final_comparison_df[match_columns].all(axis=1)  # Check if all match columns are True
            final_comparison_df["Final_Match"] = final_comparison_df["Final_Match"].replace({True: "TRUE", False: "FALSE"})  # Convert to "TRUE"/"FALSE"
            # Call the function to append the new comparison results to the Excel file
            append_comparison_to_excel(final_comparison_df, output_file)
        
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, f"Reference cell: {cell1}\n")
        output_text.insert(tk.END, "Compared Cells list:\n")
        output_text.insert(tk.END, "\n".join(cell2_list))
        output_text.insert(tk.END, "\n\nDone. Please check output file.\n")

        messagebox.showinfo("Success", "Execution completed successfully.")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

# Create main window
root = tk.Tk()
root.title("For queries ::03000871272")
root.geometry("500x400")
root.configure(bg="#f0f4f7")

# Styling
style = ttk.Style()
style.theme_use('default')

style.configure("TButton", font=("Segoe UI", 10), padding=6)
style.configure("Green.TButton", font=("Segoe UI", 10), padding=6, background="#4CAF50", foreground="white")
style.map("Green.TButton",
          background=[("active", "#45a049")],
          foreground=[("disabled", "gray")])

style.configure("TLabel", font=("Segoe UI", 10))
style.configure("TEntry", font=("Segoe UI", 10))

# Header label
header = tk.Label(root, text="SDR Cell Comparison Tool", font=("Segoe UI", 14, "bold"),
                  bg="#f0f4f7", fg="#003366")
header.pack(pady=(20, 10))

# Title label
title = tk.Label(root, text="Developed by: M.Shahzad Afzal", font=("Segoe UI", 10, "bold"),
                 bg="#f0f4f7", fg="green")
title.pack()

# Entry label
label = ttk.Label(root, text="Enter reference cell (cell1):")
label.pack(pady=(10, 5))

# Entry widget
entry = ttk.Entry(root, width=40)
entry.pack()

# Compare Button
button = ttk.Button(root, text="Compare", command=execute_code, style="Green.TButton")
button.pack(pady=10)

# Output text box inside a frame with scrollbar
output_frame = tk.Frame(root, bg="#f0f4f7")
output_frame.pack(pady=10, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(output_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

output_text = tk.Text(output_frame, height=10, width=60, wrap=tk.WORD, yscrollcommand=scrollbar.set,
                      font=("Consolas", 9), bg="#ffffff", fg="#333333", relief=tk.SUNKEN, bd=1)
output_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

scrollbar.config(command=output_text.yview)

# Run main loop
root.mainloop()


# In[ ]:




