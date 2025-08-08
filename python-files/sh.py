import math

# Define standard wire sizes (AWG, circular mils, ampacity for copper at 75°C)
standard_wires = [
    {'awg': 14, 'cm': 4110, 'ampacity': 20},
    {'awg': 12, 'cm': 6530, 'ampacity': 25},
    {'awg': 10, 'cm': 10380, 'ampacity': 35},
    {'awg': 8, 'cm': 16510, 'ampacity': 50},
    {'awg': 6, 'cm': 26250, 'ampacity': 65},
    {'awg': 4, 'cm': 41740, 'ampacity': 85},
    {'awg': 2, 'cm': 66370, 'ampacity': 115},
    {'awg': 1, 'cm': 83690, 'ampacity': 130},
    {'awg': 0, 'cm': 105600, 'ampacity': 150},
    {'awg': -1, 'cm': 133100, 'ampacity': 175},  # 2/0
    {'awg': -2, 'cm': 167800, 'ampacity': 200},  # 3/0
]

# Define standard circuit breaker sizes
standard_breakers = [15, 20, 25, 30, 40, 50, 60, 70, 80, 100, 125, 150, 175, 200]

# Define standard fuse sizes
standard_fuses = [15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 110, 125, 150, 175, 200]

# Define standard panel sizes (width x height x depth in mm)
standard_panels = [
    {'width': 400, 'height': 400, 'depth': 150},
    {'width': 400, 'height': 600, 'depth': 200},
    {'width': 600, 'height': 600, 'depth': 200},
    {'width': 600, 'height': 800, 'depth': 250},
    {'width': 800, 'height': 800, 'depth': 250},
    {'width': 800, 'height': 1000, 'depth': 300},
    {'width': 1000, 'height': 1200, 'depth': 300},
    {'width': 1200, 'height': 1400, 'depth': 400}
]

def calculate_flc(power_kw, voltage, phase_type, power_factor):
    if phase_type == "1-phase":
        return (power_kw * 1000) / (voltage * power_factor)
    else:
        return (power_kw * 1000) / (1.732 * voltage * power_factor)

def calculate_circuit_breaker(flc):
    return flc * 1.25

def get_standard_breaker(cb):
    for size in standard_breakers:
        if size >= cb:
            return size
    return None

def calculate_overload_relay(flc):
    return flc * 1.1

def calculate_contactor(flc):
    return flc

def calculate_fuse(flc):
    return flc * 1.5

def get_standard_fuse(fuse):
    for size in standard_fuses:
        if size >= fuse:
            return size
    return None

def calculate_required_cm(phase_type, flc, length_meters, V_d, conductor):
    K = 42.32 if conductor == 'copper' else 69.55
    if phase_type == "1-phase":
        return (2 * K * flc * length_meters) / V_d
    else:
        return (1.732 * K * flc * length_meters) / V_d

def get_recommended_wire(flc, required_cm):
    required_ampacity = 1.25 * flc
    for wire in standard_wires:
        if wire['ampacity'] >= required_ampacity and wire['cm'] >= required_cm:
            return wire['awg']
    return None

def calculate_pf_correction(power_kw, original_pf, desired_pf):
    if original_pf >= desired_pf:
        return 0
    tan_phi1 = math.tan(math.acos(original_pf))
    tan_phi2 = math.tan(math.acos(desired_pf))
    return power_kw * (tan_phi1 - tan_phi2)

def calculate_panel_size(num_components, include_fuse, include_plc, include_capacitors, phase_type):
    component_space = {
        'circuit_breaker': (50, 100, 100),
        'fuse': (30, 80, 80),
        'contactor': (60, 120, 120),
        'overload_relay': (50, 100, 100),
        'capacitor_bank': (200, 300, 150),
        'capacitors': (100, 150, 100),
        'plc': (150, 150, 100),
        'wiring_ducts': (100, 100, 50)
    }

    total_width = 0
    total_height = 0
    total_depth = 0
    component_count = num_components

    total_width += component_space['circuit_breaker'][0]
    total_height = max(total_height, component_space['circuit_breaker'][1])
    total_depth = max(total_depth, component_space['circuit_breaker'][2])

    total_width += component_space['contactor'][0]
    total_height = max(total_height, component_space['contactor'][1])
    total_depth = max(total_depth, component_space['contactor'][2])

    total_width += component_space['overload_relay'][0]
    total_height = max(total_height, component_space['overload_relay'][1])
    total_depth = max(total_depth, component_space['overload_relay'][2])

    if include_fuse:
        total_width += component_space['fuse'][0]
        total_height = max(total_height, component_space['fuse'][1])
        total_depth = max(total_depth, component_space['fuse'][2])
        component_count += 1

    if include_capacitors:
        if phase_type == "3-phase":
            total_width += component_space['capacitor_bank'][0]
            total_height = max(total_height, component_space['capacitor_bank'][1])
            total_depth = max(total_depth, component_space['capacitor_bank'][2])
        else:
            total_width += component_space['capacitors'][0]
            total_height = max(total_height, component_space['capacitors'][1])
            total_depth = max(total_depth, component_space['capacitors'][2])
        component_count += 1

    if include_plc:
        total_width += component_space['plc'][0]
        total_height = max(total_height, component_space['plc'][1])
        total_depth = max(total_depth, component_space['plc'][2])
        total_width += component_space['wiring_ducts'][0]
        total_height = max(total_height, component_space['wiring_ducts'][1])
        total_depth = max(total_depth, component_space['wiring_ducts'][2])
        component_count += 2

    total_width *= 1.2
    total_height *= 1.2
    total_depth *= 1.2

    for panel in standard_panels:
        if (panel['width'] >= total_width and
            panel['height'] >= total_height and
            panel['depth'] >= total_depth):
            return panel
    return None

def main():
    print("Motor Component Calculator")
    phase_type = input("Enter motor type (1-phase or 3-phase): ").lower()
    use_flc_direct = input("Do you want to input the motor's full load current (FLC) directly? (yes/no): ").lower() == "yes"

    if use_flc_direct:
        flc = float(input("Enter motor full load current (FLC) in amps: "))
        voltage = float(input("Enter voltage (V): "))
        power_factor = 0.8 if phase_type == "1-phase" else float(input("Enter power factor (for calculations): "))
    else:
        power_unit = input("Enter power unit (kW or HP): ").lower()
        if power_unit == 'hp':
            power_hp = float(input("Enter motor power (HP): "))
            power_kw = power_hp * 0.746
        else:
            power_kw = float(input("Enter motor power (kW): "))
        voltage = float(input("Enter voltage (V): "))
        power_factor = 0.8 if phase_type == "1-phase" else float(input("Enter power factor: "))
        flc = calculate_flc(power_kw, voltage, phase_type, power_factor)

    frequency = float(input("Enter frequency (Hz): "))
    length_meters = float(input("Enter length of wire run (meters): "))
    conductor = input("Enter conductor type (copper or aluminum): ").lower()
    allowable_v_drop = float(input("Enter allowable voltage drop (%): "))
    include_fuse = input("Do you want to include a fuse for additional protection? (yes/no): ").lower() == "yes"
    include_plc = input("Do you want to include a PLC in the installation? (yes/no): ").lower() == "yes"

    cb = calculate_circuit_breaker(flc)
    recommended_cb = get_standard_breaker(cb)
    ol = calculate_overload_relay(flc)
    contactor = calculate_contactor(flc)
    recommended_fuse = None
    if include_fuse:
        fuse = calculate_fuse(flc)
        recommended_fuse = get_standard_fuse(fuse)

    V_d = (allowable_v_drop / 100) * voltage
    required_cm = calculate_required_cm(phase_type, flc, length_meters, V_d, conductor)
    recommended_awg = get_recommended_wire(flc, required_cm)

    include_capacitors = False
    qc = None
    start_cap = None
    run_cap = None
    if phase_type == "3-phase":
        include_pf = input("Do you want to include power factor correction? (yes/no): ").lower() == "yes"
        if include_pf:
            desired_pf = float(input("Enter desired power factor: "))
            power_kw = flc * voltage * (1.732 if phase_type == "3-phase" else 1) * power_factor / 1000
            qc = calculate_pf_correction(power_kw, power_factor, desired_pf)
            include_capacitors = True
    elif phase_type == "1-phase":
        include_cap = input("Do you want to specify capacitors? (yes/no): ").lower() == "yes"
        if include_cap:
            start_cap = input("Enter start capacitor value (μF): ")
            run_cap = input("Enter run capacitor value (μF): ")
            include_capacitors = True

    num_components = 3
    recommended_panel = calculate_panel_size(num_components, include_fuse, include_plc, include_capacitors, phase_type)

    print(f"\nResults for {phase_type} motor:")
    print(f"Full Load Current: {flc:.2f} A")
    if recommended_cb:
        print(f"Circuit Breaker Size: {recommended_cb} A (calculated: {cb:.2f} A)")
    else:
        print(f"Circuit Breaker Size: No standard size found for {cb:.2f} A")
    if include_fuse and recommended_fuse:
        print(f"Fuse Size: {recommended_fuse} A (calculated: {fuse:.2f} A)")
    print(f"Contactor Rating: {contactor:.2f} A")
    print(f"Overload Relay Setting: {ol:.2f} A")
    if recommended_awg is not None:
        print(f"Recommended Wire Size: AWG {recommended_awg}")
    else:
        print("No standard wire meets the requirements. Consider using a larger wire or parallel conductors.")
    if phase_type == "3-phase" and include_capacitors:
        print(f"Required Capacitor Bank: {qc:.2f} kVAR")
    elif phase_type == "1-phase" and include_capacitors:
        print(f"Start Capacitor: {start_cap} μF")
        print(f"Run Capacitor: {run_cap} μF")
    if recommended_panel:
        print(f"Recommended Panel Size: {recommended_panel['width']}mm x {recommended_panel['height']}mm x {recommended_panel['depth']}mm (W x H x D)")
    else:
        print("No standard panel size meets the requirements. Consider a custom enclosure.")

    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
