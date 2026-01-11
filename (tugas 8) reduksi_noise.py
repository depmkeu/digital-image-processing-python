import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import os
import random

# ===============================
# INPUT + BACA CITRA
# ===============================
path = input("Masukkan path citra: ").strip()

try:
    img_pil = Image.open(path)
except:
    print("File tidak ditemukan!")
    raise SystemExit

mode_asli = img_pil.mode

# paksa ke grayscale 8-bit (0..255)
img_gray_pil = img_pil.convert("L")
img = np.array(img_gray_pil, dtype=np.uint8)

h, w = img.shape
n = h * w

# ===============================
# OUTPUT FOLDER
# ===============================
out_dir = "noise_reduction_result"
os.makedirs(out_dir, exist_ok=True)

base = os.path.splitext(os.path.basename(path))[0]
nama = os.path.basename(path)
format_file = os.path.splitext(path)[1].upper()
ukuran_file_kb = round(os.path.getsize(path) / 1024, 2)
rasio_aspek = round(w / h, 6)
min_val = int(img.min())
max_val = int(img.max())

# ===============================
# OPSIONAL: SALT & PEPPER NOISE
# ===============================
add_noise = input("Tambah salt & pepper noise? (y/n): ").strip().lower()

noisy = img.copy()
prob = 0.0

if add_noise == "y":
    prob = float(input("Masukkan probabilitas noise: ").strip())

    # noise 
    for y in range(h):
        for x in range(w):
            r = random.random()
            if r < prob / 2.0:
                noisy[y, x] = 0
            elif r < prob:
                noisy[y, x] = 255

# ===============================
# MEDIAN FILTER 3x3
# - ambil 9 nilai tetangga
# - urutkan dari kecil ke besar
# - ambil nilai tengah (median)
# ===============================
k = 1  # 3x3
median_img = noisy.copy()  # border tetap

for y in range(k, h - k):
    for x in range(k, w - k):
        neighbors = []

        neighbors.append(int(noisy[y-1, x-1]))
        neighbors.append(int(noisy[y-1, x  ]))
        neighbors.append(int(noisy[y-1, x+1]))

        neighbors.append(int(noisy[y  , x-1]))
        neighbors.append(int(noisy[y  , x  ]))
        neighbors.append(int(noisy[y  , x+1]))

        neighbors.append(int(noisy[y+1, x-1]))
        neighbors.append(int(noisy[y+1, x  ]))
        neighbors.append(int(noisy[y+1, x+1]))

        neighbors.sort()
        median_img[y, x] = neighbors[len(neighbors) // 2]  # median dari 9 nilai

# ===============================
# SIMPAN GAMBAR HASIL
# ===============================
out_img_path = os.path.join(out_dir, f"{base}_median_3x3.png")
Image.fromarray(median_img).save(out_img_path)
hasil_disk_kb = round(os.path.getsize(out_img_path) / 1024, 2)

# ===============================
# SIMPAN TXT REPORT
# ===============================
out_txt_path = os.path.join(out_dir, f"{base}_median_report.txt")

with open(out_txt_path, "w", encoding="utf-8") as f:
    f.write("NOISE REDUCTION – MEDIAN FILTER (3x3)\n")
    f.write("=====================================\n\n")

    f.write("1) Properti Citra (Input)\n")
    f.write("+---------------------------+------------------------------+\n")
    f.write(f"| Nama Citra                 | {nama:<28} |\n")
    f.write(f"| Format File                | {format_file:<28} |\n")
    f.write(f"| Mode asli (sebelum)        | {mode_asli:<28} |\n")
    f.write(f"| Mode proses (dipakai)      | {'Grayscale (L) 8-bit':<28} |\n")
    f.write(f"| Resolusi (w x h)           | {(str(w)+' x '+str(h)):<28} |\n")
    f.write(f"| Jumlah Piksel (n)          | {n:<28} |\n")
    f.write(f"| Rentang Intensitas (min..max) | {(str(min_val)+' .. '+str(max_val)):<25} |\n")
    f.write(f"| Rasio Aspek (w/h)          | {str(rasio_aspek):<28} |\n")
    f.write(f"| Ukuran File Input (disk)   | {(str(ukuran_file_kb)+' KB'):<28} |\n")
    f.write("+---------------------------+------------------------------+\n\n")

    f.write("2) Parameter\n")
    f.write("+---------------------------+------------------------------+\n")
    f.write(f"| Kernel median              | {'3 x 3 (9 tetangga)':<28} |\n")
    f.write(f"| Tambah salt-pepper noise   | {('YA' if add_noise=='y' else 'TIDAK'):<28} |\n")
    f.write(f"| Probabilitas noise         | {prob:<28} |\n")
    f.write("+---------------------------+------------------------------+\n\n")

    f.write("3) Output\n")
    f.write("+-----------------------------------+------------------------------+\n")
    f.write(f"| Gambar hasil median (PNG)          | {out_img_path:<28} |\n")
    f.write(f"| Ukuran file hasil (disk)           | {(str(hasil_disk_kb)+' KB'):<28} |\n")
    f.write(f"| Laporan TXT                        | {out_txt_path:<28} |\n")
    f.write("+-----------------------------------+------------------------------+\n")

# ===============================
# OUTPUT CONSOLE
# ===============================
print("\n=== HASIL MEDIAN FILTER 3x3 ===")
print("Tambahkan noise        :", "YA" if add_noise == "y" else "TIDAK")
if add_noise == "y":
    print("Probabilitas noise     :", prob)
print("Output gambar          :", out_img_path)
print("Output laporan TXT     :", out_txt_path)

# ===============================
# TAMPILKAN GAMBAR
# ===============================
plt.figure(figsize=(12, 4))

plt.subplot(1, 3, 1)
plt.imshow(img, cmap="gray")
plt.title("Citra Input (Grayscale)")
plt.axis("off")

plt.subplot(1, 3, 2)
plt.imshow(noisy, cmap="gray")
plt.title("Citra (Noise / atau sama)")
plt.axis("off")

plt.subplot(1, 3, 3)
plt.imshow(median_img, cmap="gray")
plt.title("Median Filter 3x3")
plt.axis("off")

plt.tight_layout()
plt.show()
