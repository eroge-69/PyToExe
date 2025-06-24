#!/usr/bin/env python3
def calcola_lbwoer(peso, altezza, sesso):
    # Calcola la Lean Body Weight (LBW) usando la formula di Boer.
    sesso = sesso.upper()
    if sesso == 'M':
        lbw = (0.407 * peso) + (0.267 * altezza) - 19.2
    elif sesso == 'F':
        lbw = (0.252 * peso) + (0.472 * altezza) - 48.3        
    else:
        raise ValueError("Sesso non riconosciuto. Usa 'M' per maschio o 'F' per femmina.")
    return lbw

def calcola_bsa(peso, altezza):
    # Calcola la BSA Body Surface Area usando la formula di Du Bois & Du Bois (1916).
    bsa = 0.007184 * pow(altezza, 0.725) * pow(peso, 0.425)
    return bsa   

def calcola_ckdepi(creatinina, eta, sesso):
    # Calcola la CKD-EPI con la formula del 2021.
    sesso = sesso.upper()
    if sesso == 'M':
        sex = float(1)
        if creatinina <= 0.9:
            A = float(0.9)
            B = float(-0.302)
        if creatinina > 0.9:
            A = float(0.9)
            B = float(-1.2)
    if sesso == 'F':
        sex = float(1.012)       
        if creatinina <= 0.7:
            A = float(0.7)
            B = float(-0.241)
        if creatinina > 0.7:
            A = float(0.7)
            B = float(-1.2)
    ckdepi = 142 * pow((creatinina/A), B) * pow(0.9938, eta) * sex
    return ckdepi        

def calcola_cg(creatinina, eta, peso, sesso):
    # Calcola la eGFR con l'equazione di Cockcroft-Gault (1973).
    sesso = sesso.upper()
    if sesso == 'M':
        sex = float(1)
    if sesso == 'F':
        sex = float(0.85)
    cg = sex * (140 - eta) * peso / 72 * creatinina
    return cg

def main():
    try:
        print(f"Calcolo della Lean Body Weight (LBW) secondo formula di Boer e dei Procolli/Volumi di MDC")
        sesso = input("Inserisci il sesso ('M o m' per maschio, 'F o f' per femmina): ").strip()
        eta = float(input("Inserisci l'età (anni): "))
        peso = float(input("Inserisci il peso (kg): "))
        altezza = float(input("Inserisci l'altezza (cm): "))
        creatinina = float(input("Inserisci la creatininemia (mg/dl) [default 1.0]: "))
        if not creatinina:
            creatinina = float(1.0)
        mheutente = float(input("Inserisci MHE (HU) [default 50HU]: "))
        lbw = calcola_lbwoer(peso, altezza, sesso)
        bsa = calcola_bsa(peso, altezza)
        ckdepi = calcola_ckdepi(creatinina, eta, sesso)
        cg = calcola_cg(creatinina, eta, peso, sesso)
        print(f"La Lean Body Weight calcolata è: {lbw:.2f} kg")
        # Protocollo di Caruso (2018)  
        # Caruso (2018) 700 mgI/Kg * LBW(Kg)      
        volume350C = round(lbw * 700 / 350)
        volume370C = round(lbw * 700 / 370)
        volume400C = round(lbw * 700 / 400)
        if not mheutente:
            mhe = float(50)
        else:
            mhe = float(mheutente)
        print(f"BSA Body Surface Area: {bsa:.2f} m\xb2")
        print(f"eGFR con equazione CKD-EPI [2021] è: {ckdepi:.2f} ml/min")
        egfr = ckdepi * 1.73 / bsa
        print(f"eGFR con equazione CKD-EPI [2021] normalizzata su bsa: {egfr:.2f} ml/min/m\xb2")    
        # Protocollo di Kondo (2010)
        # Kondo (2010) Dose(mgI) = (MHE*LBW(Kg)*1000/77.9)
        volume350K = round((mhe * lbw * 12.836970475) / 350)
        volume370K = round((mhe * lbw * 12.836970475) / 370)
        volume400K = round((mhe * lbw * 12.836970475) / 400)
        # Protocollo di Heiken (1995)
        # Heiken (1995) Dose(mgI) = (MHE*TBW(Kg)*1000/96)
        volume350H = round((mhe * peso * 10.416666667) / 350)
        volume370H = round((mhe * peso * 10.416666667) / 370)
        volume400H = round((mhe * peso * 10.416666667) / 400)
        # Calcolo di Flussi a durata di iniezione costante 30 secondi e 35 secondi
        # Caruso - Boer LBW
        f35030C = volume350C/30 
        f35035C = volume350C/35
        f37030C = volume370C/30
        f37035C = volume370C/35
        f40030C = volume400C/30
        f40035C = volume400C/35
        # Kondo - Boer LBW
        f35030K = volume350K/30 
        f35035K = volume350K/35
        f37030K = volume370K/30
        f37035K = volume370K/35
        f40030K = volume400K/30
        f40035K = volume400K/35
        # Heiken TBW
        f35030H = volume350H/30 
        f35035H = volume350H/35
        f37030H = volume370H/30
        f37035H = volume370H/35
        f40030H = volume400H/30
        f40035H = volume400H/35
        print(f"Il Volume di Contrasto per il Protocollo Caruso(2018) MDC [350] è: {volume350C:.2f} ml")
        print(f"Flusso a 30 secondi {f35030C:.2f} ml/s - Flusso a 35 secondi {f35035C:.2f} ml/s")
        print(f"Il Volume di Contrasto per il Protocollo Caruso(2018) MDC [370] è: {volume370C:.2f} ml")
        print(f"Flusso a 30 secondi {f37030C:.2f} ml/s - Flusso a 35 secondi {f37035C:.2f} ml/s")
        print(f"Il Volume di Contrasto per il Protocollo Caruso(2018) MDC [400] è: {volume400C:.2f} ml")
        print(f"Flusso a 30 secondi {f40030C:.2f} ml/s - Flusso a 35 secondi {f40035C:.2f} ml/s")
        print(f"Volumi di MdC per Maximum Hepatic Enhancement {mhe}HU (LBW):")
        print(f"Il Volume di Contrasto per il Protocollo Kondo(2010) MDC [350] è: {volume350K:.2f} ml")
        print(f"Flusso a 30 secondi {f35030K:.2f} ml/s - Flusso a 35 secondi {f35035K:.2f} ml/s")
        print(f"Il Volume di Contrasto per il Protocollo Kondo(2010) MDC [370] è: {volume370K:.2f} ml")
        print(f"Flusso a 30 secondi {f37030K:.2f} ml/s - Flusso a 35 secondi {f37035K:.2f} ml/s")
        print(f"Il Volume di Contrasto per il Protocollo Kondo(2010) MDC [400] è: {volume400K:.2f} ml")
        print(f"Flusso a 30 secondi {f40030K:.2f} ml/s - Flusso a 35 secondi {f40035K:.2f} ml/s")
        print(f"Volumi di MdC per Maximum Hepatic Enhancement {mhe}HU (TBW):")
        print(f"Il Volume di Contrasto per il Protocollo Heiken(1995) MDC [350] è: {volume350H:.2f} ml")
        print(f"Flusso a 30 secondi {f35030H:.2f} ml/s - Flusso a 35 secondi {f35035H:.2f} ml/s")
        print(f"Il Volume di Contrasto per il Protocollo Heiken(1995) MDC [370] è: {volume370H:.2f} ml")
        print(f"Flusso a 30 secondi {f37030H:.2f} ml/s - Flusso a 35 secondi {f37035H:.2f} ml/s")
        print(f"Il Volume di Contrasto per il Protocollo Heiken(1995) MDC [400] è: {volume400H:.2f} ml")
        print(f"Flusso a 30 secondi {f40030H:.2f} ml/s - Flusso a 35 secondi {f40035H:.2f} ml/s")
        # Medie Aritmetiche dei Volumi Caruso-Kondo
        mediaCK350 = (volume350C + volume350K) / 2
        mediaCK370 = (volume370C + volume370K) / 2
        mediaCK400 = (volume400C + volume400K) / 2
        # Medie Ponderate sul MHE dei Volumi Caruso-Kondo
        mediaCK350p = (volume350C * 50 + volume350K * mhe) / (50 + mhe)
        mediaCK370p = (volume370C * 50 + volume370K * mhe) / (50 + mhe)
        mediaCK400p = (volume400C * 50 + volume400K * mhe) / (50 + mhe)
        # Flussi Medie Aritmetiche
        f35030CK = mediaCK350/30 
        f35035CK = mediaCK350/35
        f37030CK = mediaCK370/30
        f37035CK = mediaCK370/35
        f40030CK = mediaCK400/30
        f40035CK = mediaCK400/35
        # Flussi Medie Ponderate
        f35030CKp = mediaCK350p/30 
        f35035CKp = mediaCK350p/35
        f37030CKp = mediaCK370p/30
        f37035CKp = mediaCK370p/35
        f40030CKp = mediaCK400p/30
        f40035CKp = mediaCK400p/35
        print(f"**************************************")
        print(f"***Volumi di MdC medi Caruso-Kondo:***")
        print(f"***Media Aritmetica:***")
        print(f"Il Volume di Contrasto MDC [350] è: {mediaCK350:.2f} ml")
        print(f"Flusso a 30 secondi {f35030CK:.2f} ml/s - Flusso a 35 secondi {f35035CK:.2f} ml/s")
        print(f"Il Volume di Contrasto MDC [370] è: {mediaCK370:.2f} ml")
        print(f"Flusso a 30 secondi {f37030CK:.2f} ml/s - Flusso a 35 secondi {f37035CK:.2f} ml/s")
        print(f"Il Volume di Contrasto MDC [400] è: {mediaCK400:.2f} ml")
        print(f"Flusso a 30 secondi {f40030CK:.2f} ml/s - Flusso a 35 secondi {f40035CK:.2f} ml/s")
        print(f"***Media Ponderata per MHE:***")
        print(f"Il Volume di Contrasto MDC [350] è: {mediaCK350p:.2f} ml")
        print(f"Flusso a 30 secondi {f35030CKp:.2f} ml/s - Flusso a 35 secondi {f35035CKp:.2f} ml/s")
        print(f"Il Volume di Contrasto MDC [370] è: {mediaCK370p:.2f} ml")
        print(f"Flusso a 30 secondi {f37030CKp:.2f} ml/s - Flusso a 35 secondi {f37035CKp:.2f} ml/s")
        print(f"Il Volume di Contrasto MDC [400] è: {mediaCK400p:.2f} ml")
        print(f"Flusso a 30 secondi {f40030CKp:.2f} ml/s - Flusso a 35 secondi {f40035CKp:.2f} ml/s")
        print(f"**************************************")
        # Calcolo parametri di sicurezza quantità di molecola iodata secondo Nyman-Bjork grammi Iodio/eGFR-CG
        grammiiodiostandard = peso * 0.6
        grammiiodioheiken = mhe * peso / 96
        cgnormalizzata = cg * 1.73 /bsa
        NBstandard = grammiiodiostandard / cg
        NBstandardN = grammiiodiostandard / cgnormalizzata
        NBHeiken = grammiiodioheiken /cg
        NBHeikenN = grammiiodioheiken /cgnormalizzata
        print(f"Parametri di Sicurezza secondo Nyman-Bjork [gI/eGFR-CG < 1]:")
        print(f"e-GFR Cockcroft-Gault: {cg:.2f} ml/min")
        print(f"e-GFR Cockcroft-Gault normalizzata su BSA: {cgnormalizzata:.2f} ml/min/m\xb2")
        print(f"Grammi di Iodio da Protocollo Standard [gIodio * TBW(Kg)]: {grammiiodiostandard:.2f} gI")
        print(f"Nyman-Bjork Standard: {NBstandard:.2f}")
        print(f"Nyman-Bjork Standard [eGFR-CG normalizzata]: {NBstandardN:.2f}")
        print(f"Grammi di Iodio da Protocollo Heiken [MHE * TBW(Kg) / 96]: {grammiiodioheiken:.2f} gI")
        print(f"Nyman-Bjork Heiken: {NBHeiken:.2f}")
        print(f"Nyman-Bjork Heiken [eGFR-CG normalizzata]: {NBHeikenN:.2f}")
    except ValueError as e:
        print(f"Errore: {e}")

if __name__ == "__main__":
    main()
