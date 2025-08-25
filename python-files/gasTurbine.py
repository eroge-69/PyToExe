#!/usr/bin/env python
# coding: utf-8

# In[4]:


import numpy as np
import matplotlib.pyplot as plt

def brayton_itki_analizi(pr, T3, n_komp, n_turb, n_noz, gama, R, m_debisi):
    """
    Brayton çevriminin itki değerini hesaplar.
    
    Args:
        pr (float): Basınç oranı (P2/P1).
        T3 (float): Türbin giriş sıcaklığı (K).
        n_komp (float): Kompresör izentropik verimi.
        n_turb (float): Türbin izentropik verimi.
        n_noz (float): Nozul verimi.
        gama (float): Isı kapasitesi oranı (cp/cv).
        R (float): Gaz sabiti (J/(kg*K)).
        m_debisi (float): Kütle debisi (kg/s).
    
    Returns:
        float: İtki kuvveti (N).
    """
    
    # Sabitler
    cp = gama * R / (gama - 1)
    P1 = 101325  # Pa (Ortam basıncı)
    
    # 1'den 2'ye (Kompresör)
    T1 = 298  # K (Ortam sıcaklığı)
    T2s = T1 * pr**((gama - 1) / gama)
    T2 = T1 + (T2s - T1) / n_komp
    
    # 3'ten 4'e (Türbin)
    # W_turb = W_komp olduğunda, T3 - T4 = T2 - T1'dir.
    W_komp = cp * (T2 - T1)
    T4s = T3 - W_komp / (n_turb * cp)
    T4 = T3 - (T3 - T4s) * n_turb
    
    # 4'ten 5'e (Nozul)
    P5 = P1  # Pa (Ortam basıncı, çıkış basıncı ile aynı varsayılır)
    P4 = pr * P1 
    
    T5s = T4 / (P4 / P5)**((gama - 1) / gama)
    T5 = T4 - n_noz * (T4 - T5s)
    
    # Egzoz hızını hesapla (nozul çıkış hızı)
    V5 = np.sqrt(2 * cp * (T4 - T5))
    
    # İtki kuvvetini hesapla (Newton'un ikinci hareket yasası)
    F_itki = m_debisi * V5
    
    return F_itki

#-------------------------------------------------------------------------------------------------
# GRAFİK VE KONSOL ÇIKTISI OLUŞTURMA BÖLÜMÜ
#-------------------------------------------------------------------------------------------------

# Parametrelerin nasıl değiştiğini görmek için döngü
pr_degerleri = np.linspace(2, 20, 50)  # Basınç oranı 2'den 20'ye kadar 50 farklı değer

# Farklı sıcaklıklar için itki eğrileri oluşturmak
# T3_degerleri listesine istediğiniz kadar yeni sıcaklık değeri ekleyebilirsiniz.
T3_degerleri = [1200, 1300, 1400, 1500, 1600, 1700, 1800]

m_debisi_sabit = 1  # kg/s (Sabit kütle debisi)

plt.figure(figsize=(12, 6))

for T3 in T3_degerleri:
    itki_degerleri = []
    
    for pr in pr_degerleri:
        F_itki = brayton_itki_analizi(pr, T3, 0.85, 0.90, 0.95, 1.4, 287, m_debisi_sabit)
        itki_degerleri.append(F_itki)
    
    plt.plot(pr_degerleri, itki_degerleri, label=f'T3 = {T3} K')

plt.title('Brayton Çevrimi İtki Değeri vs. Basınç Oranı')
plt.xlabel('Basınç Oranı')
plt.ylabel('İtki Kuvveti (N)')
plt.grid(True)
plt.legend()
plt.show()

#-------------------------------------------------------------------------------------------------
# SADECE BİR NOKTA İÇİN HESAPLAMA VE ÇIKTI BÖLÜMÜ
#-------------------------------------------------------------------------------------------------

pr_tek = 10
T3_tek = 1500
F_itki = brayton_itki_analizi(pr_tek, T3_tek, 0.85, 0.90, 0.95, 1.4, 287, 1)

print(f"\nBasınç Oranı = {pr_tek}, Türbin Giriş Sıcaklığı = {T3_tek} K için:")
print(f"İtki Kuvveti: {F_itki:.2f} N")

