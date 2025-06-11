import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os
from pathlib import Path

def main_function():
  file_name = next((f for f in os.listdir('uploaded_files') if f.startswith('Batch')), None)
  file_path = os.path.join('uploaded_files', file_name)
  freedom_pay = pd.read_excel(file_path)     # dataframe to store freedom pay entries
  freedom_pay.columns = ['Batch_ID', 'Processor', 'Batch_Open_Date', 'Batch_Close_Date', 'drop', 'Batch_Send_Start', 'Batch_Send_Finish', 'Batch_Status', 'Store_ID', 'Store_Name', 'Store_Alias', 'MID', 'Trans_Count', 'Net_Amount', 'Drop_Again', 'Currency']
  freedom_pay.drop(columns=['drop', 'Drop_Again'], inplace=True)
  freedom_pay = freedom_pay.iloc[1:-2]
  freedom_pay['Net_Amount'] = pd.to_numeric(freedom_pay['Net_Amount'], errors='coerce').astype('float64')
  freedom_pay = freedom_pay[freedom_pay['Store_Name'] == "ATLNR PMS"]
  freedom_pay['Batch_Open_Date'] = pd.to_datetime(
      freedom_pay['Batch_Open_Date'], format='%m/%d/%Y', errors='coerce'
  )

  file_name = next((f for f in os.listdir('uploaded_files') if f.startswith('transaction')), None)
  file_path = os.path.join('uploaded_files', file_name)
  bank_statement = pd.read_excel(file_path)    # dataframe to store bank statement entries
  bank_statement.columns = ['Date', 'Description', 'Original_Description', 'Amount', 'Type', 'Parent Category', 'Category', 'Account', 'Tags', 'Memo', 'Pending']
  bank_statement['Description_First_Word'] = bank_statement['Description'].str.split().str[0]
  bank_statement_credit = bank_statement[bank_statement['Type'] == 'Credit']
  bank_statement_debit = bank_statement[bank_statement['Type'] == 'Debit']


  #Finding the total
  freedom_pay_total = freedom_pay.iloc[-1]
  freedom_pay_total = freedom_pay_total.iloc[-4:]
  freedom_pay = freedom_pay.iloc[1:-1]

  bank_statement_total =[np.sum(bank_statement_debit['Amount']), 'USD']


  # print(bank_statement_credit['Description_First_Word'].unique())

  # print(freedom_pay['Processor'].unique())

  tracker = pd.DataFrame(columns=['Batch_ID', 'Net_Amount', 'Found', 'Freedom_Pay_Date', 'Bank_Statement_Date'])
  tracker['Batch_ID'] = freedom_pay['Batch_ID']
  tracker['Processor'] = freedom_pay['Processor']
  tracker['Net_Amount'] = freedom_pay['Net_Amount']
  tracker['Found'] = False
  tracker['Freedom_Pay_Date'] = freedom_pay['Batch_Open_Date'].dt.strftime('%m/%d/%Y')
  tracker['Bank_Statement_Date'] = 0



  # print(bank_statement_credit['Amount'])

  # print(freedom_pay['Net_Amount'])

  for i in range(freedom_pay.shape[0]):
    current_record = freedom_pay.iloc[i]
    current_record_amount = current_record['Net_Amount']

    for j in range(bank_statement_credit.shape[0]):
      current_bank_statement_record = bank_statement_credit.iloc[j]
      current_bank_statement_record_amount = current_bank_statement_record['Amount']
      if (current_record_amount == current_bank_statement_record_amount):
        tracker.loc[tracker['Net_Amount'] == current_record_amount, 'Found'] = True
        tracker.loc[tracker['Net_Amount'] == current_record_amount, 'Bank_Statement_Date'] = current_bank_statement_record['Date'].strftime('%m/%d/%Y')



  #dealing with remaining discover entries
  discover_bank_statement = bank_statement[bank_statement['Description'] == 'Discover Network Settlement']
  discover_freedom_pay = freedom_pay[freedom_pay['Processor'] == 'ChaseDD']


  discover_bank_statement = discover_bank_statement.sort_values(by='Date')
  discover_bank_statement['flag'] = 0


  tolerance = 0.10

  for i in range(discover_freedom_pay.shape[0]):
    current_record = discover_freedom_pay.iloc[i]
    current_record_amount = current_record['Net_Amount']
    current_record_date = current_record['Batch_Open_Date']

    for j in range(discover_bank_statement.shape[0]):
      current_bank_statement_record = discover_bank_statement.iloc[j]
      if (current_bank_statement_record['flag'] == 1):
        continue
      discover_bank_statement.at[j, 'flag'] = 1
      current_bank_statement_record_amount = current_bank_statement_record['Amount']
      current_bank_statement_record_date = current_bank_statement_record['Date']

      percentage_difference = abs((current_record_amount - current_bank_statement_record_amount) / current_record_amount)
      date_difference = current_bank_statement_record_date - current_record_date
      number_of_days_difference = date_difference.days

      if (percentage_difference <= tolerance and number_of_days_difference < 7):
        tracker.loc[tracker['Net_Amount'] == current_record_amount, 'Found'] = True
        tracker.loc[tracker['Net_Amount'] == current_record_amount, 'Bank_Statement_Date'] = current_bank_statement_record['Date'].strftime('%m/%d/%Y')




  # save and Download the file
  downloads_path = str(Path.home() / "Downloads")

  output_file = os.path.join(downloads_path, "Automate.xlsx")

  tracker.to_excel(output_file, index=False)


  print("done")
