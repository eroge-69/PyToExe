import numpy as np
import pandas as pd
import time
from datetime import date, timedelta,datetime
pd.set_option('display.max_columns',100)
pd.set_option('display.width',1000)
import statsmodels.tsa.seasonal as sts
from statsmodels.tsa.seasonal import STL
import statsmodels.api as sm
from statsmodels.tsa.forecasting.stl import STLForecast
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.graphics.tsaplots import plot_pacf
import os
from prophet.make_holidays import make_holidays_df
import warnings
warnings.filterwarnings('ignore')

start_run = datetime.now()

today = pd.Timestamp.now()
today_str = today.strftime('%Y-%m-%d')
today_str = pd.Timestamp(today_str)
today = pd.Timestamp.now()
today_str = today.strftime('%Y-%m-%d')
today_str = pd.Timestamp(today_str)

cek = np.datetime64('today','D')
cek = pd.Timestamp(cek).strftime('%Y-%m-%d')

cek2 = np.datetime64(cek)
low_bar = cek2 - np.timedelta64(548, 'D')
year_prev = cek2 - np.timedelta64(365, 'D')
days_back = 578
year_prev = year_prev.astype('datetime64[Y]').astype('str').astype('int64')
tomorrow = today_str + np.timedelta64(1, 'D')

#Read historical withdrawal
colnames=['atm_id','date','denom_1','deposits_1','withdrawals_1','denom_2','deposits_2','withdrawals_2','empty1','empty2','empty3']
data_list = []
folder_path = 'data'
for i in range (1,days_back):
    date = today_str - timedelta(days=i)
    # print(date)
    filename = 'REPORT_CASHINOUT_'+date.strftime('%Y%m%d')+'.TXT'
    filepath = os.path.join(folder_path, filename)
    # print(filepath)
    if os.path.isfile(filepath):
        try:
            df = pd.read_csv(filepath,sep='|',names=colnames)
            data_list.append(df)
        except Exception as e:
            print(f"error reading {filename}:{e}")
if data_list:
    combined_df = pd.concat(data_list, ignore_index=True)
    print("loaded data shape:", combined_df.shape)
else:
    print("no files found in the past", days_back,"days.")

combined_df['date'] = combined_df['date'].astype(str)
combined_df['date'] = pd.to_datetime(combined_df['date'], format='%Y%m%d.0', errors='coerce')
df_cek = combined_df.copy()
df_cek['date_mo'] = df_cek['date']
df_cek['date_mo'] = pd.to_datetime(df_cek['date_mo'], format='%Y%m', errors='coerce')
df_cek['date_mo'] = df_cek['date_mo'].dt.strftime("%Y-%m")
# df['date_mo'] = pd.to_datetime(df['date_mo'],errors='coerce')

df_cek['atm_id'] = df_cek['atm_id'].str.strip()
df2 = df_cek[~df_cek['date'].isna()]
df2.shape

cols = ['deposits_1','deposits_2','withdrawals_1','withdrawals_2']
df2[cols] = df2[cols].astype(str)
# df2[cols] = pd.to_numeric(df2[cols].str.extract(r'^(\d+)'))
# df2[cols] = df2[cols].replace('[^\d\.]','', regex=True).astype(float)
df2[cols] = df2[cols].replace(r'[}]+', '0', regex=True)
df2 = df2[~df2['atm_id'].isna()] #biasanya yg amount withdrawals/deposit aneh, atm_id == nan
df2[cols]=df2[cols].astype(float)

df2['sum_deposits'] = df2['deposits_1'] + df2['deposits_2']
df2['sum_withdrawals'] = df2['withdrawals_1'] + df2['withdrawals_2']

df2 = df2.sort_values(by = ['atm_id','date'], ascending=True)
df2.reset_index(0,drop = True, inplace = True)

df2['periode'] = pd.to_datetime(df2['date'], dayfirst=True)
df2.sort_values('periode', inplace=True)
df2['periode'] = df2['periode'].astype(str)

# selected = df2[(df2['date'] >= low_bar) & (df2['date'] <= today)] # ini tdk perlu karena waktu read udh di cek mundur sekian hari
selected = df2.copy()
selected['withdrawals_1'] = selected['withdrawals_1'].astype(int)
selected = selected[selected['withdrawals_1']!=0]

selected['norm_with50'] = selected['withdrawals_1']/50000
selected['norm_with50'] = np.round(selected['norm_with50'],2)
selected = selected[['periode', 'norm_with50','atm_id']].rename(columns={'periode': 'dtime'})

selected['dtime'] = pd.to_datetime(selected['dtime'], dayfirst=True)

selected_prep_test = selected.copy()
selected_prep_test = selected_prep_test.sort_values(['dtime','atm_id'])

# historical exog feature
holiday = make_holidays_df(
    year_list=[year_prev + i for i in range(3)], country='ID')

holiday = holiday.sort_values(by='ds')
eid = holiday[holiday['holiday'] == 'Eid al-Fitr']
selected_prep_test = selected_prep_test.merge(holiday, right_on='ds', left_on='dtime', how='left')
selected_prep_test['is_eid_prop']=selected_prep_test.dtime.isin(eid.ds).astype(int).apply(lambda x: 1 if x == 1 else 0)

days_before = 2
flagged_before = set()
for holidaybef in selected_prep_test['ds']:
    for i in range(days_before + 1):
        flagged_before.add(holidaybef - timedelta(days=i))

flagged_before_series = pd.Series(list(flagged_before))
selected_prep_test['before_holiday'] = np.where(selected_prep_test['dtime'].isin(flagged_before_series), 1, 0)

days_after = 2
flagged_after = set()

for holidayaft in selected_prep_test['ds']:
    for i in range(days_after + 1): 
        flagged_after.add(holidayaft + timedelta(days=i))

flagged_after_series = pd.Series(list(flagged_after))
selected_prep_test['after_holiday'] = np.where(selected_prep_test['dtime'].isin(flagged_after_series), 1, 0)

selected_prep_test['is_holiday_prop'] = selected_prep_test.dtime.isin(holiday.ds).astype(int).apply(lambda x: 1 if x == 1 else 0)
selected_prep_test['holiday_flag'] = selected_prep_test['is_holiday_prop'] | selected_prep_test['before_holiday'] | selected_prep_test['after_holiday']

days_before_thr = 14
flagged_before_thr = set()
for holidaybef in eid['ds']:
    for i in range(days_before_thr + 1):
        flagged_before_thr.add(holidaybef - timedelta(days=i))

flagged_beforethr_series = pd.Series(list(flagged_before_thr))
selected_prep_test['before_thr'] = np.where(selected_prep_test['dtime'].isin(flagged_beforethr_series), 1, 0)

days_after_thr = 10
flagged_after_thr = set()
for holidayaftr in eid['ds']:
    for i in range(days_after_thr + 1):
        flagged_after_thr.add(holidayaftr + timedelta(days=i))

flagged_afterthr_series = pd.Series(list(flagged_after_thr))
selected_prep_test['after_thr'] = np.where(selected_prep_test['dtime'].isin(flagged_afterthr_series), 1, 0)

selected_prep_test['thr_flag'] = selected_prep_test['before_thr'] | selected_prep_test['after_thr']
selected_prep_test['payday'] = selected_prep_test['dtime'].apply(lambda x: 1 if (x.day == 25)or(x.day == 1) else 0)

payday_window = 1 
selected_prep_test['payday'] = np.where(
    ((selected_prep_test['dtime'].dt.day >= 25 - payday_window) & (selected_prep_test['dtime'].dt.day <= 25 + payday_window))|((selected_prep_test['dtime'].dt.day >= 1 - payday_window) & (selected_prep_test['dtime'].dt.day <= 1 + payday_window)),
    1,
    selected_prep_test['payday'])

selected_prep_test['weekend_flag'] = selected_prep_test['dtime'].dt.weekday.isin([5, 6]).astype(int)

test_day_filter = selected_prep_test.copy()
test_filtered = test_day_filter.copy()

test_filtered = test_filtered.sort_values(['dtime','atm_id'])
test_filtered = test_filtered[test_filtered['norm_with50']!=0]

test_filtered_cp = test_filtered.copy()
test_filtered_cp = test_filtered_cp.value_counts(['atm_id']).reset_index(name='count')
test_filtered_cp = test_filtered_cp[test_filtered_cp['count']>14]
test_filtered = test_filtered[test_filtered['atm_id'].isin(test_filtered_cp['atm_id'])]

selected_prep_test2 = test_filtered.copy()

# select data for prediction
base_df = selected_prep_test2.copy()
base_df.rename(columns = {'norm_with50':'amount_withdrawal'}, inplace = True)
base_df = base_df[['dtime','atm_id','amount_withdrawal','holiday_flag','thr_flag','payday','weekend_flag']]

# read parameter p,q,d each ATM
%%time
param_lib = pd.read_excel("model/ATM Cash Optimization_Result_model_result_allatm_removeoutlier_50_dec24_full_allday.xlsx")
# param_lib_backup = param_lib.copy()
param_lib = param_lib.drop_duplicates(subset = 'atm_id')

def extract_p_d_q(row):
    try:
        values = row['best_order'].strip('()').split(',')
        return pd.Series({'p': int(values[0]), 'd': int(values[1]), 'q': int(values[2])})
    except:
        return pd.Series({'p': None, 'd': None, 'q': None})

param_lib[['p', 'd', 'q']] = param_lib.apply(extract_p_d_q, axis=1)
# param_lib.head()

# exog feature for prediction
yest = today_str - timedelta(days=1)

start_date = yest
date_range = pd.date_range(start = start_date, periods=8)
predict_df = pd.DataFrame({'dtime': date_range})
predict_df['dtime'] = pd.to_datetime(predict_df['dtime'])
predict_df = predict_df.sort_values(by='dtime')

holiday = holiday.sort_values(by='ds')
eid = holiday[holiday['holiday']=='Eid al-Fitr']

predict_df = predict_df.merge(holiday, right_on='ds', left_on='dtime', how='left')

predict_df['is_eid_prop']=predict_df.dtime.isin(eid.ds).astype(int).apply(lambda x: 1 if x == 1 else 0)

days_before = 2
flagged_before = set()
for holidaybef in predict_df['ds']:
    for i in range(days_before + 1):
        flagged_before.add(holidaybef - timedelta(days=i))

flagged_before_series = pd.Series(list(flagged_before))
predict_df['before_holiday'] = np.where(predict_df['dtime'].isin(flagged_before_series), 1, 0)

days_after = 2
flagged_after = set()

for holidayaft in predict_df['ds']:
    for i in range(days_after + 1): 
        flagged_after.add(holidayaft + timedelta(days=i))

flagged_after_series = pd.Series(list(flagged_after))
predict_df['after_holiday'] = np.where(predict_df['dtime'].isin(flagged_after_series), 1, 0)

predict_df['is_holiday_prop'] = predict_df.dtime.isin(holiday.ds).astype(int).apply(lambda x: 1 if x == 1 else 0)
predict_df['holiday_flag'] = predict_df['is_holiday_prop'] | predict_df['before_holiday'] | predict_df['after_holiday']

days_before_thr = 14
flagged_before_thr = set()
for holidaybef in eid['ds']:
    for i in range(days_before_thr + 1):
        flagged_before_thr.add(holidaybef - timedelta(days=i))

flagged_beforethr_series = pd.Series(list(flagged_before_thr))
predict_df['before_thr'] = np.where(predict_df['dtime'].isin(flagged_beforethr_series), 1, 0)

days_after_thr = 10
flagged_after_thr = set()
for holidayaftr in eid['ds']:
    for i in range(days_after_thr + 1):
        flagged_after_thr.add(holidayaftr + timedelta(days=i))

flagged_afterthr_series = pd.Series(list(flagged_after_thr))
predict_df['after_thr'] = np.where(predict_df['dtime'].isin(flagged_afterthr_series), 1, 0)

predict_df['thr_flag'] = predict_df['before_thr'] | predict_df['after_thr']

predict_df['payday'] = predict_df['dtime'].apply(lambda x: 1 if (x.day == 25)or(x.day == 1) else 0)

payday_window = 1 
predict_df['payday'] = np.where(
    ((predict_df['dtime'].dt.day >= 25 - payday_window) & (predict_df['dtime'].dt.day <= 25 + payday_window))|((predict_df['dtime'].dt.day >= 1 - payday_window) & (predict_df['dtime'].dt.day <= 1 + payday_window)),
    1,
    predict_df['payday'])

predict_df['weekend_flag'] = predict_df['dtime'].dt.weekday.isin([5, 6]).astype(int)
predict_df.rename(columns = {'norm_with50':'amount_withdrawal'}, inplace = True)

future_exog = predict_df[['dtime','holiday_flag','thr_flag','payday','weekend_flag']]
future_exog = future_exog.set_index('dtime')
future_exog.index.name = None

# predict withdraw: fit into model
yest_model = today_str - timedelta(days=2)

%%time
forecast_results = []
base_df['dtime'] = pd.to_datetime(base_df['dtime'])
base_df = base_df.sort_values(['atm_id', 'dtime'])
base_df = base_df.dropna()

for atm in base_df['atm_id'].unique():
    print(atm)
    df_atm = base_df[base_df['atm_id'] == atm].copy()
    df_atm.set_index('dtime', inplace=True)
    y = df_atm['amount_withdrawal']
    # print(type(y))
    # print(y.isna().sum())
    exog = df_atm[['holiday_flag', 'thr_flag', 'payday', 'weekend_flag']]
    # print(type(exog))
    # print(exog.isna().sum())
    # exog = exog.loc[:, exog.nunique()>1]
    
    row = param_lib[param_lib['atm_id'] == atm]
    if row.empty:
        continue
    order = tuple(row[['p', 'd', 'q']].values[0])
    try:
        model = sm.tsa.ARIMA(
           y,
           exog=exog,
           order=order,
           enforce_stationarity=True,
           enforce_invertibility=True
       )
        results = model.fit()
        # print(results.summary())
        
        # last_date = base_df.dtime.max()
        last_date = yest_model
        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=8, freq='D')

        forecast = results.forecast(steps=8, exog=future_exog, typ='levels')
        #print(forecast)
        df_forecast = pd.DataFrame({
           'atm_id': atm,
           'date': future_dates,
           'predicted_amount_withdrawal': forecast
       })
        forecast_results.append(df_forecast)
    except Exception as e:
        print("model failed load, need more data:", e)
    
final_forecast_df = pd.concat(forecast_results).reset_index(drop=True)
# final_forecast_df


# cashpos
colnames_cash=['atm_id','date','denom_1','closing_balance_1','denom_2','closing_balance_2','empty1','empty2']
folder = 'data'
# file_cash = f'REPORT_CASHPOS_{yesterday}.TXT'
# filepath_cash = os.path.join(folder, file_cash)
# if os.path.isfile(filepath_cash):
#         try:
#             cashpo = pd.read_csv(filepath_cash,sep='|',names=colnames_cash)
#         except Exception as e:
#             print(f"no file found {file_cash}:{e}")
cash_list = []
for i in range (1,4):
# for i in range (0,3):
    date = (today - timedelta(days=i)).strftime('%Y%m%d')
    file_cash = 'REPORT_CASHPOS_'+date+'.TXT'
    filepath_cash = os.path.join(folder, file_cash)
    if os.path.isfile(filepath_cash):
        print(f"read file:{file_cash}")
        df_cash = pd.read_csv(filepath_cash,sep='|',names=colnames_cash)
        cash_list.append(df_cash)
    else:
        print(f"missing file: {file_cash}")
if cash_list:
    cashpo = pd.concat(cash_list, ignore_index=True)
    print("loaded data shape:", cashpo.shape)
else:
    raise FileNotFoundError("no files found")

cashpo['date'] = cashpo['date'].astype(str)
cashpo['date'] = pd.to_datetime(cashpo['date'], format='%Y%m%d.0', errors='coerce')
cashpo.atm_id = cashpo.atm_id.astype(str)
cashpo.atm_id = cashpo.atm_id.str.strip()

cashpo['date'] = pd.to_datetime(cashpo['date'], errors='coerce')
cashpo['periode_cashpo'] = cashpo['date'] + pd.Timedelta(days=1) #untuk hari ini, dari cashposition terakhir kemarin
#cashpo.head(2)

cashpo = cashpo[['atm_id','periode_cashpo','closing_balance_1','closing_balance_2']]
cashpo.rename(columns={'closing_balance_1':'open_balance_50','closing_balance_2':'open_balance_100'}, inplace = True)
#cashpo.head()

cols = ['open_balance_50','open_balance_100']
cashpo[cols]=cashpo[cols].astype(str)
cashpo[cols] = cashpo[cols].replace(r'[}]+', '0', regex=True)
cashpo = cashpo[~cashpo['atm_id'].isna()] #biasanya yg amount withdrawals/deposit aneh, atm_id == nan
cashpo[cols]=cashpo[cols].astype(float)

#safety stock
folder = 'data'
file_ss = f'safety_stock.xlsx'
filepath_ss = os.path.join(folder, file_ss)
if os.path.isfile(filepath_ss):
        try:
            ss_raw = pd.read_excel(filepath_ss)
        except Exception as e:
            print(f"no file found {file_ss}:{e}")
ss_raw.rename(columns={'Cashpoint ID':'atm_id',' Safety Stock ':'safety_stock'}, inplace = True)
# ss_raw.head(2)

# amount replenish
replenish_dmaa = final_forecast_df.copy()
replenish_dmaa['dmaa_predict_withdraw'] = replenish_dmaa['predicted_amount_withdrawal'] * 50000
replenish_dmaa['periode_pred'] = pd.to_datetime(replenish_dmaa['date'], dayfirst=True)
#replenish_dmaa.head(10)

with_real_dmaa = pd.merge(replenish_dmaa[['atm_id','periode_pred','dmaa_predict_withdraw']], cashpo, left_on=['atm_id', 'periode_pred'], right_on=['atm_id','periode_cashpo'], how = 'left')
#print(with_real_dmaa.shape)

with_real_dmaa = pd.merge(with_real_dmaa[['atm_id','periode_pred','periode_cashpo','dmaa_predict_withdraw','open_balance_50']], ss_raw[['atm_id','safety_stock']], on = 'atm_id', how = 'left')
#print(with_real_dmaa.shape)
#with_real_dmaa.head(2)

def flagg (x,y,a):
    if (pd.isna(x[y])) :
        return np.nan
    else:
        return x[a]
with_real_dmaa['remaining_balance'] = with_real_dmaa.apply(flagg, y='safety_stock', a='open_balance_50', axis=1)


for i in range(1, len(with_real_dmaa)):
    if with_real_dmaa.loc[i, "atm_id"] == with_real_dmaa.loc[i - 1, "atm_id"]:
        with_real_dmaa.loc[i, "open_balance_act"] = with_real_dmaa.loc[i, "open_balance_50"] #balance_act: balance sebelumnya
        # fill open_balance dari saldo sebelumnya jika NaN
        with_real_dmaa.loc[i, "open_balance_50"] = with_real_dmaa.loc[i - 1, "remaining_balance"]
        
        with_real_dmaa.loc[i, "remaining_balance"] = with_real_dmaa.loc[i - 1, "remaining_balance"] - with_real_dmaa.loc[i, "dmaa_predict_withdraw"]
        # Jika saldo kurang dari safety stock, do replenish
        if with_real_dmaa.loc[i, "remaining_balance"] < with_real_dmaa.loc[i, "safety_stock"]:
            with_real_dmaa.loc[i, "rep_tag_dmaa"] = '1'
            with_real_dmaa.loc[i, "remaining_balance"] = 280000000  # Reset saldo*

with_real_dmaa["month"] = with_real_dmaa["periode_pred"].dt.to_period("M")
with_real_dmaa["amt_replenish_dmaa"] = 0
for atm_id in with_real_dmaa["atm_id"].unique():
# for atm_id in atm_cek["atm_id"].unique():
    # for month in with_real_dmaa["month"].unique():
    mask = (with_real_dmaa["atm_id"] == atm_id)
    cum_withdrawal = 0

    for idx in with_real_dmaa[mask].index:
        # print(atm_cek.loc[idx, "dmaa_predict_withdraw"])
        cum_withdrawal += with_real_dmaa.loc[idx, "dmaa_predict_withdraw"]
        # cum_withdrawal = cum_withdrawal + with_real_dmaa.loc[idx, "dmaa_predict_withdraw"]
        # cum_withdrawal = cum_withdrawal+(cum_withdrawal*0.2)
        if with_real_dmaa.loc[idx, "rep_tag_dmaa"] == '1':
            # print(atm_cek.loc[idx, "dmaa_predict_withdraw"])
            cum_withdrawal += with_real_dmaa.loc[idx, "dmaa_predict_withdraw"]
            # print('cumifif',cum_withdrawal)
            with_real_dmaa.loc[idx, "amt_replenish_dmaa"] = cum_withdrawal*1.2
            # print(with_real_dmaa.loc[idx, "amt_replenish_dmaa"])
            cum_withdrawal = 0
			
df_prep = with_real_dmaa[(with_real_dmaa['periode_pred']==today)&(with_real_dmaa['amt_replenish_dmaa']!=0)]
#df_prep.shape

df_prep['amt_replenish_dmaa'] = df_prep['amt_replenish_dmaa'].astype(int)
df_prep['amt_replenish_suggest'] = round(df_prep['amt_replenish_suggest']/5000000)*5000000
def cek_max(x):
    if x >=400000000:
        return 400000000
    elif x <100000000:
        return 100000000
    else:
        return x
df_prep['amt_replenish_suggest_new'] = df_prep['amt_replenish_suggest'].apply(cek_max)
df_sent = df_prep[['atm_id','periode_pred','amt_replenish_suggest_new']]
df_sent.to_excel(f'output/Order_{today_str}.xlsx',index=False)

end_run = datetime.now()
run_time = end_run - start_run
seconds = run_time.seconds
hours, seconds =  seconds // 3600, seconds % 3600
minutes, seconds = seconds // 60, seconds % 60
print(f"Run time : {hours} hour(s) {minutes} minute(s) {seconds} second(s)")
