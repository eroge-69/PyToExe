
import streamlit as st
import pandas as pd
import random
from datetime import datetime

# ----------------------------------------
# Зберігання подій
# ----------------------------------------
events = []

def log_event(block_name, data, status):
    record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "block_name": block_name,
        **data,
        "status": status
    }
    events.append(record)

class Block:
    STATUS_NORMAL = "Норма"
    STATUS_ICE    = "Ожеледь"
    STATUS_BREAK  = "Обрив"
    STATUS_SHORT  = "Коротке замикання"

    def __init__(self, idx):
        self.name = f"BV{idx}"

    def generate(self):
        return {
            'Ua': round(random.gauss(220, 5), 2),
            'Ub': round(random.gauss(220, 5), 2),
            'Uc': round(random.gauss(220, 5), 2),
            'Ia': round(random.gauss(10, 1), 2),
            'Ib': round(random.gauss(10, 1), 2),
            'Ic': round(random.gauss(10, 1), 2),
            'T':  round(random.gauss(-20, 5), 2),
            'RH': round(random.gauss(75, 10), 2),
            **{f'kz_{p1}{p2}': random.choice([0,1]) for p1,p2 in (('A','B'),('B','C'),('C','A'))},
            **{f'obr_{ph}': random.choice([0,1]) for ph in ('A','B','C')}
        }

    def determine_status(self, data):
        if any(v == 1 for k, v in data.items() if k.startswith('kz_')):
            return self.STATUS_SHORT
        if any(v == 1 for k, v in data.items() if k.startswith('obr_')):
            return self.STATUS_BREAK
        if data['T'] < 0 and data['RH'] > 80:
            return self.STATUS_ICE
        return self.STATUS_NORMAL

def simulate(block_count=7, iterations=10):
    events.clear()
    blocks = [Block(i) for i in range(1, block_count+1)]
    for _ in range(iterations):
        for blk in blocks:
            data = blk.generate()
            status = blk.determine_status(data)
            log_event(blk.name, data, status)
    return pd.DataFrame(events)

# ----------------------------------------
# Streamlit інтерфейс
# ----------------------------------------
st.title("Симуляція стану блоків")
block_count = st.slider("Кількість блоків", 1, 20, 7)
iterations = st.slider("Кількість ітерацій", 1, 100, 10)

if st.button("Запустити симуляцію"):
    df = simulate(block_count, iterations)
    st.success("Симуляція завершена!")
    st.dataframe(df)
