#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import json
import io
import time
import pandas as pd


# In[10]:


api_key = input("API Key: ")
path = input("Path: ")
headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "vi",
    "Authorization": api_key,
    "Connection": "keep-alive",
    "Host": "hoadondientu.gdt.gov.vn:30000",
    "Origin": "https://hoadondientu.gdt.gov.vn",
    "Referer": "https://hoadondientu.gdt.gov.vn/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
    "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Microsoft Edge\";v=\"138\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\""
}
df_detail=pd.DataFrame()


# In[5]:


from_date = input("From dd/mm/yyyy: ")
to_date = input("To dd/mm/yyyy: ")

df_head = pd.DataFrame()

url_input_head = "https://hoadondientu.gdt.gov.vn:30000/query/invoices/export-excel-sold?sort=tdlap:desc,khmshdon:asc,shdon:desc&search=tdlap=ge="+from_date+"T00:00:00;tdlap=le="+to_date+"T23:59:59;ttxly==5%20%20%20%20&type=purchase"

response = requests.get(url_input_head,headers=headers,verify=False)

# Convert response content to a BytesIO object for pandas
excel_data = io.BytesIO(response.content)
        
# Read Excel file into DataFrame
df = pd.read_excel(excel_data, engine='openpyxl')
df = df.iloc[4:].reset_index(drop=True)

# Promote the first remaining row as the header
new_header = df.iloc[0]  # Take the first row for column names
df = df[1:]  # Remove the header row from data
df.columns = new_header  # Set the new header
df = df.drop(df.columns[0], axis=1)
df_head = pd.concat([df_head, df], ignore_index=True)
time.sleep(0.5)

url_input_head = "https://hoadondientu.gdt.gov.vn:30000/query/invoices/export-excel-sold?sort=tdlap:desc,khmshdon:asc,shdon:desc&search=tdlap=ge="+from_date+"T00:00:00;tdlap=le="+to_date+"T23:59:59;ttxly==6%20%20%20%20&type=purchase"

response = requests.get(url_input_head,headers=headers,verify=False)

# Convert response content to a BytesIO object for pandas
excel_data = io.BytesIO(response.content)
        
# Read Excel file into DataFrame
df = pd.read_excel(excel_data, engine='openpyxl')
df = df.iloc[4:].reset_index(drop=True)

# Promote the first remaining row as the header
new_header = df.iloc[0]  # Take the first row for column names
df = df[1:]  # Remove the header row from data
df.columns = new_header  # Set the new header
df = df.drop(df.columns[0], axis=1)
df_head = pd.concat([df_head, df], ignore_index=True)
time.sleep(0.5)

url_input_head = "https://hoadondientu.gdt.gov.vn:30000/sco-query/invoices/export-excel-sold?sort=tdlap:desc,khmshdon:asc,shdon:desc&search=tdlap=ge="+from_date+"T00:00:00;tdlap=le="+to_date+"T23:59:59;ttxly==8%20%20%20%20&type=purchase"

response = requests.get(url_input_head,headers=headers,verify=False)

# Convert response content to a BytesIO object for pandas
excel_data = io.BytesIO(response.content)
        
# Read Excel file into DataFrame
df = pd.read_excel(excel_data, engine='openpyxl')
df = df.iloc[4:].reset_index(drop=True)

# Promote the first remaining row as the header
new_header = df.iloc[0]  # Take the first row for column names
df = df[1:]  # Remove the header row from data
df.columns = new_header  # Set the new header
df = df.drop(df.columns[0], axis=1)
df_head = pd.concat([df_head, df], ignore_index=True)
time.sleep(0.5)

print("Total: "+str(len(df_head))+" invoices | Loop from 0 to "+str(len(df_head)-1))
df_head.to_excel(path+r'\Input_Invoice_Header.xlsx', index=False)
print("Extract INPUT INVOICE HEADER done: "+path+r'\Input_Invoice_Header.xlsx')


# In[39]:


while True:
    
    error=[]
    loop_from=int(input("Loop from: "))
    loop_to=int(input("Loop to: "))

    for i in range(loop_from,loop_to+1):
        try:
            invoice = df_head[['MST người bán/MST người xuất hàng','Ký hiệu hóa đơn','Số hóa đơn','Ký hiệu mẫu số','Kết quả kiểm tra hóa đơn']].iloc[i]
            if invoice[4]=="Tổng cục thuế đã nhận hóa đơn có mã khởi tạo từ máy tính tiền":
                url_detail = "https://hoadondientu.gdt.gov.vn:30000/sco-query/invoices/detail?nbmst="+invoice[0]+"&khhdon="+invoice[1]+"&shdon="+invoice[2]+"&khmshdon="+invoice[3]
            else:
                url_detail = "https://hoadondientu.gdt.gov.vn:30000/query/invoices/detail?nbmst="+invoice[0]+"&khhdon="+invoice[1]+"&shdon="+invoice[2]+"&khmshdon="+invoice[3]    
            response = requests.get(url_detail,headers=headers,verify=False)
            json_data = response.json()
            
            # Create a list to hold DataFrame rows
            rows = []
            
            # Extract top-level fields, excluding nested structures
            base_data = {key: value for key, value in json_data.items() if key not in ['hdhhdvu', 'nbttkhac', 'nmttkhac', 'ttkhac', 'ttttkhac', 'thttltsuat', 'cttkhac', 'thttlphi', 'tthhdtrung']}
            
            # Expand hdhhdvu into separate rows
            try:
                for item in json_data['hdhhdvu']:
                        row = base_data.copy()
                        # Add hdhhdvu fields
                        for key, value in item.items():
                            if key != 'ttkhac' and key != 'tthhdtrung':
                                row[f"hdhhdvu_{key}"] = value
                        # Add hdhhdvu.ttkhac fields
                        for subitem in item['ttkhac']:
                            row[f"hdhhdvu_ttkhac_{subitem['ttruong']}"] = subitem['dlieu']
                        rows.append(row)
            except:
                continue
            # Create DataFrame
            df_detail_temp = pd.DataFrame(rows)
            df_detail = pd.concat([df_detail, df_detail_temp], ignore_index=True)
            print(str(i)+"/"+str(len(df_head)-1))
            time.sleep(0.5)
    
        except:
            error.append(i)
            check = input("Choose (0) to EXIT and (1) to CONTINUE: ")
            if check=="0":
                break
            else:
                continue
    
    df_detail.to_excel(path+r'\Input_Invoice_Detail.xlsx', index=False)
    print("Extract INPUT INVOICE DETAIL done: "+path+r'\Input_Invoice_Header.xlsx')
    print("List error: "+str(error))
    for i in error:
        invoice = df_head[['MST người bán/MST người xuất hàng','Ký hiệu hóa đơn','Số hóa đơn','Ký hiệu mẫu số','Kết quả kiểm tra hóa đơn']].iloc[i]
        print(invoice)
    
    var=input("Choose (0) to EXIT and (1) to CONTINUE: ")
    if var=="0":
        break
    else:
        print("Please wait at least 5 mins before trying again...")
        True

