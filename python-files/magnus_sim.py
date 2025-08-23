import numpy as np
from scipy.integrate import odeint
import sys
import os

def get_limited_input(prompt, min_val, max_val):
    while True:
        try:
            val = float(input(f"{prompt} ({min_val} to {max_val}): "))
            if min_val <= val <= max_val:
                return val
            else:
                print(f"Value must be between {min_val} and {max_val}.")
        except ValueError:
            print("Please enter a valid number.")
g    = 14.43
rho  = 0.45929
r    = 0.11
A    = np.pi * r**2
m    = 0.43
Cd   = 0.47
K = 0.03361
v_wind = 4.733
cw=0.016

def deriv(y, t):
    x, y_pos, vx, vy, omega = y

    vx_rel = vx - v_wind
    vy_rel = vy
    v_rel = np.hypot(vx_rel, vy_rel)

    if v_rel == 0:
        return [vx, vy, 0, -g, 0]

    v_hat = np.array([vx_rel, vy_rel]) / v_rel
    Fd = 0.5 * rho * Cd * A * v_rel**2
    a_drag = -Fd / m * v_hat

    Fm_mag = K * (omega * r) * v_rel
    perp = np.array([-v_hat[1], v_hat[0]])
    a_mag = (Fm_mag / m) * perp

    ax = a_drag[0] + a_mag[0]
    ay = -g + a_drag[1] + a_mag[1]
    domega_dt = -cw * np.abs(omega) * v_rel

    return [vx, vy, ax, ay, domega_dt]


while True:
    v0 = get_limited_input("Enter initial speed in m/s", 5, 40)+ np.random.normal(0, 0.5)
    angle = float(input("Enter launch angle (degrees): "))+ np.random.normal(0, 0.5)
    omega = get_limited_input("Enter angular speed in rad/s", -400, 400)+np.random.normal(0, 1)
    output_name=input("Name for the output file: ")
    vx0 = v0 * np.cos(np.radians(angle))
    vy0 = v0 * np.sin(np.radians(angle))
    y0 = [0, 0, vx0, vy0, omega]


    t = np.linspace(0, 10, 1000) 
    sol = odeint(deriv, y0, t)
    x_vals = sol[:, 0]
    y_vals = sol[:, 1]

    ground_indices = np.where(y_vals < 0)[0]
    if len(ground_indices) > 0:
        impact_index = ground_indices[0]
        x_vals = x_vals[:impact_index + 1]
        y_vals = y_vals[:impact_index + 1]
        t = t[:impact_index + 1]

    max_height = np.max(y_vals)

    plot_interval = 0.0316
    indices_to_plot = np.arange(0, len(t), int(plot_interval / (t[1] - t[0])))
    
    x_plot = x_vals[indices_to_plot]
    y_plot = y_vals[indices_to_plot]
    if indices_to_plot[-1] != len(t) - 1:
        x_plot = np.append(x_plot, x_vals[-1])
        y_plot = np.append(y_plot, y_vals[-1]) 
    noise = np.random.normal(0, 0.1, size=x_plot.shape)
    data = np.column_stack((x_plot, y_plot))

    base_path = os.path.dirname(sys.executable)
    file_path = os.path.join(base_path, output_name)
    np.savetxt(file_path, data, delimiter=",", header="x,y", comments='', fmt="%.2f")
    print(f"File saved at: {os.path.abspath(file_path)}")

    again = input("Run another simulation? (y/n): ").strip().lower()
    if again != 'y':
        break

