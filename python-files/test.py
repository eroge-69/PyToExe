import pandas as pd
import sys
import os

def summarize_fc_disbursements(input_file, output_file):
    """
    Reads loan data from ODS file and summarizes total disbursed amounts by FC
    
    Args:
        input_file (str): Path to input ODS file
        output_file (str): Path to output file (Excel or ODS)
    """
    try:
        # Read the ODS file
        print(f"Reading data from {input_file}...")
        df = pd.read_excel(input_file, engine='odf')
        
        # Check if required columns exist
        if 'L' not in df.columns and len(df.columns) < 12:
            # If columns are named differently, try to use column indices
            if len(df.columns) >= 12:
                fc_column = df.iloc[:, 11]  # Column L (index 11)
                disbursed_column = df.iloc[:, 4]  # Column E (index 4)
            else:
                raise ValueError("Input file doesn't have enough columns")
        else:
            # Use column names if available
            fc_column = df.iloc[:, 11] if len(df.columns) > 11 else df['L']
            disbursed_column = df.iloc[:, 4] if len(df.columns) > 4 else df['E']
        
        # Create a new dataframe with FC and disbursed amounts
        data = pd.DataFrame({
            'FC_Name': fc_column,
            'Disbursed_Amount': disbursed_column
        })
        
        # Remove rows where FC name is empty or NaN
        data = data.dropna(subset=['FC_Name'])
        data = data[data['FC_Name'] != '']
        
        # Convert disbursed amount to numeric, replacing non-numeric values with 0
        data['Disbursed_Amount'] = pd.to_numeric(data['Disbursed_Amount'], errors='coerce').fillna(0)
        
        # Group by FC and calculate both sum and count
        summary = data.groupby('FC_Name').agg({
            'Disbursed_Amount': ['sum', 'count']
        }).reset_index()
        
        # Flatten column names
        summary.columns = ['FC Name', 'Total Disbursed Amount', 'Number of Clients']
        
        # Sort by total disbursed amount (descending)
        summary = summary.sort_values('Total Disbursed Amount', ascending=False)
        
        # Add a total row
        total_row = pd.DataFrame({
            'FC Name': ['TOTAL'],
            'Total Disbursed Amount': [summary['Total Disbursed Amount'].sum()],
            'Number of Clients': [summary['Number of Clients'].sum()]
        })
        summary = pd.concat([summary, total_row], ignore_index=True)
        
        # Determine output format based on file extension
        print(f"Writing results to {output_file}...")
        
        if output_file.lower().endswith('.ods'):
            # Write to ODS file
            summary.to_excel(output_file, engine='odf', sheet_name='FC Summary', index=False)
        else:
            # Write to Excel file (default)
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                summary.to_excel(writer, sheet_name='FC Summary', index=False)
                
                # Format the Excel file
                workbook = writer.book
                worksheet = writer.sheets['FC Summary']
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                
                # Format numbers as currency and count styling
                from openpyxl.styles import NamedStyle
                currency_style = NamedStyle(name='currency', number_format='#,##0.00')
                number_style = NamedStyle(name='number', number_format='#,##0')
                
                for row in range(2, len(summary) + 2):
                    worksheet[f'B{row}'].style = currency_style  # Disbursed Amount
                    worksheet[f'C{row}'].style = number_style    # Number of Clients
        
        print(f"Summary completed successfully!")
        print(f"Total FCs processed: {len(summary) - 1}")  # -1 to exclude total row
        print(f"Total clients served: {summary.iloc[-1]['Number of Clients']:,}")
        print(f"Total amount disbursed: {summary.iloc[-1]['Total Disbursed Amount']:,.2f}")
        print(f"Average disbursement per client: {summary.iloc[-1]['Total Disbursed Amount'] / summary.iloc[-1]['Number of Clients']:,.2f}")
        
        return summary
        
    except FileNotFoundError:
        print(f"Error: Could not find the file '{input_file}'")
        print("Please check the file path and try again.")
        return None
    except ImportError:
        print("Error: Required libraries not installed.")
        print("Please install required packages with:")
        print("pip install pandas openpyxl odfpy")
        return None
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return None

def main():
    # Get file paths from user
    if len(sys.argv) == 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    else:
        input_file = input("Enter the path to your input ODS file: ").strip('"')
        output_file = input("Enter the path for the output file (Excel .xlsx or ODS .ods): ").strip('"')
        
        # Add appropriate extension if not provided
        if not output_file.endswith(('.xlsx', '.ods')):
            output_file += '.xlsx'  # Default to Excel if no extension
    
    # Process the files
    result = summarize_fc_disbursements(input_file, output_file)
    
    if result is not None:
        print("\nTop 5 FCs by disbursed amount:")
        print(result.head().to_string(index=False))
        
        print(f"\nTop FC Performance:")
        if len(result) > 1:  # Exclude total row
            top_fc = result.iloc[0]
            print(f"• {top_fc['FC Name']}: {top_fc['Number of Clients']:,} clients, {top_fc['Total Disbursed Amount']:,.2f} total")

if __name__ == "__main__":
    main()