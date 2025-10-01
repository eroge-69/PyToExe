import re
import sys
from pathlib import Path
import matplotlib.pyplot as plt

def process_gcode(input_file, dx=10.0, dy=10.0):
    coord_re = re.compile(r'([XY])\s*([-+]?\d*\.?\d+)')
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"Errore: file {input_file} non trovato.")
        return
    
    output_path = input_path.with_name(input_path.stem + "_safe_offset" + input_path.suffix)
    
    # Liste per plottare
    xs, ys = [], []
    curr_x, curr_y = None, None
    
    with open(input_path, 'r') as f_in, open(output_path, 'w') as f_out:
        # Scrivi header
        f_out.write("; --- HEADER DI SICUREZZA INSERITO ---\n")
        f_out.write("G21         ; unità in mm\n")
        f_out.write("G90         ; coordinate assolute\n")
        f_out.write("G28         ; homing assi\n")
        f_out.write("G0 Z5 F3000 ; solleva penna a 5mm prima di muoverti\n")
        f_out.write("; ---------------------------------\n\n")
        
        for line in f_in:
            s = line.strip().upper()
            if s.startswith(('G0','G1')):
                def repl(m):
                    nonlocal curr_x, curr_y
                    axis = m.group(1)
                    val = float(m.group(2))
                    if axis == 'X':
                        val += dx
                        curr_x = val
                        return f'X{val:.4f}'
                    elif axis == 'Y':
                        val += dy
                        curr_y = val
                        return f'Y{val:.4f}'
                    return m.group(0)
                
                newline = coord_re.sub(repl, line)
                f_out.write(newline)
                
                if curr_x is not None and curr_y is not None:
                    xs.append(curr_x)
                    ys.append(curr_y)
            else:
                f_out.write(line)
    
    print(f"File processato con successo! Salvato come: {output_path}")
    
    # --- Plot percorso ---
    if xs and ys:
        plt.figure(figsize=(6,6))
        plt.plot(xs, ys, 'b-', linewidth=0.6, label="Percorso con offset")
        plt.scatter([min(xs), max(xs)], [min(ys), max(ys)], color='red', marker='x', label="Bounding box")
        plt.gca().set_aspect('equal', adjustable='box')
        plt.xlabel("X [mm]")
        plt.ylabel("Y [mm]")
        plt.title("Anteprima PCB con offset di sicurezza")
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.show()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python secure_gcode.py <file.gcode> [offset_x offset_y]")
    else:
        infile = sys.argv[1]
        dx = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0
        dy = float(sys.argv[3]) if len(sys.argv) > 3 else 10.0
        process_gcode(infile, dx, dy)
