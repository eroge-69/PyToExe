#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np


# In[2]:


movehistory=pd.read_excel(r'T:\DataReporting\begüm\CraneDelayOptimization\Move History.xlsx',header=0)


# In[3]:


movehistory['QC?']= np.where(movehistory['Move Kind'] == 0, "",
    np.where(movehistory['Move Kind'] == "Load", movehistory['Put CHE Name'],
    np.where(movehistory['Move Kind'] == "Discharge", movehistory['Fetch CHE Name'],
    np.where(movehistory['Move Kind'] == "Delivery", "Gate",
    np.where(movehistory['Move Kind'] == "Receival", "Gate",
    np.where(movehistory['Move Kind'].str.startswith("Y"), "Yard", ""))))))


# In[4]:


movehistory['Move+Truck'] = (movehistory['Move Kind'].fillna('0').astype(str).str[0] + movehistory['Carry CHE Name'].fillna('0').astype(str).str[-4:])


# In[5]:


movehistory['RT'] = np.where(movehistory['Move Kind'].str.lower().isin(['load', 'delivery', 'yard move']), movehistory['Fetch CHE Name'], movehistory['Put CHE Name'])


# In[6]:


movehistory['Gemisaha'] = np.where(movehistory['Move Kind'].isin(['Load', 'Discharge']), '1', '')


# In[7]:


movehistory['Gemiyeçalışanlar'] = np.where(movehistory['Move Kind'].str[:2].isin(['Lo', 'Di']), movehistory['Carry CHE Name'], '')


# In[8]:


movehistory['fetchay'] = movehistory['Time of Fetch'].astype(str).str[3:6]


# In[9]:


movehistory['Date Fetch'] = (movehistory['Time of Fetch'].astype(str).str[7:9] + "-" + movehistory['Time of Fetch'].astype(str).str[3:6])


# In[10]:


movehistory['Time Fetch'] = movehistory['Time of Fetch'].astype(str).str[-4:]


# In[11]:


movehistory['q'] = (movehistory['Time Fetch'].astype(str).str[0:2] + ":" + movehistory['Time Fetch'].astype(str).str[2:4])


# In[12]:


movehistory = movehistory.replace('nan',np.nan)


# In[13]:


movehistory = movehistory.replace('na:n',np.nan)


# In[14]:


movehistory = movehistory.fillna(0)


# In[15]:


movehistory['x'] = movehistory['Time Fetch'].astype('int')


# In[16]:


def shift(x):
    if 0 < x < 800:
        return "00-08"
    elif 799 < x < 1600:
        return "08-16"
    elif 1599 < x < 2400:
        return "16-00"
    return ""


# In[17]:


movehistory['fetch zamanı'] = (
    movehistory['Date Fetch'].astype(str) + " " +
    movehistory['x'].apply(shift)
)


# In[18]:


movehistory['Date Comp'] = (movehistory['Time Completed'].astype(str).str[7:9] + "-" + movehistory['Time Completed'].astype(str).str[3:6])


# In[19]:


movehistory['Time Comp'] = movehistory['Time Completed'].astype(str).str[-4:]


# In[20]:


movehistory['w'] = (movehistory['Time Comp'].astype(str).str[0:2] + ":" + movehistory['Time Comp'].astype(str).str[2:4])


# In[21]:


movehistory = movehistory.replace('nan',np.nan)
movehistory = movehistory.replace('na:n',np.nan)
movehistory = movehistory.fillna(0)


# In[22]:


movehistory['y'] = movehistory['Time Comp'].astype('int')


# In[23]:


def shift2(x):
    if 0 < x < 800:
        return "00-08"
    elif 799 < x < 1600:
        return "08-16"
    elif 1599 < x < 2400:
        return "00-08"
    return ""


# In[24]:


movehistory['bitiş zamanı'] = (
    movehistory['Date Comp'].astype(str) + " " +
    movehistory['y'].apply(shift2)
)


# In[25]:


movehistory['sonuc zaman'] = np.where(
    movehistory['Move Kind'] == "Discharge",
    movehistory['fetch zamanı'],
    movehistory['bitiş zamanı']
)


# In[26]:


movehistory['birleştirsaat'] = np.where(
    movehistory['Move Kind'] == "Discharge",
    movehistory['q'],
    movehistory['w']
)


# In[27]:


movehistory['birleştirsaat'] = pd.to_datetime(movehistory['birleştirsaat'], format='%H:%M')


# In[28]:


hours = movehistory['birleştirsaat'].dt.hour


# In[29]:


movehistory['saat dilimi'] = hours.astype(str).str.zfill(2) + "-" + ((hours + 1) % 24).astype(str).str.zfill(2)


# In[30]:


def timelabel(t):
    if pd.isnull(t):
        return ""
    hour = t.hour
    if 0 <= hour < 8:
        return "00-08"
    elif 8 <= hour < 16:
        return "08-16"
    elif 16 <= hour <= 23:
        return "16-00"
    return ""


# In[31]:


movehistory['Shift'] = movehistory['birleştirsaat'].apply(timelabel)


# In[32]:


movehistory['move+qc'] = movehistory['QC?'].astype(str) + movehistory['Move Kind'].astype(str)


# In[33]:


movehistory['MCrn'] = (
    movehistory['Move Kind'].astype(str).str[0] +
    movehistory['QC?'].astype(str).str[-3:]
)


# In[34]:


month_map = {
    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05",
    "Jun": "06", "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10",
    "Nov": "11", "Dec": "12"
}


# In[35]:


movehistory['Tof'] = (
    movehistory['Time of Fetch'].astype(str).str[7:9] + "/" +
    movehistory['fetchay'].map(month_map).fillna("") + "/20" +
    movehistory['Time of Fetch'].astype(str).str[:2] + " " +
    movehistory['q'].astype(str).str[:5]
)


# In[36]:


movehistory['gemi saha hareket'] = (
    movehistory['Gemisaha'].astype(str) +
    movehistory['Move Kind'].astype(str)
)


# In[37]:


movehistory['ay'] = np.where(
    movehistory['Move Kind'] == "Discharge",
    movehistory['Time of Fetch'].astype(str).str[3:6],
    movehistory['Date Comp'].astype(str).str[3:6]
)


# In[38]:


movehistory['ayrakam'] = movehistory['ay'].astype(str).map(lambda x: month_map.get(x, ""))


# In[39]:


movehistory['SSTL'] = (
    movehistory['sonuc zaman'].astype(str).str[:2] + "/" +
    movehistory['ayrakam'].astype(str).str[:2] + "/20" +
    movehistory['Time Completed'].astype(str).str[:2] + " " +
    movehistory['saat dilimi'].astype(str)
)


# In[40]:


movehistory['saatdilimleri']=movehistory['SSTL']


# In[41]:


movehistory['TOC'] = (
    movehistory['Time Completed'].astype(str).str[7:9] + "/" +
    movehistory['ay'].map(month_map).fillna("") + "/20" +
    movehistory['Time Completed'].astype(str).str[:2] + " " +
    movehistory['w'].astype(str).str[:5]
)


# In[42]:


movehistory['tümtarih'] = (
    movehistory['sonuc zaman'].astype(str).str[:2] + "/" +
    movehistory['ay'].map(month_map).fillna("") + "/20" +
    np.where(
        movehistory['Move Kind'] == "Discharge",
        movehistory['Time of Fetch'].astype(str).str[:2],
        movehistory['Time Completed'].astype(str).str[:2]
    ) + " " +
    movehistory['birleştirsaat'].astype(str).str[-8:]
)


# In[43]:


movehistory['TOC'] = pd.to_datetime(movehistory['TOC'], format='%d/%m/%Y %H:%M', errors='coerce')
movehistory['Tof'] = pd.to_datetime(movehistory['Tof'], format='%d/%m/%Y %H:%M', errors='coerce')


# In[44]:


movehistory['TTT'] = (movehistory['TOC'] - movehistory['Tof']).dt.total_seconds() / (24 * 60 * 60)


# In[45]:


qc_values = movehistory['QC?'].unique()


# In[46]:


qc_values


# In[47]:


for qc in qc_values:
    df = movehistory[movehistory['QC?'] == qc].copy()
    df['DischargeCount'] = (df['Move Kind'] == 'Discharge').astype(int)
    df['LoadCount'] = (df['Move Kind'] == 'Load').astype(int)
    df_summary = df.groupby('tümtarih', as_index=False)[['DischargeCount', 'LoadCount']].sum()
    df_summary['tümtarih'] = pd.to_datetime(df_summary['tümtarih'], dayfirst=True, errors='coerce')
    df_summary = df_summary.sort_values('tümtarih').reset_index(drop=True)
    delta = df_summary['tümtarih'].diff()
    mask = df_summary['tümtarih'].notna() & (df_summary['DischargeCount'] > 0)
    df_summary['DischargeDuration'] = np.where(mask, delta, pd.Timedelta(0)).astype('timedelta64[ns]')
    if len(df_summary) > 0:
        df_summary.loc[0, 'DischargeDuration'] = pd.Timedelta(0)
    df_summary["DischargeDuration"] = df_summary["DischargeDuration"].apply(
        lambda x: f"{int(x.total_seconds()//3600):02d}:"
                  f"{int((x.total_seconds()%3600)//60):02d}:"
                  f"{int(x.total_seconds()%60):02d}"
    )
    delta = df_summary['tümtarih'].diff()
    gm_zero = df_summary['DischargeDuration'].eq('00:00:00')

    mask_load = (
        (df_summary['LoadCount'] > 0) &
        df_summary['tümtarih'].notna() &
        gm_zero
    )

    df_summary['LoadDuration'] = np.where(mask_load, delta, pd.Timedelta(0)).astype('timedelta64[ns]')
    if len(df_summary) > 0:
        df_summary.loc[0, 'LoadDuration'] = pd.Timedelta(0)

    df_summary["LoadDuration"] = df_summary["LoadDuration"].apply(
        lambda x: f"{int(x.total_seconds()//3600):02d}:"
                  f"{int((x.total_seconds()%3600)//60):02d}:"
                  f"{int(x.total_seconds()%60):02d}"
    )

    df_summary['gün']  = df_summary['tümtarih'].dt.day
    df_summary['ay']   = df_summary['tümtarih'].dt.month
    df_summary['yıl']  = df_summary['tümtarih'].dt.year
    df_summary['saat'] = df_summary['tümtarih'].dt.strftime('%H:%M:%S')
    df_summary['ilk'] = np.where(
        (df_summary['gün'] == 0) | (df_summary['gün'].astype(str) == "0"),"",
        pd.to_datetime(
            df_summary['gün'].astype(str).str.zfill(2) + "." +
            df_summary['ay'].astype(str).str.zfill(2) + "." +
            df_summary['yıl'].astype(str) + " " +
            df_summary['saat'].astype(str),
            format="%d.%m.%Y %H:%M:%S",
            errors="coerce"
        ).dt.strftime("%d.%m.%Y %H:%M:%S"))
    df_summary['son'] = df_summary['ilk'].shift(-1)
    df_summary['son'] = pd.to_datetime(df_summary['son'],format="%d.%m.%Y %H:%M:%S",errors="coerce").dt.strftime("%d.%m.%Y %H:%M")
    globals()[f"{qc}"] = df
    globals()[f"{qc}data"] = df_summary[['tümtarih', 'DischargeCount', 'LoadCount','DischargeDuration','LoadDuration','gün','ay','yıl','saat','ilk','son']]


# In[48]:


QC4data


# In[49]:


vca=pd.read_excel(r'T:\DataReporting\begüm\CraneDelayOptimization\Vessel Crane Activity.xlsx',header=0)


# In[50]:


vcaqc = vca['Crane'].unique()


# In[51]:


vcaqc


# In[52]:


for qc in vcaqc:
    df = vca[vca['Crane']== qc].copy()
    df['Date'] = pd.to_datetime(df['Date'],format='%Y-%m-%d',errors='coerce')
    start_dt = pd.to_datetime(df['Start'].astype(str), format='%H:%M:%S', errors='coerce')
    df['Date2'] = df['Date'].dt.strftime('%d.%m.%Y') + ' ' + start_dt.dt.strftime('%H:%M:%S')
    df['Gün'] = df['Date'].dt.day
    df['Ay']  = df['Date'].dt.month
    df['Yıl'] = df['Date'].dt.year
    df['ilk'] = (df['Gün'].astype(str).str.zfill(2) + '.' +df['Ay'].astype(str).str.zfill(2) + '.' +df['Yıl'].astype(str) + ' ' +df['Start'].astype(str))
    df['son'] = (df['Gün'].astype(str).str.zfill(2) + '.' +df['Ay'].astype(str).str.zfill(2) + '.' +df['Yıl'].astype(str) + ' ' +df['End'].astype(str))
    globals()[f"{qc}VCA"] = df


# In[53]:


QC4VCA


# In[54]:


movehistory['tümtarih'] = pd.to_datetime(movehistory['tümtarih'], dayfirst=True, errors='coerce')


# In[55]:


movehistory['tümtarih'] = movehistory['tümtarih'].dt.strftime('%d.%m.%Y %H:%M:%S')


# In[56]:


movehistory = movehistory[(movehistory['Move Kind']=="Discharge")|(movehistory['Move Kind']=='Load')]


# In[57]:


mindate = movehistory['tümtarih'].min()


# In[58]:


maxdate = movehistory['tümtarih'].max()


# In[59]:


mindate


# In[60]:


maxdate


# In[61]:


vals = movehistory['Carrier Visit'].dropna().unique()
vessel_visit = vals[0] if len(vals) else ""


# In[62]:


def parse_mixed(s):
    s = s.astype(str)
    dt = pd.to_datetime(s, format="%d.%m.%Y %H:%M", errors="coerce")
    return dt.fillna(pd.to_datetime(s, format="%d.%m.%Y %H:%M:%S", errors="coerce"))

qcs_common = sorted({k[:-3] for k in globals() if k.endswith("VCA")}
                    & {k[:-4] for k in globals() if k.endswith("data")})

for qc in qcs_common:
    vca = globals()[f"{qc}VCA"].copy()
    dat = globals()[f"{qc}data"].copy()

    vca["ilk_dt"]  = parse_mixed(vca["ilk"])
    dat["son_dt"]  = parse_mixed(dat["son"])
    dat["ilk_dt2"] = parse_mixed(dat["ilk"])

    vca = vca.sort_values("ilk_dt").reset_index(drop=True)
    dat = dat.dropna(subset=["son_dt"]).sort_values("son_dt").reset_index(drop=True)

    m = pd.merge_asof(
        vca[["ilk_dt"]],
        dat[["son_dt", "ilk_dt2"]],
        left_on="ilk_dt", right_on="son_dt",
        direction="forward",
        allow_exact_matches=False
    )

    vca["hareketlerstart"] = m["ilk_dt2"].dt.strftime("%d.%m.%Y %H:%M:%S")
    vca["hareketlerend"] = m["son_dt"].dt.strftime("%d.%m.%Y %H:%M:%S")
    vca["StartMeal"] = np.where(vca["Activity Desc"].eq("MEAL_BREAK"),vca["Start"],np.nan)
    mask = vca["Activity Desc"].eq("MEAL_BREAK")
    start_dt = pd.to_datetime(vca["Start"].astype(str), format="%H:%M:%S", errors="coerce")
    start_dt = start_dt.fillna(pd.to_datetime(vca["Start"].astype(str), format="%H:%M:%S", errors="coerce"))
    vca["EndMeal"] = np.where(mask, start_dt + pd.Timedelta(minutes=45), pd.NaT)
    vca["EndMeal"] = vca["EndMeal"].dt.strftime("%H:%M:%S")
    vca["Date"] = pd.to_datetime(vca["Date"], format="%Y-%m-%d", errors="coerce")
    start_dt = pd.to_datetime(vca["Start"].astype(str), format="%H:%M:%S", errors="coerce") \
             .fillna(pd.to_datetime(vca["Start"].astype(str), format="%H:%M", errors="coerce"))
    vca["navisbeklemelerstart"] = vca["Date"].dt.strftime("%d.%m.%Y") + " " + start_dt.dt.strftime("%H:%M:%S")
    vca["navisbeklemelerstart+45dk"] = (pd.to_datetime(vca["navisbeklemelerstart"], format="%d.%m.%Y %H:%M:%S", errors="coerce") + pd.Timedelta(minutes=45)).dt.strftime("%d.%m.%Y %H:%M:%S")
    vca["tablo start"] = np.where(
    vca["Activity Desc"].eq("MEAL_BREAK"), vca["hareketlerstart"],np.where(
        vca["hareketlerstart"].eq(vca["hareketlerstart"].shift(1)), 
        vca["navisbeklemelerstart"],
        vca["hareketlerstart"]
    ))
    base = pd.to_datetime(vca["navisbeklemelerstart"], format="%d.%m.%Y %H:%M:%S", errors="coerce")
    dur = pd.to_timedelta(vca["Duration"].astype(str), errors="coerce")
    vca["navisbeklemeler_end_dt"] = base + dur
    vca["navisbeklemeler_end"] = vca["navisbeklemeler_end_dt"].dt.strftime("%d.%m.%Y %H:%M:%S")
    start_dt = pd.to_datetime(vca["navisbeklemelerstart"], format="%d.%m.%Y %H:%M:%S", errors="coerce") \
    .fillna(pd.to_datetime(vca["navisbeklemelerstart"], format="%d.%m.%Y %H:%M", errors="coerce"))
    
    end_dt = pd.to_datetime(vca["navisbeklemeler_end"], format="%d.%m.%Y %H:%M:%S", errors="coerce") \
    .fillna(pd.to_datetime(vca["navisbeklemeler_end"], format="%d.%m.%Y %H:%M", errors="coerce"))
    
    mindate_dt = pd.to_datetime(mindate, format="%d.%m.%Y %H:%M:%S", errors="coerce")
    maxdate_dt = pd.to_datetime(maxdate, format="%d.%m.%Y %H:%M:%S", errors="coerce")
    
    vca["control"] = np.where((start_dt >= mindate_dt) & (end_dt <= maxdate_dt), pd.NaT, "X")

    L  = pd.to_datetime(vca["hareketlerend"],               dayfirst=True, errors="coerce")    
    K3 = pd.to_datetime(vca["hareketlerstart"].shift(-1),   dayfirst=True, errors="coerce")     
    L3 = pd.to_datetime(vca["hareketlerend"].shift(-1),     dayfirst=True, errors="coerce")     
    
    ctrl_x  = vca["control"].astype(str).str.lower().eq("x")   
    E3_meal = vca["Activity Desc"].shift(-1).eq("MEAL_BREAK")      
    E2_meal = vca["Activity Desc"].eq("MEAL_BREAK")                     
    
    vca["tabloend"] = np.where(
        ctrl_x, "",
        np.where(
            E3_meal & (L > K3), vca["navisbeklemeler_end"],            
            np.where(
                E2_meal, vca["navisbeklemelerstart+45dk"],               
                np.where(
                    L3 <= L, vca["navisbeklemelerstart"].shift(-1),  
                    vca["hareketlerend"]                                
                )
            )
        )
    )
    vca["tabloend"] = vca["tabloend"].fillna(vca["hareketlerend"])
    
    O_dt = pd.to_datetime(vca['tablo start'], dayfirst=True, errors='coerce')
    Q_dt = pd.to_datetime(vca['tabloend'], dayfirst=True, errors='coerce')
    
    out = []
    n = len(vca)
    
    for i in range(n):
        if str(vca.at[i, 'control']).lower() == 'x':
            out.append('')
            continue
        
        prevP_valid = (i > 0) and (pd.notna(out[i-1]) and str(out[i-1]) != '')
        
        o2 = O_dt.iat[i]
        q1 = Q_dt.iat[i-1] if i > 0 else pd.NaT
        o1 = O_dt.iat[i-1] if i > 0 else pd.NaT
        
        if prevP_valid and pd.notna(o2) and pd.notna(q1) and (o2 < q1):
            out.append(vca.at[i-1, 'tabloend'])
        elif pd.notna(o2) and pd.notna(o1) and (o2 < o1):
            out.append(vca.at[i-1, 'tabloend'])
        else:
            out.append(vca.at[i, 'tablo start'])
    vca['tablostart2'] = out
    vca
    terminal = {"BREAKDOWN","BREAKDOWN CR","BREAKDOWN VS","CHANGE_BAY","CONTAINER WT","CRANE ALARM","EQ. CHANGE","HATCH MOVE","HATCHMOVE","LASHING",
                "MEAL_BREAK","MEAL BREAK","OP DAMAGE","REHANDLES","START CARGO","STRIKE","SYSTEM_DELAY","TT_WAITING","UNIT REPAIR","VESSEL PREP.","BREAK TIME",
                "Q.SIDE_BREAK"}
    non_terminal = {"ANCHORAGE","CUSTOMS HOLD","END CARGO","LACK_OF_CRG","LASHING_CREW","PAN_WAITING","WAIT VESSEL","WAITING PLAN","WEATHER","TWISTLOCK",
                    "MSC_SEAL_CK","HYDRAULIC HATCH MOVE","REEFER_RPR","OPS PAUSE"}
    
    vca["DelayType"] = np.where(
        vca["Activity Desc"].isin(terminal), "Terminal",
        np.where(vca["Activity Desc"].isin(non_terminal), "Non Terminal", "Unknown"))
    I = pd.to_datetime(vca["tablostart2"], dayfirst=True, errors="coerce")
    J = pd.to_datetime(vca["tabloend"],    dayfirst=True, errors="coerce")
    I_prev = I.shift(1)
    
    cond1 = (I < I_prev) & I_prev.notna()               
    cond2 = (J < I)                                       
    cond3 = (I >= mindate_dt) & (J <= maxdate_dt)          
    
    vca["gemibekleme"] = np.where(cond1, "X",
                              np.where(cond2, "X",
                                       np.where(cond3, "", "X")))
    start_dt = pd.to_datetime(vca['tablostart2'], dayfirst=True, errors='coerce')
    end_dt   = pd.to_datetime(vca['tabloend'],    dayfirst=True, errors='coerce')
    
    delta = end_dt - start_dt
    
    mask = vca['gemibekleme'].astype(str).str.lower().eq('x')
    vca['durationnew_td'] = delta.mask(mask)
    
    vca['durationnew'] = vca['durationnew_td'].apply(
        lambda x: "" if pd.isna(x) else f"{int(x.total_seconds()//3600):02d}:"
        f"{int((x.total_seconds()%3600)//60):02d}:"f"{int(x.total_seconds()%60):02d}")
    vca['VesselVisit'] = vessel_visit
    vca['Facility'] = 'Puerto Bolivar'
    vca = vca[['Facility','VesselVisit','Crane','Activity Desc','durationnew','Remarks','DelayType','tablostart2','tabloend']]
    vca = vca.rename(columns={"durationnew":"Duration",'DelayType':'DelayTypes','tablostart2':'StartDateTime','tabloend':'EndDateTime'})

    globals()[f"{qc}VCA"] = vca


# In[63]:


accessdelays = pd.concat(
    [globals()[f"{qc}VCA"].copy() for qc in vcaqc if f"{qc}VCA" in globals()],
    ignore_index=True, sort=False
)
globals()["accessdelays"] = accessdelays


# In[64]:


accessdelays.to_excel(r'T:\DataReporting\begüm\CraneDelayOptimization\DelayReportBolivar.xlsx',index=False)


# In[ ]:




