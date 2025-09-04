import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- Sample portfolio data ---
projects = [
    {"project":"Muğla Ünv. Kafeterya", "city":"Muğla", "status":"Active", "budget_eur":25000, "production_mw":0.025, "cpi":0.95, "spi":1.02, "lat":37.215, "lon":28.363},
    {"project":"Denizli Hükümet", "city":"Denizli", "status":"Active", "budget_eur":75000, "production_mw":0.075, "cpi":1.05, "spi":0.98, "lat":37.774, "lon":29.086},
    {"project":"Istanbul Rooftop A", "city":"İstanbul", "status":"Delayed", "budget_eur":120000, "production_mw":0.12, "cpi":0.82, "spi":0.88, "lat":41.008, "lon":28.978},
    {"project":"Izmir Warehouse", "city":"İzmir", "status":"Active", "budget_eur":90000, "production_mw":0.09, "cpi":1.10, "spi":1.05, "lat":38.423, "lon":27.142},
    {"project":"Bursa Industrial", "city":"Bursa", "status":"Procurement", "budget_eur":60000, "production_mw":0.06, "cpi":0.98, "spi":1.00, "lat":40.195, "lon":29.060},
]
df = pd.DataFrame(projects)

# --- Sidebar filters ---
st.sidebar.title("Filtreler")
status_filter = st.sidebar.multiselect("Proje durumu", options=df["status"].unique(), default=df["status"].unique())
city_filter = st.sidebar.multiselect("Şehir", options=df["city"].unique(), default=df["city"].unique())

df_filtered = df[(df["status"].isin(status_filter)) & (df["city"].isin(city_filter))]

# --- KPI cards ---
st.title("Oexe Dashboard")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Aktif projeler", df_filtered[df_filtered["status"]=="Active"].shape[0])
with col2:
    st.metric("Toplam bütçe (EUR)", f"€{int(df_filtered['budget_eur'].sum()/1000)}k")
with col3:
    st.metric("CPI / SPI", f"{df_filtered['cpi'].mean():.2f} / {df_filtered['spi'].mean():.2f}")
with col4:
    st.metric("Kritik PO gecikmesi", "3")  # static demo value
with col5:
    st.metric("Üretim toplamı", f"{df_filtered['production_mw'].sum():.2f} MW")

# --- Portfolio map ---
st.subheader("Portföy Haritası")

fig, ax = plt.subplots(figsize=(6,4))
ax.set_title("Projeler")
ax.set_xlim(26, 31)
ax.set_ylim(36, 42)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.grid(True, linestyle=":", linewidth=0.5)
ax.scatter(df_filtered["lon"], df_filtered["lat"], s=120, c="blue")

for _, row in df_filtered.iterrows():
    ax.annotate(row["project"], (row["lon"], row["lat"]), xytext=(3,3), textcoords="offset points", fontsize=8)

st.pyplot(fig)

# --- Critical actions ---
st.subheader("Kritik Aksiyonlar")
actions = [
    f"Geciken iş emirleri (2)",
    f"Onay bekleyen PO'lar (4)",
    f"Geciken satınalmalar (1)",
    "Yeni proje oluştur"
]
for a in actions:
    st.write("- ", a)

# --- Project table ---
st.subheader("Projeler Tablosu")
st.dataframe(df_filtered.reset_index(drop=True))

pip install streamlit matplotlib pandas
streamlit run oexe_dashboard_app.py

