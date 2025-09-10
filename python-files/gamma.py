import ctypes

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

# Get device context for the entire screen
hDC = user32.GetDC(0)

# === ADJUST THESE VALUES ===
gamma = 0.3       # 1.0 = normal, <1 = darker, >1 = brighter
contrast = 1.2    # 1.0 = normal, >1 = higher contrast, <1 = lower contrast

# Build gamma + contrast ramp
ramp = []
for i in range(256):
    normalized = i / 255.0
    # Apply contrast first (centered around 0.5)
    adjusted = ((normalized - 0.5) * contrast) + 0.5
    if adjusted < 0:
        adjusted = 0
    if adjusted > 1:
        adjusted = 1
    # Apply gamma
    value = int((adjusted ** gamma) * 65535 + 0.5)
    if value > 65535:
        value = 65535
    ramp.append(value)

# Repeat for R, G, B
gamma_array = ramp * 3

# Convert to ctypes array
GammaArray = (ctypes.c_ushort * len(gamma_array))(*gamma_array)

# Apply gamma ramp
res = gdi32.SetDeviceGammaRamp(hDC, GammaArray)

if res:
    print(f"Gamma set to {gamma}, contrast set to {contrast}.")
else:
    print("Failed to apply gamma/contrast.")
