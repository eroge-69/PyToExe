
import numpy as np
import matplotlib.pyplot as plt

def simulate_entanglement_fidelity(device_dimensions, temperatures, F0=1.0, C=1e-15, gamma=1.07e-4):
    """
    Simulates entanglement fidelity based on device dimension and temperature.

    Args:
        device_dimensions (list): List of device dimensions in meters.
        temperatures (list): List of temperatures in Kelvin.
        F0 (float): Zero-temperature fidelity.
        C (float): Material-dependent constant.
        gamma (float): Decoherence rate.

    Returns:
        tuple: A tuple containing:
            - fidelity_vs_dimension (dict): Fidelity for each device dimension at a fixed temperature (e.g., 300K).
            - fidelity_vs_temperature (dict): Fidelity for each temperature at a fixed device dimension (e.g., 350nm).
    """
    fidelity_vs_dimension = {}
    fixed_temp = 300 # K
    for d in device_dimensions:
        fidelity = F0 - (C / (d**2)) - (gamma * fixed_temp)
        fidelity_vs_dimension[d] = max(0, fidelity) # Fidelity cannot be negative

    fidelity_vs_temperature = {}
    fixed_dimension = 350e-9 # meters (350 nm)
    for T in temperatures:
        fidelity = F0 - (C / (fixed_dimension**2)) - (gamma * T)
        fidelity_vs_temperature[T] = max(0, fidelity)

    return fidelity_vs_dimension, fidelity_vs_temperature

if __name__ == "__main__":
    # Example usage based on the research paper values
    dimensions_nm = [350, 400, 450, 500]
    dimensions_m = [d * 1e-9 for d in dimensions_nm]
    temperatures_k = list(range(4, 301, 10)) # From 4K to 300K

    fidelity_dim, fidelity_temp = simulate_entanglement_fidelity(dimensions_m, temperatures_k)

    print("\nEntanglement Fidelity vs. Device Dimension (at 300K):")
    for d, f in fidelity_dim.items():
        print(f"Dimension: {d*1e9:.0f} nm, Fidelity: {f*100:.2f}%")

    print("\nEntanglement Fidelity vs. Temperature (at 350nm):")
    for T, f in fidelity_temp.items():
        print(f"Temperature: {T} K, Fidelity: {f*100:.2f}%")

    # Plotting results
    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.plot([d*1e9 for d in fidelity_dim.keys()], [f*100 for f in fidelity_dim.values()], 
             marker='o', linestyle='-', color='blue')
    plt.title('Simulated Entanglement Fidelity vs. Device Dimension')
    plt.xlabel('Device Dimension (nm)')
    plt.ylabel('Entanglement Fidelity (%)')
    plt.grid(True)

    plt.subplot(1, 2, 2)
    plt.plot(list(fidelity_temp.keys()), [f*100 for f in fidelity_temp.values()], 
             marker='o', linestyle='-', color='red')
    plt.title('Simulated Entanglement Fidelity vs. Temperature')
    plt.xlabel('Temperature (K)')
    plt.ylabel('Entanglement Fidelity (%)')
    plt.grid(True)

    plt.tight_layout()
    plt.savefig('/home/ubuntu/quantum_project/entanglement_simulation_results.png')
    plt.close()

    print("\nSimulation results plotted and saved to entanglement_simulation_results.png")


