# Programma per il calcolo della temperatura di un disco freno a fine frenata

import math


# Input dei parametri
P_disco = float(input("Inserisci la potenza termica generata per disco [W]: "))
t_frenata = float(input("Inserisci il tempo di frenata [s]: "))
D = float(input("Inserisci il diametro del disco [m]: "))
s = float(input("Inserisci lo spessore del disco [m]: "))
rho = float(input("Inserisci la densità del materiale del disco [kg/m^3]: "))
c = float(input("Inserisci il calore specifico del materiale [J/(kg*K)]: "))
T_iniziale = float(input("Inserisci la temperatura iniziale del disco [°C]: "))
eta = float(input("Inserisci il coefficiente di assorbimento (0-1): "))
T_aria = float(input("Inserisci la temperatura dell'aria ambiente [°C]: "))
h = float(input("Inserisci il coefficiente di convezione h [W/(m^2*K)]: "))


# Energia totale generata per disco durante la frenata
Q_disco = P_disco * t_frenata


# Volume e massa del disco
V = math.pi * (D / 2) ** 2 * s
m_disco = rho * V


# Calore assorbito (senza convezione)
Q_assorbito = eta * Q_disco
Delta_T_no_conv = Q_assorbito / (m_disco * c)
T_finale_no_conv = T_iniziale + Delta_T_no_conv


# Superficie di scambio (approssimazione: 2 facce + bordo cilindrico)
A = 2 * math.pi * (D / 2) ** 2 + math.pi * D * s


# Calore ceduto per convezione durante la frenata
T_media = (T_iniziale + T_finale_no_conv) / 2
Q_conv = h * A * (T_media - T_aria) * t_frenata


# Calore effettivo
Q_eff = Q_assorbito - Q_conv


# Incremento di temperatura con dissipazione
Delta_T = Q_eff / (m_disco * c)
T_finale = T_iniziale + Delta_T


print("\n--- RISULTATI ---")
print(f"Massa disco: {m_disco:.2f} kg")
print(f"Energia totale generata per disco: {Q_disco:.2f} J")
print(f"Aumento di temperatura (senza convezione): {Delta_T_no_conv:.2f} °C")
print(f"Temperatura finale (senza convezione): {T_finale_no_conv:.2f} °C")
print(f"Calore perso per convezione: {Q_conv:.2f} J")
print(f"Aumento di temperatura effettivo: {Delta_T:.2f} °C")
print(f"Temperatura finale con convezione: {T_finale:.2f} °C")
