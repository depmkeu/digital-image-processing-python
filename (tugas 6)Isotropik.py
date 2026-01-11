## Rumus (Isotropik):
## Kernel horizontal K1:
##  [-1,  0,  1]
##  [-√2, 0, √2]
##  [-1,  0,  1]
## Kernel vertical K2:
##  [-1, -√2, -1]
##  [ 0,    0,  0]
##  [ 1,  √2,  1]
## Kombinasi: SUM / MAX / AVERAGE / MAGNITUDE

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import math
import os

# INPUT
path = input("Masukkan nama file citra: ").strip()
try:
    img_rgb = Image.open(path).convert("RGB")
except:
    print("File tidak ditemukan! Pastikan nama file benar.")
    exit()

img_array = np.array(img_rgb)
w, h = img_rgb.size

# Deteksi mode warna
if len(img_array.shape) == 2:
    mode = "Grayscale"
    bands = ["L"]
elif img_array.shape[2] == 3 and np.array_equal(img_array[:,:,0], img_array[:,:,1]) and np.array_equal(img_array[:,:,1], img_array[:,:,2]):
    mode = "Grayscale"
    bands = ["L"]
else:
    mode = "RGB"
    bands = ["R","G","B"]

rasio_aspek = round(w / h, 2)
format_file = os.path.splitext(path)[1].upper()
ukuran_file_kb = round(os.path.getsize(path) / 1024, 2)
nama = os.path.basename(path)

print("\n======================= PROPERTI CITRA =======================")
print(f"Nama Citra           : {nama}")
print(f"- Format file        : {format_file}")
print(f"- Mode warna         : {mode}")
print(f"- Resolusi           : {w} x {h} piksel (lebar x tinggi)")
print(f"- Jumlah kanal warna : {len(bands)} ({', '.join(bands)})")
print(f"- Kedalaman warna    : 8 bit per kanal")
print(f"- Rasio aspek        : {rasio_aspek}")
print(f"- Ukuran file        : {ukuran_file_kb} KB")
print("==============================================================\n")

# Grayscale
img_gray = img_rgb.convert("L")
pixels = img_gray.load()
w, h = img_gray.size

K0_sum = np.zeros((h, w), dtype=np.uint8)
K0_max = np.zeros((h, w), dtype=np.uint8)
K0_avg = np.zeros((h, w), dtype=np.uint8)
K0_mag = np.zeros((h, w), dtype=np.uint8)

sqrt2 = math.sqrt(2)

for y in range(1, h-1):
    for x in range(1, w-1):
        p = [[pixels[x+i, y+j] for i in range(-1,2)] for j in range(-1,2)]

        # K1 horizontal isotropik
        K1 = (-p[0][0] + p[0][2]
             - sqrt2 * p[1][0] + sqrt2 * p[1][2]
             - p[2][0] + p[2][2])

        # K2 vertical isotropik
        K2 = (-p[0][0] - sqrt2 * p[0][1] - p[0][2]
             + p[2][0] + sqrt2 * p[2][1] + p[2][2])

        v_sum = abs(K1) + abs(K2)
        v_max = max(abs(K1), abs(K2))
        v_avg = (abs(K1) + abs(K2)) // 2
        v_mag = int(math.sqrt(K1*K1 + K2*K2))

        K0_sum[y, x] = min(v_sum, 255)
        K0_max[y, x] = min(v_max, 255)
        K0_avg[y, x] = min(v_avg, 255)
        K0_mag[y, x] = min(v_mag, 255)

# Simpan
os.makedirs("edge_results", exist_ok=True)
Image.fromarray(K0_sum).save("edge_results/iso_sum.png")
Image.fromarray(K0_max).save("edge_results/iso_max.png")
Image.fromarray(K0_avg).save("edge_results/iso_avg.png")
Image.fromarray(K0_mag).save("edge_results/iso_mag.png")

print("Hasil Isotropik disimpan di 'edge_results' (iso_*.png)\n")

# Tampilkan
plt.figure(figsize=(14,10))
plt.subplot(2,3,1); plt.imshow(img_rgb); plt.title("Original RGB"); plt.axis("off")
plt.subplot(2,3,2); plt.imshow(img_gray, cmap="gray"); plt.title("Grayscale"); plt.axis("off")
plt.subplot(2,3,3); plt.imshow(K0_sum, cmap="gray"); plt.title("Iso: SUM"); plt.axis("off")
plt.subplot(2,3,4); plt.imshow(K0_max, cmap="gray"); plt.title("Iso: MAX"); plt.axis("off")
plt.subplot(2,3,5); plt.imshow(K0_avg, cmap="gray"); plt.title("Iso: AVERAGE"); plt.axis("off")
plt.subplot(2,3,6); plt.imshow(K0_mag, cmap="gray"); plt.title("Iso: MAGNITUDE"); plt.axis("off")
plt.tight_layout(); plt.show()
