import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

# Input Gambar
image_path = input("Masukkan nama file gambar: ").strip()
img = cv2.imread(image_path)  # OpenCV baca gambar dalam format BGR

if img is None:
    print("File tidak ditemukan!")
    exit()

# Deteksi Mode Warna
if len(img.shape) == 2:
    mode = "Grayscale"
    bands = ["L"]
elif np.array_equal(img[:, :, 0], img[:, :, 1]) and np.array_equal(img[:, :, 1], img[:, :, 2]):
    # Jika Ketiga Channel (B, G, R) Sama → Citra Grayscale
    mode = "Grayscale"
    bands = ["L"]    
else:
    mode = "RGB"
    bands = ["B", "G", "R"]  # urutan BGR karena OpenCV

# Properti Citra
h, w = img.shape[:2]
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

# ===== Rumus Peningkatan Kontras =====
# Ko = G * (Ki - P) + P
# G = Koefisien penguatan kontras (input pengguna)
# Ki = Kontras input (nilai piksel asli)
# P = Nilai skala keabuan sebagai pusat pengontrasan
# Ko = Kontras output (nilai piksel hasil)

while True:
    try:
        G = float(input("Masukkan nilai G (koefisien penguatan kontras): "))
        break  # Jika input valid, keluar dari loop
    except ValueError:
        print("Input tidak valid, masukkan angka.")

# Ubah ke float agar bisa dihitung
Ki = img.astype(np.float32)

if mode == "Grayscale":
    P = np.mean(Ki)
    Ko = G * (Ki - P) + P
else:
    Ko = np.zeros_like(Ki)
    for c in range(3):
        P = np.mean(Ki[:, :, c])
        Ko[:, :, c] = G * (Ki[:, :, c] - P) + P

# Batasi agar tetap di 0–255
Ko = np.clip(Ko, 0, 255).astype(np.uint8)

# Simpan hasil gambar
base, ext = os.path.splitext(image_path)
output_name = f"{base}_contrast{ext}"
cv2.imwrite(output_name, Ko)
print(f"Hasil citra kontras disimpan sebagai: {output_name}\n")

# Tampilkan Gambar Asli & Hasil 
plt.figure("Figure 1 - Gambar Asli dan Hasil", figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.title("Gambar Asli")
if mode == "RGB":
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
else:
    plt.imshow(img, cmap="gray")
plt.axis("off")

plt.subplot(1, 2, 2)
plt.title(f"Gambar Setelah Peningkatan Kontras (G={G})")
if mode == "RGB":
    plt.imshow(cv2.cvtColor(Ko, cv2.COLOR_BGR2RGB))
else:
    plt.imshow(Ko, cmap="gray")
plt.axis("off")

plt.tight_layout()

# Tampilkan Histogram 
plt.figure("Figure 2 - Histogram", figsize=(10, 6))

if mode == "Grayscale":
    plt.subplot(2, 1, 1)
    plt.title("Histogram Asli")
    plt.hist(Ki.flatten(), bins=256, range=(0, 256), color="gray")
    plt.xlabel("Intensitas Piksel")
    plt.ylabel("Frekuensi")

    plt.subplot(2, 1, 2)
    plt.title(f"Histogram Setelah Kontras (G={G})")
    plt.hist(Ko.flatten(), bins=256, range=(0, 256), color="black")
    plt.xlabel("Intensitas Piksel")
    plt.ylabel("Frekuensi")
else:
    colors = ("r", "g", "b")
    for i, col in enumerate(colors):
        plt.subplot(2, 3, i + 1)
        plt.title(f"Histogram {col.upper()} Asli")
        plt.hist(Ki[:, :, 2 - i].flatten(), bins=256, range=(0, 256), color=col)
        plt.xlabel("Intensitas Piksel")
        plt.ylabel("Frekuensi")

        plt.subplot(2, 3, i + 4)
        plt.title(f"Histogram {col.upper()} Setelah Kontras (G={G})")
        plt.hist(Ko[:, :, 2 - i].flatten(), bins=256, range=(0, 256), color=col)
        plt.xlabel("Intensitas Piksel")
        plt.ylabel("Frekuensi")

plt.tight_layout()
plt.show()
