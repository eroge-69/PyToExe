import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import root_scalar

def func1(m, sigy, epsy, sigu):
    """
    Auxiliary function used to solve for m in the Johnson-Cook parameter estimation.

    Parameters
    ----------
    m : float
        Intermediate parameter.
    sigy : float
        Yield strength [MPa].
    epsy : float
        Yield strain.
    sigu : float
        Ultimate tensile strength [MPa].

    Returns
    -------
    float
        Result of the nonlinear equation for solving m.
    """
    return sigy * (1.0 + epsy) - sigu * np.exp(m) * ((np.log(1.0 + epsy) / m) ** m)

def func2(n, m, sigy, epsy, sigu, ymod):
    """
    Auxiliary function used to solve for n in the Johnson-Cook parameter estimation.

    Parameters
    ----------
    n : float
        Strain hardening exponent.
    m : float
        Intermediate parameter.
    sigy : float
        Yield strength [MPa].
    epsy : float
        Yield strain.
    sigu : float
        Ultimate tensile strength [MPa].
    ymod : float
        Young's modulus [MPa].

    Returns
    -------
    float
        Result of the nonlinear equation for solving n.
    """
    term1 = sigu * np.exp(m)
    term2 = sigy * (1.0 + epsy)
    term3 = (np.power(m - sigu * np.exp(m) / ymod, n) -
             np.power(np.log(1.0 + epsy) - sigy * (1.0 + epsy) / ymod, n))
    denom = (n * np.power(m - sigu * np.exp(m) / ymod, n - 1.0) *
             (np.exp(-m) - sigu / ymod))
    return term1 - term2 - sigu * term3 / denom

def calcular_coeficientes(ymod, sigy, sigu, offset):
    """
    Calculate Johnson-Cook material model parameters A, B, n.

    Parameters
    ----------
    ymod : float
        Young's modulus [MPa].
    sigy : float
        Yield strength [MPa].
    sigu : float
        Ultimate tensile strength [MPa].
    offset : float
        Offset strain (e.g., 0.002 for 0.2%).

    Returns
    -------
    A : float
        Johnson-Cook parameter A [MPa].
    B : float
        Johnson-Cook parameter B [MPa].
    n : float
        Johnson-Cook strain hardening exponent.
    epsu : float
        Ultimate true strain.
    """
    epsy = offset + sigy / ymod

    sol_m = root_scalar(lambda m: func1(m, sigy, epsy, sigu), bracket=[0.01, 1.0], method='brentq')
    m = sol_m.root
    epsu = np.exp(m) - 1.0

    sol_n = root_scalar(lambda n: func2(n, m, sigy, epsy, sigu, ymod), bracket=[0.01, 1.0], method='brentq')
    n = sol_n.root

    term_b = (np.log(1.0 + epsu) - sigu * (1.0 + epsu) / ymod)
    if term_b <= 0:
        raise ValueError("Invalid value for logarithm in B calculation.")
    B = sigu / (n * (term_b ** (n - 1.0)) * (1.0 / (1.0 + epsu) - sigu / ymod))
    A = sigy * (1.0 + epsy) - B * (np.log(1.0 + epsy) - sigy * (1.0 + epsy) / ymod) ** n

    return A, B, n, epsu

def plotar_JC(material, A, B, n, sigy, sigu, ymod, offset, epsu, save=False):
    """
    Plot the true and engineering stress–strain curves using the Johnson-Cook model.

    This function generates a plot comparing the engineering and true stress–strain
    responses of a material described by the Johnson-Cook model. It uses the model
    parameters A, B, n to calculate the true stress from transformed strain values,
    and derives the engineering stress accordingly. The yield and ultimate strengths
    are displayed as horizontal reference lines with annotations, and the final point
    of the true curve is marked with a labeled crosshair.

    Parameters
    ----------
    material : str
        Material name.
    A : float
        Johnson-Cook parameter A [MPa].
    B : float
        Johnson-Cook parameter B [MPa].
    n : float
        Johnson-Cook strain hardening exponent.
    sigy : float
        Yield strength [MPa].
    sigu : float
        Ultimate tensile strength [MPa].
    ymod : float
        Young's modulus [MPa].
    offset : float
        Yield offset strain (e.g., 0.002 for 0.2% offset).
    epsu : float
        True strain at rupture (maximum true strain).
    save : bool, optional
        If True, saves the plot as a SVG file without displaying it.
    
    Returns
    -------
    strains_eng : ndarray
        Array of engineering strain values.
    stresses_eng : ndarray
        Array of engineering stress values computed from the Johnson-Cook true stress.
    """
    import numpy as np
    import matplotlib.pyplot as plt

    strains_eng_full = np.linspace(0, epsu, 1000)
    log_valid = np.log(1 + strains_eng_full) - sigy * (1 + strains_eng_full) / ymod

    mask_valid = log_valid > 0
    strains_eng_valid = strains_eng_full[mask_valid]
    log_valid_valid = log_valid[mask_valid]

    stresses_true_valid = A + B * np.power(log_valid_valid, n)
    stresses_eng_valid = stresses_true_valid / (1 + strains_eng_valid)
    strains_true_valid = np.log(1 + strains_eng_valid)

    strains_eng = np.insert(strains_eng_valid, 0, 0.0)
    stresses_eng = np.insert(stresses_eng_valid, 0, 0.0)
    strains_true = np.insert(strains_true_valid, 0, 0.0)
    stresses_true = np.insert(stresses_true_valid, 0, 0.0)

    strain_u = strains_true[-1]
    stress_u = stresses_true[-1]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(strains_eng, stresses_eng, 'k--', linewidth=1.2, label='Engineering Stress–Strain')
    ax.plot(strains_true, stresses_true, 'k-', linewidth=1.5, label='True Stress–Strain')

    ax.axhline(y=sigy, color='gray', linestyle='--', linewidth=1, label='Yield Strength')
    ax.axhline(y=sigu, color='gray', linestyle=':', linewidth=1, label='Ultimate Strength')
    ax.text(epsu * 0.99, sigy + 5, f'{sigy:.1f} MPa', ha='right', va='bottom', fontsize=9, color='gray')
    ax.text(epsu * 0.99, sigu + 5, f'{sigu:.1f} MPa', ha='right', va='bottom', fontsize=9, color='gray')

    ax.axvline(x=strain_u, color='black', linestyle=':', linewidth=1)
    ax.axhline(y=stress_u, color='black', linestyle=':', linewidth=1)
    ax.text(strain_u - 0.015, stress_u, f"εu = {strain_u:.4f}\nσu = {stress_u:.1f} MPa",
            va='center', ha='left', fontsize=9,
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="gray", lw=0.5))

    ax.set_title(f'Material: {material} (Johnson-Cook Model)', fontsize=12)
    ax.set_xlabel('Strain')
    ax.set_ylabel('Stress [MPa]')
    ax.grid(True, which='both', linestyle='-', linewidth=0.5, color='lightgray')
    ax.legend(loc='upper left')
    fig.tight_layout()

    if save:
        fig.savefig(f"{material.replace(' ', '_')}_JC.svg")
        plt.close(fig)
    else:
        plt.show()

    return strains_eng, stresses_eng

def plotar_tabular(material, sigy, sigu, ymod, offset, epsu, npts=300, save=False):
    """
    Plot the true and engineering stress–strain curves using a power-law 
    approximation derived from tabular input data.

    Parameters
    ----------
    material : str
        Material name.
    sigy : float
        Yield strength [MPa].
    sigu : float
        Ultimate strength [MPa].
    ymod : float
        Young's modulus [MPa].
    offset : float
        Yield offset strain (e.g., 0.002 for 0.2%).
    epsu : float
        True strain at rupture (maximum true strain).
    npts : int, optional
        Number of strain points to generate. Default is 300.
    save : bool, optional
        If True, saves the plot as a SVG file without displaying it.
    """
    eps_yield = offset + sigy / ymod
    eps_rupt = epsu
    eps_yield_pl = eps_yield - sigy / ymod
    eps_rupt_pl = eps_rupt - sigu / ymod

    n = (np.log10(sigu) - np.log10(sigy)) / (np.log10(eps_rupt_pl) - np.log10(eps_yield_pl))
    logK = np.log10(sigu) - n * np.log10(eps_rupt_pl)
    K = 10 ** logK

    sigma_nom = np.linspace(sigy, sigu, npts - 1)
    strain_nom = sigma_nom / ymod + (sigma_nom / K) ** (1 / n)
    strain_true = np.log(1 + strain_nom)
    stress_true = sigma_nom * (1 + strain_nom)
    stress_eng = sigma_nom

    strain_nom = np.insert(strain_nom, 0, 0.0)
    strain_true = np.insert(strain_true, 0, 0.0)
    stress_true = np.insert(stress_true, 0, 0.0)
    stress_eng = np.insert(stress_eng, 0, 0.0)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(strain_nom, stress_eng, 'k--', linewidth=1.2, label='Engineering Stress–Strain')
    ax.plot(strain_true, stress_true, 'k-', linewidth=1.5, label='True Stress–Strain')

    ax.axhline(y=sigy, color='gray', linestyle='--', linewidth=1, label='Yield Strength')
    ax.axhline(y=sigu, color='gray', linestyle=':', linewidth=1, label='Ultimate Strength')
    ax.text(epsu * 0.99, sigy + 5, f'{sigy:.1f} MPa', ha='right', va='bottom', fontsize=9, color='gray')
    ax.text(epsu * 0.99, sigu + 5, f'{sigu:.1f} MPa', ha='right', va='bottom', fontsize=9, color='gray')

    strain_u = strain_true[-1]
    stress_u = stress_true[-1]
    ax.axvline(x=strain_u, color='black', linestyle=':', linewidth=1)
    ax.axhline(y=stress_u, color='black', linestyle=':', linewidth=1)
    ax.text(strain_u - 0.015, stress_u, f"εu = {strain_u:.4f}\nσu = {stress_u:.1f} MPa",
            va='center', ha='left', fontsize=9,
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="gray", lw=0.5))

    ax.set_title(f'Material: {material} (Tabular Approximation)', fontsize=12)
    ax.set_xlabel('Strain')
    ax.set_ylabel('Stress [MPa]')
    ax.grid(True, which='both', linestyle='-', linewidth=0.5, color='lightgray')
    ax.legend(loc='upper left')
    fig.tight_layout()

    if save:
        fig.savefig(f"{material.replace(' ', '_')}_TABULAR.svg")
        plt.close(fig)
    else:
        plt.show()

def exportar_inp_jc(nome, material, density, ymod, nu, A, B, n):
    """
    Export material model to Abaqus .inp format using Johnson-Cook formulation.

    Parameters
    ----------
    nome : str
        Output file name.
    material : str
        Material name.
    density : float
        Density [tonn/mm³].
    ymod : float
        Young's modulus [MPa].
    nu : float
        Poisson's ratio.
    A : float
        Johnson-Cook A parameter [MPa].
    B : float
        Johnson-Cook B parameter [MPa].
    n : float
        Johnson-Cook n parameter.
    """
    with open(f"{nome}.inp", "w") as f:
        f.write(f"*MATERIAL, NAME={material}\n")
        f.write("*DENSITY\n")
        f.write(f"  {density},\n")
        f.write("*ELASTIC\n")
        f.write(f"  {ymod}, {nu}\n")
        f.write("*PLASTIC, HARDENING=JOHNSON COOK\n")
        f.write(f"  {A:.10f}, {B:.10f}, {n:.10f}, 0., 0., 0.\n")

def exportar_inp_tabular(nome, material, density, ymod, nu, sigy, sigu, offset, epsu, npts=15):
    """
    Export material model to Abaqus .inp format using tabular stress–strain data.

    Parameters
    ----------
    nome : str
        Output file name.
    material : str
        Material name.
    density : float
        Density [tonn/mm³].
    ymod : float
        Young's modulus [MPa].
    nu : float
        Poisson's ratio.
    sigy : float
        Yield strength [MPa].
    sigu : float
        Ultimate strength [MPa].
    offset : float
        Offset strain.
    epsu : float
        Strain at rupture.
    npts : int, optional
        Number of tabular points, by default 15.
    """
    eps_yield = offset + sigy / ymod
    eps_rupt = epsu
    eps_yield_pl = eps_yield - sigy / ymod
    eps_rupt_pl = eps_rupt - sigu / ymod
    n = (np.log10(sigu) - np.log10(sigy)) / (np.log10(eps_rupt_pl) - np.log10(eps_yield_pl))
    logK = np.log10(sigu) - n * np.log10(eps_rupt_pl)
    K = 10 ** logK

    sigma_nom = np.linspace(sigy, sigu, npts - 1)
    strain_nom = sigma_nom / ymod + (sigma_nom / K) ** (1 / n)
    strain_true = np.log(1 + strain_nom)
    stress_true = sigma_nom * (1 + strain_nom)
    strain_plastic = strain_true - (stress_true / ymod)

    # First special point: extrapolated stress at strain = sigy / E
    strain_true_first = sigy / ymod
    strain_plastic_first = 0.0
    s1, s2 = stress_true[0], stress_true[1]
    e1, e2 = strain_true[0], strain_true[1]
    stress_true_first = s1 - ((s2 - s1) / (e2 - e1)) * (e1 - strain_true_first)

    stress_true = np.insert(stress_true, 0, stress_true_first)
    strain_plastic = np.insert(strain_plastic, 0, strain_plastic_first)

    with open(f"{nome}.inp", "w") as f:
        f.write(f"*MATERIAL, NAME={material}\n")
        f.write("*DENSITY\n")
        f.write(f"  {density},\n")
        f.write("*ELASTIC\n")
        f.write(f"  {ymod}, {nu}\n")
        f.write("*PLASTIC\n")
        for s, e in zip(stress_true, strain_plastic):
            f.write(f"  {s:.10f}, {e:.10f}\n")

def run_batch_mode():
    """
    Executes batch processing of materials using input from 'material_data.csv'.
    Automatically generates .inp material cards and SVG plots for each entry.

    Returns
    -------
    success : bool
        True if batch mode was executed, False otherwise.
    """
    filename = "material_data.csv"
    if not os.path.isfile(filename):
        print("\n[ERROR] File 'material_data.csv' not found in current directory.")
        print("Please ensure the CSV file is placed alongside this script.")
        return False

    try:
        df = pd.read_csv(filename, sep=";")
        required_columns = [
            "Materialname", "E", "Sy", "Su", "offset",
            "epsolon_u", "poisson", "density"
        ]
        if not all(col in df.columns for col in required_columns):
            raise ValueError("Missing one or more required columns in CSV file.")
    except Exception as e:
        print(f"\n[ERROR] Failed to read 'material_data.csv': {e}")
        print("Ensure the file is properly formatted with the expected columns.")
        return False

    print(f"\nFound {len(df)} materials in 'material_data.csv'.")
    confirm = input("Proceed with batch generation of material cards and plots? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Batch mode cancelled.")
        return False

    for idx, row in df.iterrows():
        try:
            material = str(row["Materialname"])
            ymod = float(row["E"])
            sigy = float(row["Sy"])
            sigu = float(row["Su"])
            offset = float(row["offset"])
            epsu = float(row["epsolon_u"])
            nu = float(row["poisson"])
            density = float(row["density"])

            A, B, n, epsu_computed = calcular_coeficientes(ymod, sigy, sigu, offset)

            filename_jc = material.replace(" ", "_") + "_JC"
            filename_tab = material.replace(" ", "_") + "_TABULAR"
            exportar_inp_jc(filename_jc, material, density, ymod, nu, A, B, n)
            exportar_inp_tabular(filename_tab, material, density, ymod, nu, sigy, sigu, offset, epsu)

            plotar_JC(material, A, B, n, sigy, sigu, ymod, offset, epsu, save=True)
            plotar_tabular(material, sigy, sigu, ymod, offset, epsu, save=True)

            print(f"[{idx + 1}/{len(df)}] Material '{material}' processed successfully.")
        except Exception as e:
            print(f"[ERROR] Failed to process material at row {idx + 1}: {e}")

    print("\nBatch processing completed.")
    return True

def main():
    while True:
        print("\n--- Material Model Input ---")
        material = input("Material name: ").strip()
        ymod = float(input("Young's modulus [MPa]: "))
        sigy = float(input("Yield strength [MPa]: "))
        sigu = float(input("Ultimate strength [MPa]: "))
        offset = float(input("Offset strain (e.g., 0.002 for 0.2%): "))
        epsu = float(input("Strain at rupture (e.g., 0.2 for 20%): "))
        nu = float(input("Poisson's ratio: "))
        density = float(input("Density [tonn/mm³] (e.g., 7.85e-9): "))

        try:
            A, B, n, epsu_computed = calcular_coeficientes(ymod, sigy, sigu, offset)
        except Exception as e:
            print(f"Error in calculations: {e}")
            continue

        # Display Johnson-Cook results
        print(f"\nJohnson-Cook parameters for {material}:")
        print(f"A = {A:.6f} MPa")
        print(f"B = {B:.6f} MPa")
        print(f"n = {n:.10f}")

        # Compute and display tabular parameters
        eps_yield = offset + sigy / ymod
        eps_yield_pl = eps_yield - sigy / ymod
        eps_rupt_pl = epsu - sigu / ymod
        n_tabular = (np.log10(sigu) - np.log10(sigy)) / (np.log10(eps_rupt_pl) - np.log10(eps_yield_pl))
        logK = np.log10(sigu) - n_tabular * np.log10(eps_rupt_pl)
        K_tabular = 10 ** logK

        print(f"\nTabular model approximation:")
        print(f"n (power law exponent) = {n_tabular:.6f}")
        print(f"K (strength coefficient) = {K_tabular:.2f} MPa")

        # Ask to show plots
        view = input("\nDo you want to display the stress–strain plots? (y/n): ").strip().lower()
        if view == 'y':
            plotar_JC(material, A, B, n, sigy, sigu, ymod, offset, epsu)
            plotar_tabular(material, sigy, sigu, ymod, offset, epsu)

        # Export material cards
        export = input("\nDo you want to export the material cards (.inp)? (y/n): ").strip().lower()
        if export == 'y':
            filename_jc = material.replace(" ", "_") + "_JC"
            filename_tab = material.replace(" ", "_") + "_TABULAR"
            exportar_inp_jc(filename_jc, material, density, ymod, nu, A, B, n)
            exportar_inp_tabular(filename_tab, material, density, ymod, nu, sigy, sigu, offset, epsu)
            print("Both Johnson-Cook and Tabular material cards exported successfully.")

        # Export plots
        save_plots = input("\nDo you want to save the plots as SVG? (y/n): ").strip().lower()
        if save_plots == 'y':
            plotar_JC(material, A, B, n, sigy, sigu, ymod, offset, epsu, save=True)
            plotar_tabular(material, sigy, sigu, ymod, offset, epsu, save=True)
            print("Plots saved successfully.")

        cont = input("\nDo you want to enter another material? (y/n): ").strip().lower()
        if cont != 'y':
            print("Exiting.")
            break

if __name__ == "__main__":
    print("Select execution mode:")
    print("1 - Interactive (manual input)")
    print("2 - Batch (from material_data.csv)")
    mode = input("Enter 1 or 2: ").strip()

    if mode == '2':
        success = run_batch_mode()
        if not success:
            print("\nReturning to interactive mode...\n")
            main()
    else:
        main()
