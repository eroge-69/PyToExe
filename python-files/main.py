import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')

# ----------- Thermodynamic Processes -----------
def isothermal_process(n, T, V_start, V_end, R=8.314):
    V = np.linspace(V_start, V_end, 100)
    return V, (n * R * T) / V

def isochoric_process(n, V, T_start, T_end, R=8.314):
    T = np.linspace(T_start, T_end, 100)
    return T, (n * R * T) / V

def isobaric_process(n, P, V_start, V_end, R=8.314):
    V = np.linspace(V_start, V_end, 100)
    return V, (P * V) / (n * R)

def adiabatic_process(n, T_start, V_start, V_end, gamma=1.4, R=8.314):
    V = np.linspace(V_start, V_end, 100)
    T = T_start * (V_start / V) ** (gamma - 1)
    return V, (n * R * T) / V

# ----------- Plotting Function -----------
def plot_process(x, y, xlabel, ylabel, title):
    fig, ax = plt.subplots()
    line, = ax.plot(x, y, label=title)
    ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    ax.legend()
    ax.grid(True)
    annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)
    def update_annot(ind):
        idx = ind["ind"][0]
        annot.xy = (x[idx], y[idx])
        annot.set_text(f"{xlabel}={x[idx]:.3f}\n{ylabel}={y[idx]:.3f}")
        annot.get_bbox_patch().set_alpha(0.8)
    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            cont, ind = line.contains(event)
            if cont:
                update_annot(ind)
                annot.set_visible(True)
                fig.canvas.draw_idle()
            elif vis:
                annot.set_visible(False)
                fig.canvas.draw_idle()
    fig.canvas.mpl_connect("motion_notify_event", hover)
    plt.show()

# ----------- Main Program -----------
def main():
    processes = {
        '1': (isothermal_process, ["n (moles)", "T (K)", "V_start (m^3)", "V_end (m^3)"], "Volume (m³)", "Pressure (Pa)", "Isothermal Process"),
        '2': (isochoric_process, ["n (moles)", "V (m^3)", "T_start (K)", "T_end (K)"], "Temperature (K)", "Pressure (Pa)", "Isochoric Process"),
        '3': (isobaric_process, ["n (moles)", "P (Pa)", "V_start (m^3)", "V_end (m^3)"], "Volume (m³)", "Temperature (K)", "Isobaric Process"),
        '4': (adiabatic_process, ["n (moles)", "T_start (K)", "V_start (m^3)", "V_end (m^3)", "gamma (Cp/Cv)"], "Volume (m³)", "Pressure (Pa)", "Adiabatic Process")
    }
    print("----------------------------------            Project By -")
    print("|  Thermodynamic Process Plotter |            Justin  | Sarvesh | Anvita  | Tanish")
    print("----------------------------------            2024101 | 2024102 | 2024103 | 2024104")
    print("Select process:")
    for k, v in processes.items():
        print(f"{k}. {v[4]}")
    choice = input("Enter choice (1-4): ")
    if choice in processes:
        func, prompts, xlabel, ylabel, title = processes[choice][:5]
        args = []
        for p in prompts:
            while True:
                try:
                    val = float(input(f"Enter {p}: "))
                    args.append(val)
                    break
                except ValueError:
                    print(f"Invalid value for {p}. Please enter a number.")
        x, y = func(*args)
        plot_process(x, y, xlabel, ylabel, title)
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()
