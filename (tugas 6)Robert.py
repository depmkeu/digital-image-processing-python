## Rumus (Roberts cross):
## Kernel diagonal1: [[1, 0],
##                   [0, -1]]
## Kernel diagonal2: [[0, 1],
##                   [-1, 0]]
## K1 = a - d
## K2 = b - c
## Kombinasi (contoh yang dipakai di sini):
##   K0_sum = |K1| + |K2|
##   K0_max = max(|K1|, |K2|)
##   K0_avg = (|K1| + |K2|) / 2
##   K0_mag = sqrt(K1^2 + K2^2)

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os
import math

# === INPUT GAMBAR ===
path = input("Masukkan nama file citra: ").strip()

try:
    img_rgb = Image.open(path).convert("RGB")
except:
    print("File tidak ditemukan! Pastikan nama file benar.")
    exit()

# Konversi ke array untuk deteksi mode
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

# Print properti citra
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

# Siapkan citra grayscale untuk operasi (kernel)
img_gray = img_rgb.convert("L")
pixels = img_gray.load()
w, h = img_gray.size

# Siapkan canvas hasil
K0_sum = np.zeros((h, w), dtype=np.uint8)
K0_max = np.zeros((h, w), dtype=np.uint8)
K0_avg = np.zeros((h, w), dtype=np.uint8)
K0_mag = np.zeros((h, w), dtype=np.uint8)

# === Proses Roberts ===
# Perulangan pixel 
for y in range(h-1):
    for x in range(w-1):
        a = pixels[x, y]           # top-left
        b = pixels[x+1, y]         # top-right
        c = pixels[x, y+1]         # bottom-left
        d = pixels[x+1, y+1]       # bottom-right

        # Rumus Roberts:
        K1 = a - d      # diagonal1
        K2 = b - c      # diagonal2

        # Terapkan kombinasi sesuai modul:
        v_sum = abs(K1) + abs(K2)                 # (1) SUM
        v_max = max(abs(K1), abs(K2))             # (2) MAX
        v_avg = (abs(K1) + abs(K2)) // 2          # (3) AVERAGE (integer)
        v_mag = int(math.sqrt(K1*K1 + K2*K2))     # (4) MAGNITUDE

        # Clip ke 0..255
        K0_sum[y, x] = min(v_sum, 255)
        K0_max[y, x] = min(v_max, 255)
        K0_avg[y, x] = min(v_avg, 255)
        K0_mag[y, x] = min(v_mag, 255)

# Simpan hasil
os.makedirs("edge_results", exist_ok=True)
Image.fromarray(K0_sum).save("edge_results/robert_sum.png")
Image.fromarray(K0_max).save("edge_results/robert_max.png")
Image.fromarray(K0_avg).save("edge_results/robert_avg.png")
Image.fromarray(K0_mag).save("edge_results/robert_mag.png")

print("Hasil Roberts disimpan di folder 'edge_results' (file: robert_*.png)\n")

# Tampilkan
plt.figure(figsize=(12,8))
plt.subplot(2,3,1); plt.imshow(img_rgb); plt.title("Original RGB"); plt.axis("off")
plt.subplot(2,3,2); plt.imshow(img_gray, cmap="gray"); plt.title("Grayscale"); plt.axis("off")
plt.subplot(2,3,3); plt.imshow(K0_sum, cmap="gray"); plt.title("Roberts: SUM"); plt.axis("off")
plt.subplot(2,3,4); plt.imshow(K0_max, cmap="gray"); plt.title("Roberts: MAX"); plt.axis("off")
plt.subplot(2,3,5); plt.imshow(K0_avg, cmap="gray"); plt.title("Roberts: AVERAGE"); plt.axis("off")
plt.subplot(2,3,6); plt.imshow(K0_mag, cmap="gray"); plt.title("Roberts: MAGNITUDE"); plt.axis("off")
plt.tight_layout(); plt.show()
