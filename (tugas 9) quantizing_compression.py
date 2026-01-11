import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import os
import math

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

# Paksa semua input jadi grayscale
img_gray_pil = img_pil.convert("L")
img = np.array(img_gray_pil, dtype=np.uint8)

h, w = img.shape
P = h * w  # P = jumlah piksel

# ===============================
# OUTPUT FOLDER
# ===============================
out_dir = "quantizing_result"
os.makedirs(out_dir, exist_ok=True)

base = os.path.splitext(os.path.basename(path))[0]
nama = os.path.basename(path)
format_file = os.path.splitext(path)[1].upper()
ukuran_file_kb = round(os.path.getsize(path) / 1024, 2)
rasio_aspek = round(w / h, 6)
min_val = int(img.min())
max_val = int(img.max())

# ===============================
# PARAMETER KUANTISASI
# contoh : 256 -> 16 level (4 bit)
# ===============================
L_new = 16  # dapat diubah derajat keabuannya menjadi 8/16/32 dst,disini menggunakan 4 bit.
bit_new = int(round(math.log2(L_new)))
if 2 ** bit_new != L_new:
    print("L_new harus pangkat 2 (misal 4, 8, 16, 32, 64, 128, 256).")
    raise SystemExit

# ===============================
# LANGKAH 1: HISTOGRAM 
# ===============================
hist = {}
for y in range(h):
    for x in range(w):
        v = int(img[y, x])
        if v in hist:
            hist[v] += 1
        else:
            hist[v] = 1

# ===============================
# LANGKAH 2: BENTUK KELOMPOK (≈ P/L_new piksel per kelompok)
# ===============================
target = P / L_new

groups = []  # list of list nilai lama per kelompok
current_group = []
current_count = 0

for val in sorted(hist.keys()):
    current_group.append(val)
    current_count += hist[val]

    if current_count >= target and len(groups) < (L_new - 1):
        groups.append(current_group)
        current_group = []
        current_count = 0

if current_group:
    groups.append(current_group)

# kalau kelompok kurang dari L_new, sisanya dianggap kelompok kosong 
# mapping akan pakai index kelompok yang ada

# ===============================
# LANGKAH 3: MAPPING NILAI LAMA -> NILAI BARU (0..L_new-1)
# ===============================
mapping = {}
for i, group in enumerate(groups):
    new_val = min(i, L_new - 1)
    for old_val in group:
        mapping[old_val] = new_val

# ===============================
# TERAPKAN KUANTISASI
# hasil "quantized" berisi 0..(L_new-1)
# ===============================
quantized = np.zeros_like(img, dtype=np.uint8)
for y in range(h):
    for x in range(w):
        quantized[y, x] = mapping[int(img[y, x])]

# buat tampilan biar kelihatan (skala ke 0..255)
scale = 255 // (L_new - 1) if L_new > 1 else 0
quantized_view = (quantized * scale).astype(np.uint8)

# ===============================
# UKURAN DATA (bit)
# ===============================
original_bits = P * 8
after_bits = P * bit_new

ratio_kompresi = 100.0 - ((after_bits / original_bits) * 100.0) if original_bits > 0 else 0.0
cr_asli_hasil = (original_bits / after_bits) if after_bits > 0 else 0.0

# ===============================
# SIMPAN GAMBAR HASIL
# ===============================
out_img_path = os.path.join(out_dir, f"{base}_quantized_{L_new}level.png")
Image.fromarray(quantized_view).save(out_img_path)
hasil_disk_kb = round(os.path.getsize(out_img_path) / 1024, 2)

# ===============================
# SIMPAN TXT (
# ===============================
out_txt_path = os.path.join(out_dir, f"{base}_quantizing_report.txt")

with open(out_txt_path, "w", encoding="utf-8") as f:
    f.write("QUANTIZING COMPRESSION (LOSSY)\n")
    f.write("==============================================\n\n")

    # 1) Properti citra
    f.write("1) Properti Citra\n")
    f.write("+---------------------------+------------------------------+\n")
    f.write(f"| Nama Citra                    | {nama:<28} |\n")
    f.write(f"| Format File                   | {format_file:<28} |\n")
    f.write(f"| Mode asli (sebelum)           | {mode_asli:<28} |\n")
    f.write(f"| Mode proses (dipakai)         | {'Grayscale (L) 8-bit':<28} |\n")
    f.write(f"| Resolusi (w x h)              | {(str(w)+' x '+str(h)):<28} |\n")
    f.write(f"| Jumlah Piksel (P)             | {P:<28} |\n")
    f.write(f"| Rentang Intensitas (min..max) | {(str(min_val)+' .. '+str(max_val)):<28} |\n")
    f.write(f"| Rasio Aspek (w/h)             | {str(rasio_aspek):<28} |\n")
    f.write(f"| Ukuran File Input (disk)      | {(str(ukuran_file_kb)+' KB'):<28} |\n")
    f.write("+---------------------------+------------------------------+\n\n")

    # 2) Parameter quantizing
    f.write("2) Parameter Quantizing\n")
    f.write("+---------------------------+------------------------------+\n")
    f.write(f"| Level baru (L_new)         | {L_new:<28} |\n")
    f.write(f"| Bit/piksel baru (log2 L)   | {bit_new:<28} |\n")
    f.write(f"| Target piksel/kelompok     | {target:<28.4f} |\n")
    f.write("+---------------------------+------------------------------+\n\n")

    # 3) Histogram (nilai intensitas vs jumlah piksel)
    f.write("3) Histogram Citra Awal\n")
    f.write("+----------+--------------+\n")
    f.write("| Nilai    | Jumlah Piksel|\n")
    f.write("+----------+--------------+\n")
    for k in sorted(hist.keys()):
        f.write(f"| {k:8d} | {hist[k]:12d} |\n")
    f.write("+----------+--------------+\n\n")

    # 4) Pembentukan kelompok
    f.write("4) Pembentukan Kelompok (≈ P/L_new)\n")
    f.write("+----------+-----------------------------+----------------+\n")
    f.write("| Kelompok | Rentang Nilai Lama          | Total Piksel    |\n")
    f.write("+----------+-----------------------------+----------------+\n")
    for i, group in enumerate(groups):
        total_group = 0
        for v in group:
            total_group += hist[v]
        rng = f"{group[0]}..{group[-1]}" if len(group) > 1 else f"{group[0]}"
        f.write(f"| {i+1:8d} | {rng:<27} | {total_group:14d} |\n")
    f.write("+----------+-----------------------------+----------------+\n\n")

    # 5) Mapping nilai lama -> nilai baru
    f.write(f"5) Pemetaan Nilai Lama -> Nilai Baru (0..{L_new-1})\n")
    f.write("+----------+----------+\n")
    f.write("| NilaiOld | NilaiNew |\n")
    f.write("+----------+----------+\n")
    for k in sorted(mapping.keys()):
        f.write(f"| {k:8d} | {mapping[k]:8d} |\n")
    f.write("+----------+----------+\n\n")

    # 6) Ukuran data (bit)
    f.write("6) Ukuran Data (bit) + Rasio\n")
    f.write("+---------------------------------------------+------------------+\n")
    f.write(f"| Ukuran citra asli (P x 8 bit)               | {original_bits:16d} |\n")
    f.write(f"| Ukuran citra hasil (P x {bit_new} bit)              | {after_bits:16d} |\n")
    f.write(f"| Ratio = 100% - (hasil/asli x 100%)          | {ratio_kompresi:16.2f} |\n")
    f.write(f"| CR (Asli/Hasil)                             | {cr_asli_hasil:16.4f} |\n")
    f.write("+---------------------------------------------+------------------+\n\n")

    # 7) Output file
    f.write("7) Output\n")
    f.write("+-----------------------------------+------------------------------+\n")
    f.write(f"| Gambar hasil quantizing (PNG)     | {out_img_path:<28} |\n")
    f.write(f"| Ukuran file hasil (disk)          | {(str(hasil_disk_kb)+' KB'):<28} |\n")
    f.write(f"| Catatan                           | {'LOSSY (level berubah)':<28} |\n")
    f.write("+-----------------------------------+------------------------------+\n")

# ===============================
# OUTPUT CONSOLE 
# ===============================
print("\n======================= PROPERTI CITRA =======================")
print(f"Nama Citra              : {nama}")
print(f"- Format file           : {format_file}")
print(f"- Mode asli             : {mode_asli}")
print(f"- Mode proses           : Grayscale (L) 8-bit")
print(f"- Resolusi              : {w} x {h} (lebar x tinggi)")
print(f"- Jumlah piksel (P)     : {P}")
print(f"- Rentang Intensitas    : {min_val} .. {max_val}")
print(f"- Ukuran file (disk)    : {ukuran_file_kb} KB")
print("==============================================================")

print("\n=== HASIL QUANTIZING ===")
print(f"Level: 256 -> {L_new} (bit/piksel: 8 -> {bit_new})")
print(f"Ukuran sebelum : P x 8  = {P} x 8  = {original_bits} bit")
print(f"Ukuran sesudah : P x {bit_new}  = {P} x {bit_new}  = {after_bits} bit")
print("Ratio = 100% - (hasil/asli * 100%)")
print(f"      = 100% - ({after_bits}/{original_bits} * 100%)")
print(f"      = {ratio_kompresi:.2f}%")
print(f"CR (Asli/Hasil) : {cr_asli_hasil:.4f}")
print("Catatan         : LOSSY (derajat keabuan/level berubah)")
print("================================")

print("\n=== PARAMETER QUANTIZING ===")
print(f"Level keabuan baru (L_new) : {L_new:<28} |\n")
print(f"Bit per piksel (log2 L)    : {bit_new:<28} |\n")

print("\nSelesai.")
print("TXT tersimpan   :", out_txt_path)
print("Gambar tersimpan:", out_img_path)

# ===============================
# TAMPILKAN GAMBAR
# ===============================
plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
plt.imshow(img, cmap="gray")
plt.title("Citra Input (Grayscale 8-bit)")
plt.axis("off")

plt.subplot(1, 2, 2)
plt.imshow(quantized_view, cmap="gray")
plt.title(f"Citra Setelah Quantizing ({L_new} level)")
plt.axis("off")

plt.tight_layout()
plt.show()
