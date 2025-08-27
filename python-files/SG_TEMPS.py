import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import os
import glob
import zipfile
import pandas as pd

def col_to_index(col_letter):
    col_letter = col_letter.upper()
    index = 0
    for char in col_letter:
        index = index * 26 + (ord(char) - ord('A') + 1)
    return index - 1


def fix_temperature(val):
    if isinstance(val, str):
        val = val.replace(',', '.')
    try:
        f = float(val)
    except Exception:
        return None

    if f > 100:
        f = f / 1e13
        
    return f


def process_csv(file_obj):
    
    df = pd.read_csv(
        file_obj,
        header=0,
        sep=';',
        engine='python',
        usecols=[col_to_index("A"), col_to_index("AH"), col_to_index("AT")],
        skiprows=lambda i: i > 0 and (i - 1) % 120 != 0 
    )

    ts_idx = col_to_index("A")
    az_idx = col_to_index("AH")
    bd_idx = col_to_index("AT")


    df.iloc[:, ts_idx] = pd.to_datetime(df.iloc[:, ts_idx], dayfirst=True)
    

    df.iloc[:, az_idx] = df.iloc[:, az_idx].apply(fix_temperature)
    df.iloc[:, bd_idx] = df.iloc[:, bd_idx].apply(fix_temperature)
    

    df = df.iloc[:, [ts_idx, az_idx, bd_idx]]
    df = df.iloc[::300].copy() 
    return df
    

main_directory = r'\\nas-archivio\UTC-SHARE\Automazione\BESS\LOG IMPIANTI\2019 - ELECTRA CAPO VERDE\SCADA\2025\03'

sg_codes = [f'SG0{i}' for i in range(1, 3)]  
data_dict = {sg: [] for sg in sg_codes}

for day_folder in os.listdir(main_directory):
    daily_path = os.path.join(main_directory, day_folder)
    if os.path.isdir(daily_path):
       
        for sg in sg_codes:
            zip_pattern = os.path.join(daily_path, f'*_{sg}.zip')
            zip_files = glob.glob(zip_pattern)
            for zip_file in zip_files:
                print(f"  Processing ZIP file: {zip_file} for {sg}")
                try:
                    with zipfile.ZipFile(zip_file, 'r') as z:
                        for filename in z.namelist():
                            if filename.endswith('.csv'):
                                print("    Found CSV in ZIP:", filename)
                                with z.open(filename) as f:
                                    try:
                                        df = process_csv(f)
                                        data_dict[sg].append(df)
                                    except Exception as e:
                                        continue
                except Exception as e:
                    continue

x = str(main_directory)




months = {
    '01' : 'January',
    '02' : 'February',
    '03' : 'March',
    '04' : 'April',
    '05' : 'May',
    '06' : 'June',
    '07' : 'July',
    '08' : 'August',
    '09' : 'September',
    '10' : 'October',
    '11' : 'November',
    '12' : 'December'    
}

colors = [
    'rgba(31, 119, 180, 0.5)',    # Blue
    'rgba(44, 160, 44, 0.5)',     # Green
]

fig = go.Figure()

for i, sg in enumerate(sg_codes):
    if data_dict[sg]:
        combined_df = pd.concat(data_dict[sg], ignore_index=True)
        combined_df.columns = list(range(combined_df.shape[1]))
        combined_df.sort_values(by=0, inplace=True)
        
        combined_df.set_index(0, inplace=True)
        combined_df = combined_df.resample('1min').mean() 
        combined_df.reset_index(inplace=True)
        

        x_vals = combined_df.iloc[:, 0].values
        y1 = combined_df.iloc[:, 1].values 
        y2 = combined_df.iloc[:, 2].values 
        y_top = np.maximum(y1, y2)
        y_bottom = np.minimum(y1, y2)
        
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=y_top,
            mode='lines',
            line=dict(width=1, color='rgba(0,0,0,0)'),
            connectgaps=True,
            showlegend=False,
            name=f'{sg} Upper'
        ))
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=y_bottom,
            mode='lines',
            fill='tonexty',
            fillcolor=colors[i],
            line=dict(width=1, color='rgba(0,0,0,0)'),
            connectgaps=True,
            name=sg
        ))
       
    else:
        print(f"No data found for {sg}")


fig.update_layout(
    title={
        'text': f'Capo Verde - Storage Group Temperatures - {months[x[-2:]]} 202{x[-4]}',
        'x': 0.5,          
        'xanchor': 'center'
    },
    xaxis_title='Time',
    yaxis_title='Temperature (°C)',
    plot_bgcolor='white',       
    paper_bgcolor='white',     
    font=dict(
        family='Arial, sans-serif',
        size=18,
        color='#333'
    ),
    legend=dict(
        traceorder='reversed'
    ),
    margin=dict(l=60, r=60, t=60, b=60)
)



