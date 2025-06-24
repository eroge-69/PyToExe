# Create Excel writer
with pd.ExcelWriter('india_telecom_data.xlsx') as writer:
    pd.DataFrame(wireless_data, index=years).to_excel(writer, sheet_name='Wireless')
    pd.DataFrame(wireline_data, index=years).to_excel(writer, sheet_name='Wireline')
    pd.DataFrame(mso_data, index=years).to_excel(writer, sheet_name='MSO')
    pd.DataFrame(dth_data, index=years).to_excel(writer, sheet_name='DTH')
    pd.DataFrame(ott_data, index=years).to_excel(writer, sheet_name='OTT & YouTube')