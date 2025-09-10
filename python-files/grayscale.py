import os 
from datetime import datetime
import serial
import numpy as np
import matplotlib.pyplot as plt

# --- Serial ---
ser = serial.Serial("/dev/ttyUSB0", 9600, timeout=1)

rows_expected = 100
cols_expected = 100
img = np.zeros((rows_expected, cols_expected), dtype=np.uint16)

plt.ion()
fig, ax = plt.subplots()
im = ax.imshow(np.zeros_like(img, dtype=float), cmap="gray", vmin=0, vmax=255)

plt.title("Live LDR Scan")
plt.show()
row = 0
print("📡 Waiting for scan to start...")

try:
    while row < rows_expected:
        line = ser.readline().decode(errors="ignore").strip()
        if line.startswith("[") and line.endswith("]"):
            try:
                values = list(map(int, line[1:-1].split(",")))
                if len(values) == cols_expected:
                    img[row, :] = values

                    # Update display with proper grayscale
                    normalized = 255 - ((img.astype(float) - 960) * 255 / (1017 - 960))
                    normalized = np.clip(normalized, 0, 255)
                    im.set_data(normalized)

                    ax.set_title(f"Live LDR Scan Row {row+1}/{rows_expected}")
                    plt.draw()
                    plt.pause(0.05)

                    print(f"✅ Row {row+1} received")
                    row += 1
                else:
                    print(f"⚠️ Row skipped (wrong length)")
            except Exception as e:
                print(f"⚠️ Parse error: {e}")
except KeyboardInterrupt:
    print("\nStopped by user")
finally:
    ser.close()
    plt.ioff()
    plt.show()
    
    # Ensure folder exists
    folder_name = "LAKS_scanner"
    os.makedirs(folder_name, exist_ok=True)

    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(folder_name, f"ldr_scan_{timestamp}.png")

    # Normalize and save the final scanned image
    normalized = 255 - ((img.astype(float) - 960) * 255 / (1017 - 960))
    normalized = np.clip(normalized, 0, 255)
    plt.imsave(filename, normalized, cmap="gray")
    print(f"💾 Scan saved as '{filename}'")

