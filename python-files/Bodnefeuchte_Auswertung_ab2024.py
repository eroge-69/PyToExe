import psycopg2
from psycopg2 import Error

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.colors as mcolors
import numpy as np
import math
from matplotlib.dates import DateFormatter, MonthLocator
from matplotlib.lines import Line2D
from datetime import datetime 
from datetime import timedelta
from glob import glob
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator, AutoLocator)
import matplotlib.dates as mdates
from scipy.stats import linregress
from scipy.optimize import curve_fit

# first thing, download the newest data from radar.
# see readme in the same folder

try:
    print("Brienz Niederschlagsmessungen")
    print("wait...")
    # Connect to an existing database
    connection = psycopg2.connect(user="webgis",
                                  password="webGIS!2009",
                                  host="chdcrgisdb1",
                                  port="5432",
                                  database="dbmess",
                                  options="-c search_path=gr_brienz,public")

    # Create a cursor to perform database operations
    cursor = connection.cursor()
    
    print("connecting...")
    cursor.execute("SELECT tb_mess.mess_dat AS dat1, tb_mess.mess_messwert, tb_messstellen.ms_name AS ms_name \
                    FROM tb_messstellen INNER JOIN tb_mess ON tb_messstellen.ms_id = tb_mess.mess_fk_ms \
                    WHERE ((tb_mess.mess_fk_param)=17065713 ) \
                    ORDER BY tb_mess.mess_dat DESC , tb_messstellen.ms_name;") 

    columns = [desc[0] for desc in cursor.description]
    ereignisse = pd.DataFrame(cursor.fetchall(), columns=columns)

    ms_name = 'RM01: Regenmesser'
    print(ms_name)
    
    # except (Exception, Error) as error:
#     print("Error while connecting to PostgreSQL:", error)
finally:
    if (connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")


## Apply to NS in Brienz
## IMPORT - Regendaten & preparation 
    x = ereignisse["dat1"][ereignisse["ms_name"]== ms_name]
    x = x[::-1]     # invert vector direction
    x_datetime = x.astype('datetime64[ns]')
    
    y = ereignisse["mess_messwert"][ereignisse["ms_name"]==ms_name]
    y = y[::-1]         # invert vecor direction
    y = y.astype('double')

    data_rain = pd.DataFrame({'Date': x, 'Values':y})
    data_rain.set_index('Date', inplace=True)
    ## Auswahln Zeitfenster
    # target_date = datetime(2022, 11, 1)
    # data_rain = data_rain[data_rain.index >= target_date]
    ## Tages-, Monatswerte und Cumulative generieren
    daily_values_rain = data_rain.resample('D').sum()  # You can use .mean(), .max(), etc.
    # daily_values_rain['cumul'] = daily_values_rain['Values'].cumsum()
    # monthly_values = data_rain.resample('ME').sum()  # You can use .mean(), .max(), etc.
    ## "Moving_sum" 
    daily_values_rain['movsum_7d'] = daily_values_rain['Values'].rolling(window=7).sum()     # shift(1) macht das rückgängig
    daily_values_rain['movsum_14d'] = daily_values_rain['Values'].rolling(window=14).sum()     # shift(1) macht das rückgängig

    plt.figure(figsize=(14, 6))
    plt.axhspan(0, 5, color='green', alpha=0.2, label='nicht gesättigt')
    plt.axhspan(40, 65, color='yellow', alpha=0.2, label='min. teilgesättigt')
    plt.axhspan(65, max(daily_values_rain['movsum_7d'].dropna()), color='red', alpha=0.2, label='gestättigt')
    plt.axvspan( pd.to_datetime('2024-11-01'),  pd.to_datetime('2025-03-31'), color='red', alpha=0.6, label='winter')
    plt.axvspan( pd.to_datetime('2023-11-01'),  pd.to_datetime('2024-03-31'), color='red', alpha=0.6, label='')
    plt.axvspan( pd.to_datetime('2022-11-01'),  pd.to_datetime('2023-03-31'), color='red', alpha=0.6, label='')
    plt.plot(daily_values_rain.index, daily_values_rain['movsum_7d'].values, label=f'7 Tage Summe', marker='', linestyle ='-', color='blue',markersize=5)
    plt.title(f'Einschätzung Bodensättigung auf Basis des Niederschlags (Summe 7 Tage)')
    plt.xlabel('Datum')
    plt.ylabel('Niederschlag [mm]')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    # plt.xlim(pd.to_datetime('2023-04-01'), pd.to_datetime('2023-07-01'))
    # plt.savefig(f'Ergebnisse/Bodenfeuchte_BRIENZ_2023_Insel_7T.png')
    plt.savefig(f'Ergebnisse/Bodenfeuchte_BRIENZ_7_Tage.png')
    plt.show()

    plt.figure(figsize=(14, 6))
    plt.axhspan(0, 15, color='green', alpha=0.2, label='nicht gesättigt')
    plt.axhspan(65, 100, color='yellow', alpha=0.2, label='min. teilgesättigt')
    plt.axhspan(100, max(daily_values_rain['movsum_14d'].dropna()), color='red', alpha=0.2, label='gestättigt')
    plt.axvspan( pd.to_datetime('2024-11-01'),  pd.to_datetime('2025-03-31'), color='red', alpha=0.6, label='winter')
    plt.axvspan( pd.to_datetime('2023-11-01'),  pd.to_datetime('2024-03-31'), color='red', alpha=0.6, label='')
    plt.axvspan( pd.to_datetime('2022-11-01'),  pd.to_datetime('2023-03-31'), color='red', alpha=0.6, label='')
    plt.plot(daily_values_rain.index, daily_values_rain['movsum_14d'].values, label=f'14 Tage Summe', marker='', linestyle ='-', color='blue',markersize=5)
    plt.title(f'Einschätzung Bodensättigung auf Basis des Niederschlags (Summe 14 Tage)')
    plt.xlabel('Datum')
    plt.ylabel('Niederschlag [mm]')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    # plt.xlim(pd.to_datetime('2023-04-01'), pd.to_datetime('2023-07-01'))
    # plt.savefig(f'Ergebnisse/Bodenfeuchte_BRIENZ_2023_Insel_14T.png')
    plt.savefig(f'Ergebnisse/Bodenfeuchte_BRIENZ_14_Tage.png')
    plt.show()

        
## IMPORT - RADAR data (https://app.geoprevent.com/stations/382/export)
    radar = pd.read_csv('2025-05-13.csv')
    x_rad = pd.to_datetime(radar['Timestamp'])  # Convert 'Date' column to datetime
    # x_rad = x_rad.astype('datetime64[ns]')
    y_rad = radar['Velocity GP-AIM Point 11 (16914)']  # 'Value' column to plot
    y_rad = y_rad.astype('double')
    x_rad_filter = x_rad[x_rad >= target_date]
    y_rad_filter = y_rad[x_rad >= target_date]

    data_radar = pd.DataFrame({'Date': x_rad_filter, 'Values':y_rad_filter})
    data_radar.set_index('Date', inplace=True)
    daily_values_radar = data_radar.resample('D').mean()  # You can use .mean(), .max(), etc.
    daily_values_radar['movmean_3d'] = daily_values_radar['Values'].rolling(window=3).mean()

## IMPORT - Bodenfeuchte data (https://www.bodenmessnetz.ch/messwerte/datenabfrage 
    # boden = pd.read_csv('bodemessnetz_2023_Andeer.csv',sep=';', header=1, skiprows=12)
    # Station = 'Andeer'
    # boden = pd.read_csv('bodemessnetz_2022_Cazis.csv',sep=';', header=1, skiprows=10)
    # Station = 'Cazis'
    boden = pd.read_csv('bodemessnetz_2023_Disentis.csv',sep=';', header=1, skiprows=10)
    Station = 'Disentis'

    x_bod = pd.to_datetime(boden.iloc[:,0])  # Convert 'Date' column to datetime
    bf = boden.iloc[:,3]  # Saugspannung in 35 cm Tiefe
    ns_bod = boden.iloc[:,1]  # Niederschlag
    y_rad = y_rad.astype('double')
    # x_rad_filter = x_rad[x_rad >= target_date]        # FILTER
    # y_rad_filter = y_rad[x_rad >= target_date]

    data_bod = pd.DataFrame({'Date': x_bod, 'bf':bf, 'ns':ns_bod})
    
    data_bod['Month'] = data_bod['Date'].dt.month
    # VIEW DATA
    # data_bod.plot(x='Date', y='bf', kind='line', title='Values over Time')
    # data_bod.plot(x='Date', y='ns', kind='line', title='Values over Time')
    # plt.show()
    # data_bod.set_index('Date', inplace=True)      # INDEX
    plt.plot(ns_bod, bf, marker='o', linestyle='')

    plt.close('all')
    window_size = [3, 7, 14, 21]

    summer_data = data_bod[data_bod['Month'].isin([4,5,6,7,8,9,10])].dropna() 
    winter_data = data_bod[data_bod['Month'].isin([11,12,1,2,3])].dropna() 

    # Define exponential decay function
    def exp_decay(x, a, b):
        return a * np.exp(-b * x)

    for w in window_size:
        plt.figure()
        winter_data['ns_sum_w'] = winter_data['ns'].rolling(window=w).sum()
        winter_data['bf_pre'] = winter_data['bf'].shift(1).rolling(window=w).sum()
        winter_data.dropna(inplace=True)    # removes NaN
        x = winter_data['ns_sum_w'].values
        y = winter_data['bf'].values
        c = winter_data['bf_pre'].values
        plt.plot(x, y, label=f'Winter', marker='o', linestyle ='', color='blue',markersize=2)
        plt.title(f'Bodenfeuchte VS vergangene Niederschlag (Summe {w} Tage)')
        plt.xlabel('Niederschlag [mm]')
        plt.ylabel('Saugspannung in 35 cm Tiefe [cbar]')
        plt.grid(True)
        plt.yscale('log')
        plt.ylim([1,100])
        plt.xlim([-5,150])
        plt.axhspan(0, 6, color='red', alpha=0.2, label='nass')
        plt.axhspan(6, 10, color='orange', alpha=0.2, label='sehr feucht')
        plt.axhspan(10, 20, color='yellow', alpha=0.2, label='feucht')
        plt.axhspan(20, 80, color='green', alpha=0.2, label='trocken')
        x_fit = np.linspace(min(x), max(x), 100)
        # slope, intercept, r_value, p_value, std_err = linregress(x, y)
        # print(f"R²: {r_value**2:.3f}")  # r_value is correlation coefficient, square it to get R²
        # y_fit = slope * x_fit + intercept
        # plt.plot(x_fit, y_fit, color='red', label=f'Fit line: y={slope:.2f}x + {intercept:.2f}')

        # params, _ = curve_fit(exp_decay, x, y)
        # a, b = params
        # y_fit = exp_decay(x_fit, a, b)
        # plt.plot(x_fit, y_fit, color='red', label=f'Fit: y = {a:.2f}·e^(-{b:.2f}x)')
        plt.legend()
        # plt.show()
        plt.savefig(f'Ergebnisse/Bodenfeuchte_{Station}_Winter_{w}_Tage.png')
        
        plt.figure()
        plt.scatter(x, y, c*4, c, cmap='viridis', edgecolor='k')
        # plt.show()


        plt.figure()
        ns_sum_s = summer_data['ns'].rolling(window=w).sum()
        plt.plot(ns_sum_s, summer_data['bf'], label=f'Sommer', marker='o', linestyle ='', color='red',markersize=2)
        plt.title(f'Bodenfeuchte VS vergangene Niederschlag (Summe {w} Tage)')
        plt.xlabel('Niederschlag [mm]')
        plt.ylabel('Saugspannung in 35 cm Tiefe [cbar]')
        plt.grid(True)
        plt.yscale('log')
        plt.ylim([1,100])
        plt.xlim([-5,150])
        plt.axhspan(0, 6, color='red', alpha=0.2, label='nass')
        plt.axhspan(6, 10, color='orange', alpha=0.2, label='sehr feucht')
        plt.axhspan(10, 20, color='yellow', alpha=0.2, label='feucht')
        plt.axhspan(20, 80, color='green', alpha=0.2, label='trocken')
        plt.legend()
        plt.savefig(f'Ergebnisse/Bodenfeuchte_{Station}_Summer_{w}_Tage.png')

    # plt.show()

    plt.close('all')
    for w in window_size:
        plt.figure()
        ns_sum_w = winter_data['ns'].rolling(window=w).sum()
        plt.plot(ns_sum_w, winter_data['bf'], label=f'winter', marker='.', linestyle ='', color='blue',markersize=5)
        ns_sum_s = summer_data['ns'].rolling(window=w).sum()
        plt.plot(ns_sum_s, summer_data['bf'], label=f'Summer', marker='.', linestyle ='', color='red')
        plt.title(f'Bodenfeuchte VS vergangene Niederschlag (Summe {w} Tage)')
        plt.xlabel('Niederschlag [mm]')
        plt.ylabel('Saugspannung in 35 cm Tiefe [cbar]')
        plt.grid(True)
        plt.xlim([-5,150])
        plt.yscale('log')
        plt.ylim([1,100])
        plt.axhspan(0, 6, color='red', alpha=0.2, label='nass')
        plt.axhspan(6, 10, color='orange', alpha=0.2, label='sehr feucht')
        plt.axhspan(10, 20, color='yellow', alpha=0.2, label='feucht')
        plt.axhspan(20, 80, color='green', alpha=0.2, label='trocken')
        plt.legend()
        plt.savefig(f'Ergebnisse/Bodenfeuchte_{Station}_{w}_Tage.png')
        # plt.show()


print("this is the end")   
