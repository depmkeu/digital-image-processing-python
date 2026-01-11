from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import os

# Input Gambar
image_path = input("Masukkan nama file gambar: ").strip()

try:
    img = Image.open(image_path)
except:
    print("File tidak ditemukan!")
    exit()

# Deteksi mode gambar (Grayscale atau RGB)
if img.mode == "L":  # Jika gambar grayscale
    mode = "Grayscale"
    bands = ["L"]
elif img.mode == "RGB":  # Jika gambar RGB
    mode = "RGB"
    bands = ["R", "G", "B"]
else:
    print("Format gambar tidak didukung!")
    exit()

# Properti Citra
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

# Rumus Pencerminan
# Horizontal → x' = w - 1 - x,  y' = y
# Vertikal   → x' = x,          y' = h - 1 - y
# Kombinasi  → x' = w - 1 - x,  y' = h - 1 - y

# Buat citra kosong untuk setiap hasil (otomatis sesuai mode)
if mode == "Grayscale":
    flip_horizontal = Image.new("L", (w, h))
    flip_vertical = Image.new("L", (w, h))
    flip_both = Image.new("L", (w, h))
else:
    flip_horizontal = Image.new("RGB", (w, h))
    flip_vertical = Image.new("RGB", (w, h))
    flip_both = Image.new("RGB", (w, h))

# Proses flipping manual per piksel
for y in range(h):
    for x in range(w):
        pixel = img.getpixel((x, y))

        # Horizontal
        x_new = w - 1 - x
        y_new = y
        flip_horizontal.putpixel((x_new, y_new), pixel)

        # Vertikal
        x_new = x
        y_new = h - 1 - y
        flip_vertical.putpixel((x_new, y_new), pixel)

        # Kombinasi
        x_new = w - 1 - x
        y_new = h - 1 - y
        flip_both.putpixel((x_new, y_new), pixel)

# Simpan Semua Hasil
os.makedirs("flipping_result", exist_ok=True)
base_name = os.path.splitext(os.path.basename(image_path))[0]

flip_horizontal.save(f"flipping_result/{base_name}_flipping_horizontal.png")
flip_vertical.save(f"flipping_result/{base_name}_flipping_vertical.png")
flip_both.save(f"flipping_result/{base_name}_flipping_kombinasi.png")

print("Semua hasil pencerminan berhasil disimpan di folder 'flipping_result'!\n")

# Tampilkan Hasil
plt.figure("Pencerminan (Flipping)", figsize=(12, 6))

plt.subplot(2, 2, 1)
plt.imshow(img, cmap="gray" if mode == "Grayscale" else None)
plt.title("Citra Asli")
plt.axis("off")

plt.subplot(2, 2, 2)
plt.imshow(flip_horizontal, cmap="gray" if mode == "Grayscale" else None)
plt.title("Pencerminan Horizontal")
plt.axis("off")

plt.subplot(2, 2, 3)
plt.imshow(flip_vertical, cmap="gray" if mode == "Grayscale" else None)
plt.title("Pencerminan Vertikal")
plt.axis("off")

plt.subplot(2, 2, 4)
plt.imshow(flip_both, cmap="gray" if mode == "Grayscale" else None)
plt.title("Pencerminan Kombinasi")
plt.axis("off")

plt.tight_layout()
plt.show()
