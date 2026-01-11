import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

# Input Gambar
image_path = input("Masukkan nama file gambar: ").strip()
img = cv2.imread(image_path)  # OpenCV baca gambar BGR

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

# Rumus Modifikasi Kecemerlangan
# Ko = Ki + C
# C > 0 → gambar lebih cerah
# C < 0 → gambar lebih gelap

while True:
    try:
        C = int(input("Masukkan nilai konstanta C (positif = lebih cerah, negatif = lebih gelap): "))
        break  # Jika input valid, keluar dari loop
    except ValueError:
        print("Input tidak valid, masukkan angka integer.")

# Ubah ke float agar bisa dihitung
Ki = img.astype(np.float32)

if mode == "Grayscale":
    Ko = Ki + C
else:
    Ko = np.zeros_like(Ki)
    # Setiap channel bisa dimodifikasi dengan nilai sama (C)
    for c in range(3):
        Ko[:, :, c] = Ki[:, :, c] + C

# Batasi agar tetap di rentang 0–255
Ko = np.clip(Ko, 0, 255).astype(np.uint8)

# Simpan hasil gambar
base, ext = os.path.splitext(image_path)
output_name = f"{base}_brightness{ext}"
cv2.imwrite(output_name, Ko)
print(f"Hasil citra brightness disimpan sebagai: {output_name}\n")

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
plt.title(f"Gambar Setelah Modifikasi Brightness (C={C})")
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
    plt.title(f"Histogram Setelah Brightness (C={C})")
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
        plt.title(f"Histogram {col.upper()} Setelah Brightness (C={C})")
        plt.hist(Ko[:, :, 2 - i].flatten(), bins=256, range=(0, 256), color=col)
        plt.xlabel("Intensitas Piksel")
        plt.ylabel("Frekuensi")

plt.tight_layout()
plt.show()
