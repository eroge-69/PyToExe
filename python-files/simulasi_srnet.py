from PIL import Image, ImageFilter
import numpy as np

# Load HR image
hr = Image.open("your_hr_image.png").convert("RGB")
#hr = hr.resize((128, 128))  # kecilkan agar lebih cepat

# Step 1: Degradasi → Buat LR image (blur + downscale)
lr = hr.filter(ImageFilter.GaussianBlur(radius=1.2))
scale = 4
lr = lr.resize((hr.width // scale, hr.height // scale), Image.BICUBIC)
lr.save("simulasi_LR.png")

# Step 2: Simulasi "Proses ESRNet"

# (a) Upsample 2x dua kali → total 4x (mirip PixelShuffle)
sr = lr.resize((lr.width * 2, lr.height * 2), Image.BICUBIC)
sr = sr.resize((sr.width * 2, sr.height * 2), Image.BICUBIC)

# (b) Tambahkan proses "residual" palsu: sharpening beberapa kali
for _ in range(3):  # mirip residual block ringan
    sr = sr.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))

sr.save("simulasi_SR.png")

# Step 3: Evaluasi – Hitung L1 Loss (Mean Absolute Error)
sr_np = np.asarray(sr).astype(np.float32) / 255.0
hr_np = np.asarray(hr).astype(np.float32) / 255.0
loss = np.mean(np.abs(hr_np - sr_np))
print(f"L1 Loss (simulasi): {loss:.4f}")

