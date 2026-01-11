from PIL import Image
import matplotlib.pyplot as plt
import math
import os
import numpy as np

# Input Gambar
image_path = input("Masukkan nama file gambar: ").strip()

try:
    img = Image.open(image_path).convert("RGB")
except:
    print("File tidak ditemukan!")
    exit()
# Konversi ke array NumPy untuk analisis warna
img_array = np.array(img)

# Deteksi Mode Warna (Grayscale / RGB)
if len(img_array.shape) == 2:
    mode = "Grayscale"
    bands = ["L"]
elif img_array.shape[2] == 3 and np.array_equal(img_array[:, :, 0], img_array[:, :, 1]) and np.array_equal(img_array[:, :, 1], img_array[:, :, 2]):
    mode = "Grayscale"
    bands = ["L"]
else:
    mode = "RGB"
    bands = ["R", "G", "B"]

# Tampilkan Properti Citra
w, h = img.size
format_file = os.path.splitext(image_path)[1].upper()
ukuran_file_kb = round(os.path.getsize(image_path) / 1024, 2)
rasio_aspek = round(w / h, 2)

print("\n======================= PROPERTI CITRA =======================")
print(f"- Format file        : {format_file}")
print(f"- Mode warna         : {mode}")
print(f"- Resolusi           : {w} x {h} piksel (lebar x tinggi)")
print(f"- Jumlah kanal warna : {len(bands)} ({', '.join(bands)})")
print(f"- Kedalaman warna    : 8 bit per kanal")
print(f"- Rasio aspek        : {rasio_aspek}")
print(f"- Ukuran file        : {ukuran_file_kb} KB")
print("==============================================================\n")

# Rumus Rotasi 1/4 Putaran (90° CW)
# w’ = h   dan   h’ = w
# x’ = w’ – 1 – y
# y’ = x
rot90 = Image.new("RGB", (h, w))
for y in range(h):
    for x in range(w):
        x_new = h - 1 - y
        y_new = x
        rot90.putpixel((x_new, y_new), img.getpixel((x, y)))

# Rumus Rotasi 1/2 Putaran (180° CW)
# x’ = w’ – 1 – x
# y’ = h’ – 1 – y
rot180 = Image.new("RGB", (w, h))
for y in range(h):
    for x in range(w):
        x_new = w - 1 - x
        y_new = h - 1 - y
        rot180.putpixel((x_new, y_new), img.getpixel((x, y)))

# Rumus Rotasi Bebas (Counter Clockwise / CCW)
# x’ =  x cos(θ) + y sin(θ)
# y’ = -x sin(θ) + y cos(θ)
# w’ = |w cos(θ)| + |h sin(θ)|
# h’ = |w sin(θ)| + |h cos(θ)|

sudut = float(input("Masukkan sudut rotasi bebas: "))
theta = math.radians(sudut)

w_new = int(abs(w * math.cos(theta)) + abs(h * math.sin(theta)))
h_new = int(abs(w * math.sin(theta)) + abs(h * math.cos(theta)))

rot_bebas = Image.new("RGB", (w_new, h_new), (255, 255, 255))

# Titik pusat citra asli & baru
xc, yc = w // 2, h // 2
xc_new, yc_new = w_new // 2, h_new // 2

for y in range(h_new):
    for x in range(w_new):
        # Koordinat relatif terhadap pusat baru
        x_rel = x - xc_new
        y_rel = y - yc_new

        # Transformasi balik (agar piksel tidak kosong)
        x_asli = math.cos(-theta) * x_rel - math.sin(-theta) * y_rel + xc
        y_asli = math.sin(-theta) * x_rel + math.cos(-theta) * y_rel + yc

        if 0 <= x_asli < w and 0 <= y_asli < h:
            piksel = img.getpixel((int(x_asli), int(y_asli)))
            rot_bebas.putpixel((x, y), piksel)

# Simpan Semua Hasil Rotasi
os.makedirs("rotating_result", exist_ok=True)
base_name = os.path.splitext(os.path.basename(image_path))[0]

rot90.save(f"rotating_result/{base_name}_rotating90.png")
rot180.save(f"rotating_result/{base_name}_rotating180.png")
rot_bebas.save(f"rotating_result/{base_name}_rotating_bebas_{int(sudut)}deg.png")

print("Semua hasil rotasi berhasil disimpan di folder 'rotating_result'!\n")

# Tampilkan Semua Hasil 
plt.figure("Rotasi Citra", figsize=(12, 6))

plt.subplot(2, 2, 1)
plt.imshow(img)
plt.title("Citra Asli")
plt.axis("off")

plt.subplot(2, 2, 2)
plt.imshow(rot90)
plt.title("Rotasi 90°")
plt.axis("off")

plt.subplot(2, 2, 3)
plt.imshow(rot180)
plt.title("Rotasi 180°")
plt.axis("off")

plt.subplot(2, 2, 4)
plt.imshow(rot_bebas)
plt.title(f"Rotasi Bebas {sudut}°")
plt.axis("off")

plt.tight_layout()
plt.show()
