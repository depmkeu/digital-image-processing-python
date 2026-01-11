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

# Deteksi Mode Warna
if img.mode == 'L':  # Jika gambar grayscale
    mode = "Grayscale"
    bands = ["L"]
elif np.array_equal(np.array(img)[:, :, 0], np.array(img)[:, :, 1]) and np.array_equal(np.array(img)[:, :, 1], np.array(img)[:, :, 2]):
    mode = "Grayscale"
    bands = ["L"]
else:
    mode = "RGB"
    bands = ["R", "G", "B"]  # Urutan RGB

# Properti Citra
h, w = img.size  # Mengambil dimensi gambar (lebar, tinggi)
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

# ===== Rumus NEGASI =====
# Ko = 255 - Ki
Kmax = 255
# Mengonversi citra ke numpy array untuk pengolahan
img_array = np.array(img, dtype=np.float32)

Ko = Kmax - img_array  # Rumus Negasi
Ko = np.clip(Ko, 0, 255).astype(np.uint8)

# Simpan Hasil
base, ext = os.path.splitext(image_path)
output_name = f"{base}_negasi{ext}"
result_image = Image.fromarray(Ko)  # Mengonversi array numpy kembali ke gambar PIL
result_image.save(output_name)
print(f"Hasil citra negatif disimpan sebagai: {output_name}\n")

# Tampilkan Gambar Asli & Hasil 
plt.figure("Figure 1 - Gambar Asli dan Negatif", figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.title("Gambar Asli")
plt.imshow(img)
plt.axis("off")

plt.subplot(1, 2, 2)
plt.title("Citra Negatif")
plt.imshow(Ko, cmap="gray")
plt.axis("off")

plt.tight_layout()

# Histogram RGB
plt.figure("Figure 2 - Histogram", figsize=(12, 8))

if mode == "Grayscale":
    plt.subplot(2, 1, 1)
    plt.title("Histogram Asli")
    plt.hist(img_array.flatten(), bins=256, range=(0, 256), color="gray")
    plt.xlabel("Intensitas Piksel")
    plt.ylabel("Frekuensi")

    plt.subplot(2, 1, 2)
    plt.title("Histogram Negatif")
    plt.hist(Ko.flatten(), bins=256, range=(0, 256), color="black")
    plt.xlabel("Intensitas Piksel")
    plt.ylabel("Frekuensi")
else:
    colors = ("r", "g", "b")
    for i, col in enumerate(colors):
        # Histogram Asli
        plt.subplot(2, 3, i + 1)
        plt.title(f"Histogram {col.upper()} Asli")
        plt.hist(img_array[:, :, 2 - i].flatten(), bins=256, range=(0, 256), color=col)
        plt.xlabel("Intensitas Piksel")
        plt.ylabel("Frekuensi")

        # Histogram Negatif
        plt.subplot(2, 3, i + 4)
        plt.title(f"Histogram {col.upper()} Negatif")
        plt.hist(Ko[:, :, 2 - i].flatten(), bins=256, range=(0, 256), color=col)
        plt.xlabel("Intensitas Piksel")
        plt.ylabel("Frekuensi")

plt.tight_layout()
plt.show()
