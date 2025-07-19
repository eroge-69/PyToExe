import streamlit as st
import serial
import time
from collections import deque
import pandas as pd
import matplotlib.pyplot as plt

# ---------- Setup ----------
PORT = "COM8"  # Change this to your Arduino's port
BAUD = 9600

try:
    ser = serial.Serial(PORT, BAUD)
except:
    st.error("⚠️ Could not connect to Arduino. Is it plugged in?")
    st.stop()

# ---------- Streamlit UI ----------
st.set_page_config(page_title="Live Plant Monitor", layout="centered")
st.title("🌿 PhytoSense AI - LIVE Monitor")

signal_data = deque(maxlen=100)
timestamp_data = deque(maxlen=100)

plot = st.line_chart([], height=300)
status_placeholder = st.empty()

# ---------- Loop ----------
while True:
    try:
        line = ser.readline().decode().strip()
        signal = int(line)
        timestamp = time.time()

        signal_data.append(signal)
        timestamp_data.append(timestamp)

        # Update chart
        df = pd.DataFrame({"Signal": list(signal_data)}, index=timestamp_data)
        plot.line_chart(df)

        # Diagnosis
        mean = sum(signal_data) / len(signal_data)
        std = pd.Series(signal_data).std()

        if std > 20:
            status = "⚠️ Plant seems stressed!"
        elif mean < 300:
            status = "💧 Plant might be dehydrated."
        else:
            status = "✅ Plant looks healthy."

        status_placeholder.markdown(f"### 🧠 Status: {status}")

        time.sleep(0.5)  # Smooth update

    except KeyboardInterrupt:
        st.write("🛑 Monitoring stopped.")
        ser.close()
        break
    except:
        st.warning("📴 Waiting for stable signal...")
        continue
