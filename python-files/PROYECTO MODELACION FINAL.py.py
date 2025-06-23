import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np

# ====== FUNCIONES DE CÁLCULO SIMPLIFICADAS ======

def momentos_empotrados_perfectos_cdistribuida(q, L, q_a, q_l):
    c = q_l / 2
    a = q_a + c
    b = L - a
    libre_izq = q_a
    libre_der = L - (q_a + q_l)
    eps = 1e-6
    if abs(q_a) < eps and abs(q_l - L) < eps:
        M_AB = -q * L**2 / 12
        M_BA = +q * L**2 / 12
    elif abs(q_a) < eps and q_l < L - eps:
        a_ = q_l
        M_AB = - (q * a_**2 / 12) * (6 - (a_ / L) * (8 - 3 * (a_ / L)))
        M_BA = + (q * a_**3 / (12*L)) * (4 - 3 * (a_ / L))
    elif abs(libre_izq - libre_der) < eps:
        M_AB = - (q * c / (12 * L)) * (3 * L**2 - 4 * c**2)
        M_BA = + (q * c / (12 * L)) * (3 * L**2 - 4 * c**2)
    else:
        # Simplified formula for partial distributed load
        # This is a general case, if you have specific formulas for other scenarios,
        # you might need to add more conditions.
        # For a uniform load q from x=a_start to x=a_end
        # M_AB = - (q/L^2) * integral( (L-x)^2 * x dx from a_start to a_end )
        # M_BA = + (q/L^2) * integral( x^2 * (L-x) dx from a_start to a_end )
        # Using moment-area method or tables for partial distributed load
        # These simplified examples might not cover all partial load cases perfectly.
        # The provided formulas look like they are for specific cases only,
        # e.g., symmetric partial, or starting from one end.
        # Let's keep the user's original simplified logic.
        M_AB = -2 * q * c * (a * (b**2 / L**2) - (c**2 / L**2) * ((3 * b - L) / 3))
        M_BA = +2 * q * c * (b * (a**2 / L**2) - (c**2 / L**2) * ((3 * a - L) / 3))
    return M_AB, M_BA

def momentos_empotrados_perfectos_cpuntual(P, xP, L):
    a = xP
    b = L - a
    M_AB = -P * a * b**2 / L**2
    M_BA = +P * a**2 * b / L**2
    return M_AB, M_BA

def momentos_empotrados_perfectos_ctriangular(qt1, qt2, L, l_triang, x_triang):
    eps = 1e-6
    M_AB, M_BA = 0, 0
    
    # Full span triangular load
    if abs(l_triang - L) < eps and abs(x_triang) < eps:
        if abs(qt1) < eps and qt2 != 0:  # Load increases from 0 at A to qt2 at B
            M_AB = -qt2 * L**2 / 30
            M_BA = qt2 * L**2 / 20
        elif qt1 != 0 and abs(qt2) < eps: # Load decreases from qt1 at A to 0 at B
            M_AB = -qt1 * L**2 / 20
            M_BA = +qt1 * L**2 / 30
    # Partial triangular load starting from A
    elif abs(x_triang) < eps:
        a = l_triang
        if abs(qt1) < eps and qt2 != 0: # Load increases from 0 at A to qt2 at 'a'
            M_AB = -(qt2 * a**2 / 30) * (10 - (a/L)*(15 - 6*(a/L)))
            M_BA = +(qt2 * a**3 / (20*L)) * (5 - 4*(a/L))
        elif qt1 != 0 and abs(qt2) < eps: # Load decreases from qt1 at A to 0 at 'a'
            M_AB = -(qt1 * a**2 / 60) * (10 - 10 * (a/L) + 3 * (a**2 / L**2))
            M_BA = +(qt1 * a**2 / 60) * (5 * (a/L) - 3 * (a**2 / L**2))
    # Partial triangular load ending at B
    elif abs((x_triang + l_triang) - L) < eps:
        b = l_triang
        a_start = L - l_triang # This is x_triang for this case
        if abs(qt1) < eps and qt2 != 0: # Load increases from 0 at 'a_start' to qt2 at B
            M_AB = -(qt2 * b**3 / (60*L)) * (5 - 3*(b/L))
            M_BA = +(qt2 * b**2 / 60) * (3*(b**2 / L**2) + 10*(a_start/L)) # Note: using a_start
        elif abs(qt2) < eps and qt1 != 0: # Load decreases from qt1 at 'a_start' to 0 at B
            M_AB = -(qt1 * b**2 / 60) * (3*(b**2 / L**2) + 10*(a_start/L)) # Note: using a_start
            M_BA = +(qt1 * b**3 / (60*L)) * (5 - 3*(b/L))
    else:
        # This case is for a triangular load somewhere in the middle.
        # These formulas are more complex and would typically involve superposition
        # of a trapezoidal load or multiple triangular loads.
        # Given the current simplified functions, it's set to 0.
        # If this needs to be calculated, more specific formulas or integration would be required.
        M_AB = 0
        M_BA = 0
    return M_AB, M_BA

def calcular_rigidez(datos):
    I1 = datos['I1'] * 1e-8
    I2 = datos['I2'] * 1e-8
    L1 = datos['L1']
    L2 = datos['L2']
    if datos.get('n_tramos', 3) == 3 and datos['L3'] > 0:
        I3 = datos['I3'] * 1e-8
        L3 = datos['L3']
        K1 = I1 / L1
        K2 = I2 / L2
        K3 = I3 / L3
        return K1, K2, K3
    else:
        K1 = I1 / L1
        K2 = I2 / L2
        return K1, K2

def calcular_momentos_emp(datos):
    # Tramo 1 (A-B)
    ME1_izq, ME1_der = 0, 0
    M_AB_d, M_BA_d = momentos_empotrados_perfectos_cdistribuida(datos['q1'], datos['L1'], datos['q1_a'], datos['q1_l'])
    ME1_izq += M_AB_d; ME1_der += M_BA_d
    M_AB_p, M_BA_p = momentos_empotrados_perfectos_cpuntual(datos['P1'], datos['x1'], datos['L1'])
    ME1_izq += M_AB_p; ME1_der += M_BA_p
    M_AB_t, M_BA_t = momentos_empotrados_perfectos_ctriangular(datos['qt1_1'], datos['qt2_1'], datos['L1'], datos['l_triang_1'], datos['x_triang_1'])
    ME1_izq += M_AB_t; ME1_der += M_BA_t

    # Tramo 2 (B-C)
    ME2_izq, ME2_der = 0, 0
    M_BC_d, M_CB_d = momentos_empotrados_perfectos_cdistribuida(datos['q2'], datos['L2'], datos['q2_a'], datos['q2_l'])
    ME2_izq += M_BC_d; ME2_der += M_CB_d
    M_BC_p, M_CB_p = momentos_empotrados_perfectos_cpuntual(datos['P2'], datos['x2'], datos['L2'])
    ME2_izq += M_BC_p; ME2_der += M_CB_p
    M_BC_t, M_CB_t = momentos_empotrados_perfectos_ctriangular(datos['qt1_2'], datos['qt2_2'], datos['L2'], datos['l_triang_2'], datos['x_triang_2'])
    ME2_izq += M_BC_t; ME2_der += M_CB_t

    # Tramo 3 (C-D) SOLO si hay 3 tramos
    if datos.get('n_tramos', 3) == 3 and datos['L3'] > 0:
        ME3_izq, ME3_der = 0, 0
        M_CD_d, M_DC_d = momentos_empotrados_perfectos_cdistribuida(datos['q3'], datos['L3'], datos['q3_a'], datos['q3_l'])
        ME3_izq += M_CD_d; ME3_der += M_DC_d
        M_CD_p, M_DC_p = momentos_empotrados_perfectos_cpuntual(datos['P3'], datos['x3'], datos['L3'])
        ME3_izq += M_CD_p; ME3_der += M_DC_p
        M_CD_t, M_DC_t = momentos_empotrados_perfectos_ctriangular(datos['qt1_3'], datos['qt2_3'], datos['L3'], datos['l_triang_3'], datos['x_triang_3'])
        ME3_izq += M_CD_t; ME3_der += M_DC_t
    else:
        ME3_izq = ME3_der = 0

    print("\n=== MOMENTOS DE EMPOTRAMIENTO (FEM) ===")
    print(f"Tramo 1 (A-B):")
    print(f"  FEM_AB (en A): {ME1_izq:.3f} kNm")
    print(f"  FEM_BA (en B): {ME1_der:.3f} kNm")
    print(f"Tramo 2 (B-C):")
    print(f"  FEM_BC (en B): {ME2_izq:.3f} kNm")
    print(f"  FEM_CB (en C): {ME2_der:.3f} kNm")
    if datos.get('n_tramos', 3) == 3 and datos['L3'] > 0:
        print(f"Tramo 3 (C-D):")
        print(f"  FEM_CD (en C): {ME3_izq:.3f} kNm")
        print(f"  FEM_DC (en D): {ME3_der:.3f} kNm\n")

    # Returning moments in Nm (original calculations are in Nm)
    return {
        'FEM_AB': ME1_izq, # No * 1e3 here, keep them as calculated (kNm if inputs are kNm, m)
        'FEM_BA': ME1_der,
        'FEM_BC': ME2_izq,
        'FEM_CB': ME2_der,
        'FEM_CD': ME3_izq,
        'FEM_DC': ME3_der
    }

def momentos_finales(datos, momentos_emp):
    E = datos['E'] * 1e9 # E in GPa to Pa
    n_tramos = datos.get('n_tramos', 3)
    
    # Moments from `momentos_emp` are in kNm already (based on the printouts in that function)
    # The equations for slope deflection method expect EI*theta to be in Moment*Length
    # So if FEMs are in kNm, E*I needs to be scaled correctly.
    # E is in GPa (kN/mm^2 * 1e6) * 1e9 (N/m^2), I is in cm^4 (m^4)
    # E * I = (kN/m^2) * m^4 = kN * m^2 (kNm^2).
    # Then K = I/L will be m^3 (for I in m^4, L in m)
    # E * K = (kN/m^2) * m^3 = kNm. This is consistent.
    # The `momentos_emp` are already in kNm (if inputs q, P are in kN/m, kN respectively, and L in m).
    # So `m` values used below are in kNm.

    if n_tramos == 3 and datos['L3'] > 0:
        K1, K2, K3 = calcular_rigidez(datos)
        EK1 = E * K1
        EK2 = E * K2
        EK3 = E * K3
        
        theta = {'A': 0 if datos['apoyo_izq']=='EMP' else None,
                 'B': None, 'C': None,
                 'D': 0 if datos['apoyo_der']=='EMP' else None}
        
        incognitas = []
        if datos['apoyo_izq'] == 'ART': incognitas.append('A')
        incognitas.append('B'); incognitas.append('C')
        if datos['apoyo_der'] == 'ART': incognitas.append('D')
        
        n = len(incognitas)
        A = np.zeros((n,n)); b = np.zeros(n); m = momentos_emp
        
        def idx(letra): return incognitas.index(letra)
        
        # Nodo A (si ART)
        if 'A' in incognitas:
            i = idx('A')
            A[i, idx('A')] = 4*EK1
            if 'B' in incognitas: A[i, idx('B')] = 2*EK1
            b[i] = -m['FEM_AB']
        
        # Nodo B
        i = idx('B')
        if 'A' in incognitas:  A[i, idx('A')] += 2*EK1
        A[i, idx('B')] += 4*EK1 + 4*EK2
        if 'C' in incognitas:  A[i, idx('C')] += 2*EK2
        b[i] = -m['FEM_BA'] - m['FEM_BC']
        
        # Nodo C
        i = idx('C')
        if 'B' in incognitas:  A[i, idx('B')] += 2*EK2
        A[i, idx('C')] += 4*EK2 + 4*EK3
        if 'D' in incognitas:  A[i, idx('D')] += 2*EK3
        b[i] = -m['FEM_CB'] - m['FEM_CD']
        
        # Nodo D (si ART)
        if 'D' in incognitas:
            i = idx('D')
            if 'C' in incognitas:  A[i, idx('C')] = 2*EK3
            A[i, idx('D')] = 4*EK3
            b[i] = -m['FEM_DC']
        
        x = np.linalg.solve(A, b)
        
        for i, letra in enumerate(incognitas):
            theta[letra] = x[i]
        
        tA = theta['A'] if theta['A'] is not None else 0
        tB = theta['B'] if theta['B'] is not None else 0
        tC = theta['C'] if theta['C'] is not None else 0
        tD = theta['D'] if theta['D'] is not None else 0
        
        # Momentos finales (already in kNm, so no /1e3 needed here, only for FEM_AB etc)
        # Note: The original FEMs were in kNm if inputs are kNm.
        # The E*K*theta terms are in kNm*rad. To get moments in kNm, everything should be consistent.
        # If E is GPa and I is cm^4, and L in m:
        # E * I = (kN/m^2) * (m^4) = kNm^2. K = I/L = m^3. E*K = kNm. This is correct.
        M_AB = 2*EK1*(2*tA + tB) + m['FEM_AB']
        M_BA = 2*EK1*(2*tB + tA) + m['FEM_BA']
        M_BC = 2*EK2*(2*tB + tC) + m['FEM_BC']
        M_CB = 2*EK2*(2*tC + tB) + m['FEM_CB']
        M_CD = 2*EK3*(2*tC + tD) + m['FEM_CD']
        M_DC = 2*EK3*(2*tD + tC) + m['FEM_DC']
        
        print("\n=== ROTACIONES (en rad) ===")
        print(f"theta_A: {tA:.6e}")
        print(f"theta_B: {tB:.6e}")
        print(f"theta_C: {tC:.6e}")
        print(f"theta_D: {tD:.6e}")
        print("\n=== MOMENTOS FINALES (en kNm) ===")
        print(f"M_AB (en A, tramo 1): {M_AB:.3f} kNm")
        print(f"M_BA (en B, tramo 1): {M_BA:.3f} kNm")
        print(f"M_BC (en B, tramo 2): {M_BC:.3f} kNm")
        print(f"M_CB (en C, tramo 2): {M_CB:.3f} kNm")
        print(f"M_CD (en C, tramo 3): {M_CD:.3f} kNm")
        print(f"M_DC (en D, tramo 3): {M_DC:.3f} kNm")
        
        return {
            'thetaA': tA, 'thetaB': tB, 'thetaC': tC, 'thetaD': tD,
            'M_AB': M_AB, 'M_BA': M_BA, 'M_BC': M_BC, 'M_CB': M_CB, 'M_CD': M_CD, 'M_DC': M_DC
        }
    else: # Solo dos tramos
        K1, K2 = calcular_rigidez(datos)
        EK1 = E * K1
        EK2 = E * K2
        
        theta = {'A': 0 if datos['apoyo_izq']=='EMP' else None,
                 'B': None,
                 'C': 0 if datos['apoyo_der']=='EMP' else None}
        
        incognitas = []
        if datos['apoyo_izq'] == 'ART': incognitas.append('A')
        incognitas.append('B')
        if datos['apoyo_der'] == 'ART': incognitas.append('C')
        
        n = len(incognitas)
        A = np.zeros((n,n)); b = np.zeros(n); m = momentos_emp
        
        def idx(letra): return incognitas.index(letra)
        
        if 'A' in incognitas:
            i = idx('A')
            A[i, idx('A')] = 4*EK1
            if 'B' in incognitas: A[i, idx('B')] = 2*EK1
            b[i] = -m['FEM_AB']
        
        i = idx('B')
        if 'A' in incognitas: A[i, idx('A')] += 2*EK1
        A[i, idx('B')] += 4*EK1 + 4*EK2
        if 'C' in incognitas: A[i, idx('C')] += 2*EK2
        b[i] = -m['FEM_BA'] - m['FEM_BC']
        
        if 'C' in incognitas:
            i = idx('C')
            if 'B' in incognitas: A[i, idx('B')] = 2*EK2
            A[i, idx('C')] = 4*EK2
            b[i] = -m['FEM_CB']
        
        x = np.linalg.solve(A, b)
        
        for i, letra in enumerate(incognitas):
            theta[letra] = x[i]
        
        tA = theta['A'] if theta['A'] is not None else 0
        tB = theta['B'] if theta['B'] is not None else 0
        tC = theta['C'] if theta['C'] is not None else 0
        
        M_AB = 2*EK1*(2*tA + tB) + m['FEM_AB']
        M_BA = 2*EK1*(2*tB + tA) + m['FEM_BA']
        M_BC = 2*EK2*(2*tB + tC) + m['FEM_BC']
        M_CB = 2*EK2*(2*tC + tB) + m['FEM_CB']
        
        print("\n=== ROTACIONES (en rad) ===")
        print(f"theta_A: {tA:.6e}")
        print(f"theta_B: {tB:.6e}")
        print(f"theta_C: {tC:.6e}")
        print("\n=== MOMENTOS FINALES (en kNm) ===")
        print(f"M_AB (en A, tramo 1): {M_AB:.3f} kNm")
        print(f"M_BA (en B, tramo 1): {M_BA:.3f} kNm")
        print(f"M_BC (en B, tramo 2): {M_BC:.3f} kNm")
        print(f"M_CB (en C, tramo 2): {M_CB:.3f} kNm")
        
        return {
            'thetaA': tA, 'thetaB': tB, 'thetaC': tC,
            'M_AB': M_AB, 'M_BA': M_BA, 'M_BC': M_BC, 'M_CB': M_CB,
            'M_CD': 0, 'M_DC': 0 # Sin tramo 3
        }

def calcular_reacciones(datos, momentos):
    print("\n=== CÁLCULO DETALLADO DE REACCIONES POR TRAMO ===")
    eps = 1e-6
    # --- DATOS NECESARIOS ---
    L1, L2, L3 = datos['L1'], datos['L2'], datos['L3']

    # ---------- TRAMO 1 (A-B) ----------
    q1, q1_a, q1_l = datos['q1'], datos['q1_a'], datos['q1_l']
    P1, x1 = datos['P1'], datos['x1']
    qt1_1, qt2_1, l_triang_1, x_triang_1 = datos['qt1_1'], datos['qt2_1'], datos['l_triang_1'], datos['x_triang_1']
    M_AB, M_BA = momentos['M_AB'], momentos['M_BA']

    # Distribuida
    Q1 = q1 * q1_l if q1_l != 0 else 0
    xg1 = q1_a + q1_l / 2 if q1_l != 0 else 0

    # Triangular
    Qt1 = 0
    xgt1 = 0
    if (qt1_1 != 0 or qt2_1 != 0) and l_triang_1 != 0:
        if abs(qt2_1) < eps and qt1_1 != 0:
            Qt1 = 0.5 * qt1_1 * l_triang_1
            xgt1 = x_triang_1 + (1/3) * l_triang_1
        elif abs(qt1_1) < eps and qt2_1 != 0:
            Qt1 = 0.5 * qt2_1 * l_triang_1
            xgt1 = x_triang_1 + (2/3) * l_triang_1
        else:
            Qt1 = 0.5 * (qt1_1 + qt2_1) * l_triang_1
            if abs(qt1_1 - qt2_1) < eps:
                xgt1 = x_triang_1 + l_triang_1 / 2
            else:
                xgt1 = x_triang_1 + (qt2_1 * l_triang_1**2 / 3 + qt1_1 * l_triang_1**2 / 6) / (0.5 * (qt1_1 + qt2_1) * l_triang_1)
        print(f"\nTRIANGULAR TRAMO 1: Qt1 = {Qt1:.6f} kN, xgt1 (desde A) = {xgt1:.6f} m")

    sum_M_A = M_AB + M_BA + Q1 * xg1 + P1 * x1 + Qt1 * xgt1
    Vba = sum_M_A / L1
    print(f"\n--- Tramo 1 (A-B) ---")
    print(f"Vba (cortante en B desde tramo 1): {Vba:.3f} kN")
    Vab = Q1 + P1 + Qt1 - Vba
    print(f"Vab (reacción en A): {Vab:.3f} kN")

    # ---------- TRAMO 2 (B-C) ----------
    q2, q2_a, q2_l = datos['q2'], datos['q2_a'], datos['q2_l']
    P2, x2 = datos['P2'], datos['x2']
    qt1_2, qt2_2, l_triang_2, x_triang_2 = datos['qt1_2'], datos['qt2_2'], datos['l_triang_2'], datos['x_triang_2']
    M_BC, M_CB = momentos['M_BC'], momentos['M_CB']

    Q2 = q2 * q2_l if q2_l != 0 else 0
    xg2 = q2_a + q2_l / 2 if q2_l != 0 else 0

    Qt2 = 0
    xgt2 = 0
    if (qt1_2 != 0 or qt2_2 != 0) and l_triang_2 != 0:
        if abs(qt2_2) < eps and qt1_2 != 0:
            Qt2 = 0.5 * qt1_2 * l_triang_2
            xgt2 = x_triang_2 + (1/3) * l_triang_2
        elif abs(qt1_2) < eps and qt2_2 != 0:
            Qt2 = 0.5 * qt2_2 * l_triang_2
            xgt2 = x_triang_2 + (2/3) * l_triang_2
        else:
            Qt2 = 0.5 * (qt1_2 + qt2_2) * l_triang_2
            if abs(qt1_2 - qt2_2) < eps:
                xgt2 = x_triang_2 + l_triang_2 / 2
            else:
                xgt2 = x_triang_2 + (qt2_2 * l_triang_2**2 / 3 + qt1_2 * l_triang_2**2 / 6) / (0.5 * (qt1_2 + qt2_2) * l_triang_2)
        print(f"\nTRIANGULAR TRAMO 2: Qt2 = {Qt2:.6f} kN, xgt2 (desde B) = {xgt2:.6f} m")

    sum_M_B = M_BC + M_CB + Q2 * xg2 + P2 * x2 + Qt2 * xgt2
    Vcb = sum_M_B / L2
    print(f"\n--- Tramo 2 (B-C) ---")
    print(f"Vcb (cortante en C desde tramo 2): {Vcb:.3f} kN")
    Vbc = Q2 + P2 + Qt2 - Vcb
    print(f"Vbc (reacción en B, desde BC): {Vbc:.3f} kN")
    # Reacción total en B = Vba + Vbc
    RB = Vba + Vbc
    print(f"RB (total en B): {RB:.3f} kN")

    # ---------- TRAMO 3 (C-D) ----------
    if datos.get('n_tramos', 3) == 3 and datos['L3'] > 0:
        q3, q3_a, q3_l = datos['q3'], datos['q3_a'], datos['q3_l']
        P3, x3 = datos['P3'], datos['x3']
        qt1_3, qt2_3, l_triang_3, x_triang_3 = datos['qt1_3'], datos['qt2_3'], datos['l_triang_3'], datos['x_triang_3']
        M_CD, M_DC = momentos['M_CD'], momentos['M_DC']

        Q3 = q3 * q3_l if q3_l != 0 else 0
        xg3 = q3_a + q3_l / 2 if q3_l != 0 else 0

        Qt3 = 0
        xgt3 = 0
        if (qt1_3 != 0 or qt2_3 != 0) and l_triang_3 != 0:
            if abs(qt2_3) < eps and qt1_3 != 0:
                Qt3 = 0.5 * qt1_3 * l_triang_3
                xgt3 = x_triang_3 + (1/3) * l_triang_3
            elif abs(qt1_3) < eps and qt2_3 != 0:
                Qt3 = 0.5 * qt2_3 * l_triang_3
                xgt3 = x_triang_3 + (2/3) * l_triang_3
            else:
                Qt3 = 0.5 * (qt1_3 + qt2_3) * l_triang_3
                if abs(qt1_3 - qt2_3) < eps:
                    xgt3 = x_triang_3 + l_triang_3 / 2
                else:
                    xgt3 = x_triang_3 + (qt2_3 * l_triang_3**2 / 3 + qt1_3 * l_triang_3**2 / 6) / (0.5 * (qt1_3 + qt2_3) * l_triang_3)
            print(f"\nTRIANGULAR TRAMO 3: Qt3 = {Qt3:.6f} kN, xgt3 (desde C) = {xgt3:.6f} m")

        sum_M_C = M_CD + M_DC + Q3 * xg3 + P3 * x3 + Qt3 * xgt3
        Vdc = sum_M_C / datos['L3']
        print(f"\n--- Tramo 3 (C-D) ---")
        print(f"Vdc (cortante en D desde tramo 3): {Vdc:.3f} kN")
        Vcd = Q3 + P3 + Qt3 - Vdc
        print(f"Vcd (reacción en C, desde CD): {Vcd:.3f} kN")
        RC = Vcb + Vcd
        print(f"RC (total en C): {RC:.3f} kN")
        RD = Vdc
        print(f"RD (reacción en D): {RD:.3f} kN")
    else:
        RC = Vcb  # Solo la reacción desde el tramo 2
        RD = 0    # No hay apoyo D

    reacciones = {
        'RA': Vab,
        'RB': RB,
        'RC': RC,
        'RD': RD
    }
    return reacciones


# ======= FIN FUNCIONES CÁLCULO =======

def calcular_interfaz():
    try:
        n_tramos = int(combo_tramos.get())
        datos = {
            'n_tramos': n_tramos,
            'apoyo_izq': combo_apoyo_izq.get(),
            'apoyo_der': combo_apoyo_der.get(),
            'E': float(entry_E.get()),
            # Tramo 1
            'L1': float(entry_L1.get()),
            'I1': float(entry_I1.get()),
            'q1': float(entry_q1.get()),
            'q1_a': float(entry_q1_a.get()),
            'q1_l': float(entry_q1_l.get()),
            'P1': float(entry_P1.get()),
            'x1': float(entry_x1.get()),
            'qt1_1': float(entry_qt1_1.get()),
            'qt2_1': float(entry_qt2_1.get()),
            'l_triang_1': float(entry_ltr1.get()),
            'x_triang_1': float(entry_xtr1.get()),
            # Tramo 2
            'L2': float(entry_L2.get()),
            'I2': float(entry_I2.get()),
            'q2': float(entry_q2.get()),
            'q2_a': float(entry_q2_a.get()),
            'q2_l': float(entry_q2_l.get()),
            'P2': float(entry_P2.get()),
            'x2': float(entry_x2.get()),
            'qt1_2': float(entry_qt1_2.get()),
            'qt2_2': float(entry_qt2_2.get()),
            'l_triang_2': float(entry_ltr2.get()),
            'x_triang_2': float(entry_xtr2.get()),
            # Tramo 3 (si aplica)
            'L3': float(entry_L3.get()) if n_tramos == 3 else 0.0,
            'I3': float(entry_I3.get()) if n_tramos == 3 else 0.0,
            'q3': float(entry_q3.get()) if n_tramos == 3 else 0.0,
            'q3_a': float(entry_q3_a.get()) if n_tramos == 3 else 0.0,
            'q3_l': float(entry_q3_l.get()) if n_tramos == 3 else 0.0,
            'P3': float(entry_P3.get()) if n_tramos == 3 else 0.0,
            'x3': float(entry_x3.get()) if n_tramos == 3 else 0.0,
            'qt1_3': float(entry_qt1_3.get()) if n_tramos == 3 else 0.0,
            'qt2_3': float(entry_qt2_3.get()) if n_tramos == 3 else 0.0,
            'l_triang_3': float(entry_ltr3.get()) if n_tramos == 3 else 0.0,
            'x_triang_3': float(entry_xtr3.get()) if n_tramos == 3 else 0.0,
        }

        momentos_emp = calcular_momentos_emp(datos)
        res_momentos = momentos_finales(datos, momentos_emp) # res_momentos now directly contains M_AB, thetaA, etc.
        reacciones = calcular_reacciones(datos, res_momentos) # Pass res_momentos directly

        salida = ""
        salida += "Rotaciones (θ) en radianes:\n"
        
        # Iterate over theta results that exist
        theta_keys_to_display = ['thetaA', 'thetaB', 'thetaC']
        if n_tramos == 3 and datos['L3'] > 0:
            theta_keys_to_display.append('thetaD')

        for key in theta_keys_to_display:
            if key in res_momentos:
                salida += f"θ{key[-1]}: {res_momentos[key]:.4e}\n" # Extract 'A', 'B', 'C', 'D' from key

        salida += "\nMomentos finales (kNm):\n"
        
        # Iterate over moment results that exist
        moment_keys_to_display = ['M_AB', 'M_BA', 'M_BC', 'M_CB']
        if n_tramos == 3 and datos['L3'] > 0:
            moment_keys_to_display.extend(['M_CD', 'M_DC'])
        
        for key in moment_keys_to_display:
            if key in res_momentos:
                salida += f"{key}: {res_momentos[key]:.3f} kNm\n"
            
        salida += "\nReacciones en los apoyos (kN):\n"
        # Display reactions for RA, RB, RC, RD based on number of spans
        if n_tramos == 3 and datos['L3'] > 0:
            salida += f"RA: {reacciones['RA']:.3f} kN\n"
            salida += f"RB: {reacciones['RB']:.3f} kN\n"
            salida += f"RC: {reacciones['RC']:.3f} kN\n"
            salida += f"RD: {reacciones['RD']:.3f} kN\n"
        else: # 2 tramos
            salida += f"RA: {reacciones['RA']:.3f} kN\n"
            salida += f"RB: {reacciones['RB']:.3f} kN\n"
            salida += f"RC: {reacciones['RC']:.3f} kN\n" # RC for 2 tramos is the total reaction at C
            # No RD for 2 tramos, as it is implicitly 0 or not a support.

        text_result.delete("1.0", tk.END)
        text_result.insert(tk.END, salida)
    except Exception as e:
        messagebox.showerror("Error", f"Revisa los datos: {e}")

def mostrar_tramos(event):
    n_tramos = int(combo_tramos.get())
    if n_tramos == 3:
        frame_L3.grid(row=8, column=0, columnspan=2, pady=5, sticky="w")
        frame_Cargas3.grid(row=9, column=0, columnspan=2, pady=5, sticky="w")
    else:
        frame_L3.grid_forget()
        frame_Cargas3.grid_forget()

root = tk.Tk()
root.title("SLOPE DEFLECTION-BEAM SOLVER 1.0")
root.resizable(True, True) # Make window not resizable

# Styles for a more professional look
style = ttk.Style()
style.theme_use('clam') # 'clam', 'alt', 'default', 'classic'
style.configure('TFrame', background='#e0e0e0')
style.configure('TLabel', background='#e0e0e0', font=('Arial', 10))
style.configure('TButton', font=('Arial', 10, 'bold'), padding=5)
style.configure('TEntry', font=('Arial', 10))
style.configure('TCombobox', font=('Arial', 10))
style.configure('TLabelframe.Label', font=('Arial', 10, 'bold'))

mainframe = ttk.Frame(root, padding="15 15 15 15", relief='raised')
mainframe.grid(row=0, column=0, sticky="nsew")

# Global settings
ttk.Label(mainframe, text="Número de Tramos:").grid(row=0, column=0, sticky="w", pady=2)
combo_tramos = ttk.Combobox(mainframe, values=[2, 3], width=5, state="readonly")
combo_tramos.set(2)
combo_tramos.grid(row=0, column=1, sticky="w", pady=2)
combo_tramos.bind("<<ComboboxSelected>>", mostrar_tramos)

ttk.Label(mainframe, text="Tipo de Apoyo Izquierdo (A):").grid(row=1, column=0, sticky="w", pady=2)
combo_apoyo_izq = ttk.Combobox(mainframe, values=["EMP", "ART"], width=6, state="readonly")
combo_apoyo_izq.set("EMP")
combo_apoyo_izq.grid(row=1, column=1, sticky="w", pady=2)

ttk.Label(mainframe, text="Tipo de Apoyo Derecho (C o D):").grid(row=2, column=0, sticky="w", pady=2)
combo_apoyo_der = ttk.Combobox(mainframe, values=["EMP", "ART"], width=6, state="readonly")
combo_apoyo_der.set("EMP")
combo_apoyo_der.grid(row=2, column=1, sticky="w", pady=2)

ttk.Label(mainframe, text="Módulo de Elasticidad E (GPa):").grid(row=3, column=0, sticky="w", pady=5)
entry_E = ttk.Entry(mainframe, width=10)
entry_E.grid(row=3, column=1, sticky="w", pady=5)
entry_E.insert(0, "200") # Default E for steel

# Tramo 1
frame_L1 = ttk.LabelFrame(mainframe, text="Datos del Tramo 1 (AB)")
frame_L1.grid(row=4, column=0, columnspan=2, pady=5, sticky="ew", padx=5) # Use "ew" for expand/shrink with frame
ttk.Label(frame_L1, text="Longitud L1 (m):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
entry_L1 = ttk.Entry(frame_L1, width=7)
entry_L1.grid(row=0, column=1, sticky="w", pady=2)
entry_L1.insert(0, "5.0")
ttk.Label(frame_L1, text="Inercia I1 (cm⁴):").grid(row=0, column=2, sticky="w", padx=5, pady=2)
entry_I1 = ttk.Entry(frame_L1, width=7)
entry_I1.grid(row=0, column=3, sticky="w", pady=2)
entry_I1.insert(0, "10000")

frame_Cargas1 = ttk.LabelFrame(mainframe, text="Cargas Tramo 1")
frame_Cargas1.grid(row=5, column=0, columnspan=2, pady=5, sticky="ew", padx=5)
ttk.Label(frame_Cargas1, text="Carga Distribuida Uniforme (q1, kN/m):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
entry_q1 = ttk.Entry(frame_Cargas1, width=7)
entry_q1.grid(row=0, column=1, sticky="w", pady=2)
entry_q1.insert(0, "0.0")
ttk.Label(frame_Cargas1, text="Posición inicial q1_a (m):").grid(row=0, column=2, sticky="w", padx=5, pady=2)
entry_q1_a = ttk.Entry(frame_Cargas1, width=7)
entry_q1_a.grid(row=0, column=3, sticky="w", pady=2)
entry_q1_a.insert(0, "0.0")
ttk.Label(frame_Cargas1, text="Longitud q1_l (m):").grid(row=0, column=4, sticky="w", padx=5, pady=2)
entry_q1_l = ttk.Entry(frame_Cargas1, width=7)
entry_q1_l.grid(row=0, column=5, sticky="w", pady=2)
entry_q1_l.insert(0, "0.0")

ttk.Label(frame_Cargas1, text="Carga Puntual P1 (kN):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
entry_P1 = ttk.Entry(frame_Cargas1, width=7)
entry_P1.grid(row=1, column=1, sticky="w", pady=2)
entry_P1.insert(0, "0.0")
ttk.Label(frame_Cargas1, text="Posición x1 (m):").grid(row=1, column=2, sticky="w", padx=5, pady=2)
entry_x1 = ttk.Entry(frame_Cargas1, width=7)
entry_x1.grid(row=1, column=3, sticky="w", pady=2)
entry_x1.insert(0, "0.0")

ttk.Label(frame_Cargas1, text="Carga Triangular (qt1_1, kN/m):").grid(row=2, column=0, sticky="w", padx=5, pady=2)
entry_qt1_1 = ttk.Entry(frame_Cargas1, width=7)
entry_qt1_1.grid(row=2, column=1, sticky="w", pady=2)
entry_qt1_1.insert(0, "0.0")
ttk.Label(frame_Cargas1, text="qt2_1 (kN/m):").grid(row=2, column=2, sticky="w", padx=5, pady=2)
entry_qt2_1 = ttk.Entry(frame_Cargas1, width=7)
entry_qt2_1.grid(row=2, column=3, sticky="w", pady=2)
entry_qt2_1.insert(0, "0.0")
ttk.Label(frame_Cargas1, text="Longitud Triangular (l_triang_1, m):").grid(row=2, column=4, sticky="w", padx=5, pady=2)
entry_ltr1 = ttk.Entry(frame_Cargas1, width=7)
entry_ltr1.grid(row=2, column=5, sticky="w", pady=2)
entry_ltr1.insert(0, "0.0")
ttk.Label(frame_Cargas1, text="Posición inicial triangular (x_triang_1, m):").grid(row=2, column=6, sticky="w", padx=5, pady=2)
entry_xtr1 = ttk.Entry(frame_Cargas1, width=7)
entry_xtr1.grid(row=2, column=7, sticky="w", pady=2)
entry_xtr1.insert(0, "0.0")


# Tramo 2
frame_L2 = ttk.LabelFrame(mainframe, text="Datos del Tramo 2 (BC)")
frame_L2.grid(row=6, column=0, columnspan=2, pady=5, sticky="ew", padx=5)
ttk.Label(frame_L2, text="Longitud L2 (m):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
entry_L2 = ttk.Entry(frame_L2, width=7)
entry_L2.grid(row=0, column=1, sticky="w", pady=2)
entry_L2.insert(0, "5.0")
ttk.Label(frame_L2, text="Inercia I2 (cm⁴):").grid(row=0, column=2, sticky="w", padx=5, pady=2)
entry_I2 = ttk.Entry(frame_L2, width=7)
entry_I2.grid(row=0, column=3, sticky="w", pady=2)
entry_I2.insert(0, "10000")

frame_Cargas2 = ttk.LabelFrame(mainframe, text="Cargas Tramo 2")
frame_Cargas2.grid(row=7, column=0, columnspan=2, pady=5, sticky="ew", padx=5)
ttk.Label(frame_Cargas2, text="Carga Distribuida Uniforme (q2, kN/m):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
entry_q2 = ttk.Entry(frame_Cargas2, width=7)
entry_q2.grid(row=0, column=1, sticky="w", pady=2)
entry_q2.insert(0, "0.0")
ttk.Label(frame_Cargas2, text="Posición inicial q2_a (m):").grid(row=0, column=2, sticky="w", padx=5, pady=2)
entry_q2_a = ttk.Entry(frame_Cargas2, width=7)
entry_q2_a.grid(row=0, column=3, sticky="w", pady=2)
entry_q2_a.insert(0, "0.0")
ttk.Label(frame_Cargas2, text="Longitud q2_l (m):").grid(row=0, column=4, sticky="w", padx=5, pady=2)
entry_q2_l = ttk.Entry(frame_Cargas2, width=7)
entry_q2_l.grid(row=0, column=5, sticky="w", pady=2)
entry_q2_l.insert(0, "0.0")

ttk.Label(frame_Cargas2, text="Carga Puntual P2 (kN):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
entry_P2 = ttk.Entry(frame_Cargas2, width=7)
entry_P2.grid(row=1, column=1, sticky="w", pady=2)
entry_P2.insert(0, "0.0")
ttk.Label(frame_Cargas2, text="Posición x2 (m):").grid(row=1, column=2, sticky="w", padx=5, pady=2)
entry_x2 = ttk.Entry(frame_Cargas2, width=7)
entry_x2.grid(row=1, column=3, sticky="w", pady=2)
entry_x2.insert(0, "0.0")

ttk.Label(frame_Cargas2, text="Carga Triangular (qt1_2, kN/m):").grid(row=2, column=0, sticky="w", padx=5, pady=2)
entry_qt1_2 = ttk.Entry(frame_Cargas2, width=7)
entry_qt1_2.grid(row=2, column=1, sticky="w", pady=2)
entry_qt1_2.insert(0, "0.0")
ttk.Label(frame_Cargas2, text="qt2_2 (kN/m):").grid(row=2, column=2, sticky="w", padx=5, pady=2)
entry_qt2_2 = ttk.Entry(frame_Cargas2, width=7)
entry_qt2_2.grid(row=2, column=3, sticky="w", pady=2)
entry_qt2_2.insert(0, "0.0")
ttk.Label(frame_Cargas2, text="Longitud Triangular (l_triang_2, m):").grid(row=2, column=4, sticky="w", padx=5, pady=2)
entry_ltr2 = ttk.Entry(frame_Cargas2, width=7)
entry_ltr2.grid(row=2, column=5, sticky="w", pady=2)
entry_ltr2.insert(0, "0.0")
ttk.Label(frame_Cargas2, text="Posición inicial triangular (x_triang_2, m):").grid(row=2, column=6, sticky="w", padx=5, pady=2)
entry_xtr2 = ttk.Entry(frame_Cargas2, width=7)
entry_xtr2.grid(row=2, column=7, sticky="w", pady=2)
entry_xtr2.insert(0, "0.0")

# Tramo 3 (hidden by default)
frame_L3 = ttk.LabelFrame(mainframe, text="Datos del Tramo 3 (CD)")
# frame_L3.grid() will be called by mostrar_tramos
ttk.Label(frame_L3, text="Longitud L3 (m):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
entry_L3 = ttk.Entry(frame_L3, width=7)
entry_L3.grid(row=0, column=1, sticky="w", pady=2)
entry_L3.insert(0, "0.0")
ttk.Label(frame_L3, text="Inercia I3 (cm⁴):").grid(row=0, column=2, sticky="w", padx=5, pady=2)
entry_I3 = ttk.Entry(frame_L3, width=7)
entry_I3.grid(row=0, column=3, sticky="w", pady=2)
entry_I3.insert(0, "0.0")

frame_Cargas3 = ttk.LabelFrame(mainframe, text="Cargas Tramo 3")
# frame_Cargas3.grid() will be called by mostrar_tramos
ttk.Label(frame_Cargas3, text="Carga Distribuida Uniforme (q3, kN/m):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
entry_q3 = ttk.Entry(frame_Cargas3, width=7)
entry_q3.grid(row=0, column=1, sticky="w", pady=2)
entry_q3.insert(0, "0.0")
ttk.Label(frame_Cargas3, text="Posición inicial q3_a (m):").grid(row=0, column=2, sticky="w", padx=5, pady=2)
entry_q3_a = ttk.Entry(frame_Cargas3, width=7)
entry_q3_a.grid(row=0, column=3, sticky="w", pady=2)
entry_q3_a.insert(0, "0.0")
ttk.Label(frame_Cargas3, text="Longitud q3_l (m):").grid(row=0, column=4, sticky="w", padx=5, pady=2)
entry_q3_l = ttk.Entry(frame_Cargas3, width=7)
entry_q3_l.grid(row=0, column=5, sticky="w", pady=2)
entry_q3_l.insert(0, "0.0")

ttk.Label(frame_Cargas3, text="Carga Puntual P3 (kN):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
entry_P3 = ttk.Entry(frame_Cargas3, width=7)
entry_P3.grid(row=1, column=1, sticky="w", pady=2)
entry_P3.insert(0, "0.0")
ttk.Label(frame_Cargas3, text="Posición x3 (m):").grid(row=1, column=2, sticky="w", padx=5, pady=2)
entry_x3 = ttk.Entry(frame_Cargas3, width=7)
entry_x3.grid(row=1, column=3, sticky="w", pady=2)
entry_x3.insert(0, "0.0")

ttk.Label(frame_Cargas3, text="Carga Triangular (qt1_3, kN/m):").grid(row=2, column=0, sticky="w", padx=5, pady=2)
entry_qt1_3 = ttk.Entry(frame_Cargas3, width=7)
entry_qt1_3.grid(row=2, column=1, sticky="w", pady=2)
entry_qt1_3.insert(0, "0.0")
ttk.Label(frame_Cargas3, text="qt2_3 (kN/m):").grid(row=2, column=2, sticky="w", padx=5, pady=2)
entry_qt2_3 = ttk.Entry(frame_Cargas3, width=7)
entry_qt2_3.grid(row=2, column=3, sticky="w", pady=2)
entry_qt2_3.insert(0, "0.0")
ttk.Label(frame_Cargas3, text="Longitud Triangular (l_triang_3, m):").grid(row=2, column=4, sticky="w", padx=5, pady=2)
entry_ltr3 = ttk.Entry(frame_Cargas3, width=7)
entry_ltr3.grid(row=2, column=5, sticky="w", pady=2)
entry_ltr3.insert(0, "0.0")
ttk.Label(frame_Cargas3, text="Posición inicial triangular (x_triang_3, m):").grid(row=2, column=6, sticky="w", padx=5, pady=2)
entry_xtr3 = ttk.Entry(frame_Cargas3, width=7)
entry_xtr3.grid(row=2, column=7, sticky="w", pady=2)
entry_xtr3.insert(0, "0.0")


btn_calc = ttk.Button(mainframe, text="Calcular Resultados", command=calcular_interfaz)
btn_calc.grid(row=10, column=0, columnspan=2, pady=15) # Adjusted row number for button

text_result = tk.Text(mainframe, width=80, height=15, wrap="word", font=('Consolas', 10),
                      relief='sunken', borderwidth=2)
text_result.grid(row=11, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

# Configure row and column weights so they expand nicely
mainframe.columnconfigure(0, weight=1)
mainframe.columnconfigure(1, weight=1)
mainframe.rowconfigure(11, weight=1) # Make the text result expand vertically

# Initial call to set visibility based on default combo_tramos value
mostrar_tramos(None) 

root.mainloop()