from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os

# Input Gambar
image_path = input("Masukkan nama file gambar: ").strip()
try:
    img = Image.open(image_path)  # PIL membuka gambar
except FileNotFoundError:
    print("File tidak ditemukan!")
    exit()

# Konversi ke Grayscale secara manual (tanpa fungsi jadi)
# Rumus NTSC: Ko = 0.299R + 0.587G + 0.114B
if img.mode == 'RGB':
    r, g, b = img.split()  # Pisahkan channel RGB
    # Convert ke numpy array untuk pengolahan
    r = np.array(r, dtype=np.float32)
    g = np.array(g, dtype=np.float32)
    b = np.array(b, dtype=np.float32)
    # Gunakan rumus NTSC untuk konversi ke grayscale
    img_grayscale = (0.299 * r + 0.587 * g + 0.114 * b).astype(np.uint8)
else:
    # Jika gambar sudah grayscale, langsung konversi
    img_grayscale = np.array(img, dtype=np.uint8)

# Deteksi Mode Warna
mode = "Grayscale"
bands = ["L"]

# Properti Citra
h, w = img_grayscale.shape[:2]
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

# ===== Rumus Thresholding =====
# Pengambangan Tunggal:
# Ko = 0 jika Ki < T
# Ko = 255 jika Ki ≥ T
T = 140
Ko_tunggal = np.zeros((h, w), dtype=np.uint8)
for y in range(h):
    for x in range(w):
        Ko_tunggal[y, x] = 0 if img_grayscale[y, x] < T else 255

# Pengambangan Ganda:
# Ko = 255 jika T_low ≤ Ki ≤ T_high, 0 lainnya
T_low, T_high = 100, 140
Ko_ganda = np.zeros((h, w), dtype=np.uint8)
for y in range(h):
    for x in range(w):
        if T_low <= img_grayscale[y, x] <= T_high:
            Ko_ganda[y, x] = 255
        else:
            Ko_ganda[y, x] = 0

# Simpan Hasil
base, ext = os.path.splitext(image_path)
output_single = f"{base}_thresholdingTunggal{ext}"
output_double = f"{base}_thresholdingGanda{ext}"

result_single = Image.fromarray(Ko_tunggal)  # Convert to PIL Image
result_double = Image.fromarray(Ko_ganda)  # Convert to PIL Image

result_single.save(output_single)
result_double.save(output_double)

print(f"Hasil Threshold Tunggal disimpan sebagai : {output_single}")
print(f"Hasil Threshold Ganda   disimpan sebagai : {output_double}\n")

# ===== Tampilkan Gambar Asli dan Hasil =====
plt.figure("Figure 1 - Citra Asli dan Hasil Thresholding", figsize=(12, 6))

plt.subplot(1, 3, 1)
plt.title("Citra Grayscale Asli")
plt.imshow(img_grayscale, cmap="gray")
plt.axis("off")

plt.subplot(1, 3, 2)
plt.title(f"Threshold Tunggal (T={T})")
plt.imshow(Ko_tunggal, cmap="gray")
plt.axis("off")

plt.subplot(1, 3, 3)
plt.title(f"Threshold Ganda ({T_low}-{T_high})")
plt.imshow(Ko_ganda, cmap="gray")
plt.axis("off")

plt.tight_layout()

# ===== Histogram =====
plt.figure("Figure 2 - Histogram", figsize=(10, 6))

plt.subplot(3, 1, 1)
plt.title("Histogram Citra Grayscale Asli")
plt.hist(img_grayscale.flatten(), bins=256, range=(0, 256), color="black")
plt.xlabel("Intensitas Piksel")
plt.ylabel("Frekuensi")

plt.subplot(3, 1, 2)
plt.title("Histogram Threshold Tunggal")
plt.hist(Ko_tunggal.flatten(), bins=256, range=(0, 256), color="black")
plt.xlabel("Intensitas Piksel")
plt.ylabel("Frekuensi")

plt.subplot(3, 1, 3)
plt.title("Histogram Threshold Ganda")
plt.hist(Ko_ganda.flatten(), bins=256, range=(0, 256), color="black")
plt.xlabel("Intensitas Piksel")
plt.ylabel("Frekuensi")

plt.tight_layout()
plt.show()
