import os
from PIL import Image

# ============================================================
# SEGMENTASI BERDASARKAN INTENSITAS (URUT PIXEL) - GRAYSCALE 8-BIT
# FINAL: tanpa sorted() untuk sorting (pakai counting sort 0..255)
# Output:
# 1) grayscale 8-bit
# 2) sorted-pixels ascending (global ordering, diisi ulang row-major)
# 3) report TXT lengkap (termasuk tabel sebelum vs sesudah untuk SEMUA pixel)
# ============================================================

# ===============================
# INPUT
# ===============================
image_path = input("Masukkan path citra: ").strip()

try:
    img_rgb = Image.open(image_path).convert("RGB")  # I/O boleh
except:
    print("File tidak ditemukan!")
    raise SystemExit

w, h = img_rgb.size
pix = img_rgb.load()
n = w * h

# ===============================
# OUTPUT FOLDER
# ===============================
out_dir = "segmentasi_sort_output"
os.makedirs(out_dir, exist_ok=True)

base = os.path.splitext(os.path.basename(image_path))[0]
nama = os.path.basename(image_path)
format_file = os.path.splitext(image_path)[1].upper()
ukuran_file_kb = round(os.path.getsize(image_path) / 1024, 2)
rasio_aspek = round(w / h, 6)

# ============================================================
# (1) GRAYSCALE 8-BIT
# I = 0.299R + 0.587G + 0.114B
# ============================================================
gray = [0] * n
min_val = 255
max_val = 0

idx = 0
for y in range(h):
    for x in range(w):
        r, g, b = pix[x, y]
        v = int(round(0.299 * r + 0.587 * g + 0.114 * b))
        if v < 0:
            v = 0
        elif v > 255:
            v = 255

        gray[idx] = v
        idx += 1

        if v < min_val:
            min_val = v
        if v > max_val:
            max_val = v

gray_img = Image.new("L", (w, h))
gray_img.putdata(gray)
gray_path = os.path.join(out_dir, f"{base}_grayscale_8bit.png")
gray_img.save(gray_path)
gray_disk_kb = round(os.path.getsize(gray_path) / 1024, 2)

# ============================================================
# (2) SORTING INTENSITAS TANPA sorted()
# Counting Sort karena domain intensitas 0..255
#
# Konsep "segmentasi":
# - semua piksel dikumpulkan (gray 1D)
# - diurutkan global dari intensitas terkecil -> terbesar
# - disusun ulang ke gambar baru secara row-major:
#   (0,0)->(w-1,0)->...->(0,1)->...->(w-1,h-1)
# ============================================================
count = [0] * 256
for v in gray:
    count[v] += 1 #loop semua nilai

sorted_vals = [0] * n #Membuat array secara berurut
pos = 0
for val in range(256):
    c = count[val]
    for _ in range(c):
        sorted_vals[pos] = val
        pos += 1

sorted_img = Image.new("L", (w, h))
sorted_img.putdata(sorted_vals)
sorted_path = os.path.join(out_dir, f"{base}_sorted_pixels_ascending.png")
sorted_img.save(sorted_path)
sorted_disk_kb = round(os.path.getsize(sorted_path) / 1024, 2)

# ============================================================
# Histogram & Probabilitas
# freq[k] = nk
# P(k) = nk/n
# ============================================================
freq = count[:]  # sudah ada
symbols = []
for k in range(256):
    if freq[k] > 0:
        symbols.append(k)

L = len(symbols)

# ============================================================
# REPORT TXT
# - Properti
# - Rumus grayscale
# - Histogram & peluang
# - Penjelasan sorting (counting sort)
# - Tabel (x,y) sebelum vs sesudah untuk SEMUA pixel
# ============================================================
rep_path = os.path.join(out_dir, f"{base}_report_segmentasi_sort.txt")
with open(rep_path, "w", encoding="utf-8") as f:
    f.write("SEGMENTASI BERDASARKAN INTENSITAS (URUT PIXEL) - GRAYSCALE 8-BIT\n")
    f.write("================================================================\n\n")

    # 1) Properti
    f.write("1) Properti Citra (Input)\n")
    f.write("+---------------------------+------------------------------+\n")
    f.write(f"| Nama Citra                 | {nama:<28} |\n")
    f.write(f"| Format File                | {format_file:<28} |\n")
    f.write(f"| Mode Proses                | {'RGB -> Grayscale (L) 8-bit':<28} |\n")
    f.write(f"| Resolusi (w x h)           | {(str(w)+' x '+str(h)):<28} |\n")
    f.write(f"| Jumlah Piksel (n)          | {n:<28} |\n")
    f.write(f"| Derajat Keabuan (min..max) | {(str(min_val)+' .. '+str(max_val)):<28} |\n")
    f.write(f"| Rasio Aspek (w/h)          | {str(rasio_aspek):<28} |\n")
    f.write(f"| Ukuran File Input (disk)   | {(str(ukuran_file_kb)+' KB'):<28} |\n")
    f.write(f"| Jumlah Simbol Unik (L)     | {L:<28} |\n")
    f.write("+---------------------------+------------------------------+\n\n")

    # 2) Konversi grayscale
    f.write("2) Konversi Grayscale 8-bit\n")
    f.write("Rumus (modul): I = 0.299R + 0.587G + 0.114B\n")
    f.write("Implementasi: v = round(0.299*r + 0.587*g + 0.114*b)\n")
    f.write("Clamping: jika v<0 -> 0, jika v>255 -> 255\n\n")

    # 3) Histogram & peluang
    f.write("3) Histogram Intensitas (nk) dan Peluang P(k)=nk/n\n")
    f.write("+----------+------------+------------+\n")
    f.write("| k        | nk         | P(k)       |\n")
    f.write("+----------+------------+------------+\n")
    for k in symbols:
        pk = freq[k] / n
        f.write(f"| {k:8d} | {freq[k]:10d} | {pk:10.6f} |\n")
    f.write("+----------+------------+------------+\n\n")

    # 4) Penjelasan sorting
    f.write("4) Pengelompokan/Urut Intensitas (Global Intensity Ordering)\n")
    f.write("Konsep: semua piksel dikumpulkan, lalu diurutkan dari intensitas terkecil ke terbesar.\n")
    f.write("Metode: Counting Sort (karena domain intensitas 0..255)\n\n")
    f.write("Langkah:\n")
    f.write("a) Hitung frekuensi tiap intensitas: count[val] = jumlah kemunculan val\n")
    f.write("b) Susun keluaran urut: tulis 'val' sebanyak count[val] dari val=0..255\n")
    f.write("c) Isi kembali citra output secara row-major: (0,0) -> (w-1,h-1)\n\n")

    # 5) Ukuran data (catatan)
    grayscale_bits = n * 8
    f.write("5) Ukuran Data (bit) - Catatan\n")
    f.write("+---------------------------------------------+------------------+\n")
    f.write(f"| Ukuran citra grayscale 8-bit (n x 8 bit)    | {grayscale_bits:16d} |\n")
    f.write(f"| Ukuran setelah sorting (tetap n x 8 bit)    | {grayscale_bits:16d} |\n")
    f.write("+---------------------------------------------+------------------+\n\n")

    # 6) Output
    f.write("6) Output\n")
    f.write("+-----------------------------------+------------------------------+\n")
    f.write(f"| Grayscale 8-bit (PNG)            | {os.path.basename(gray_path):<28} |\n")
    f.write(f"| Ukuran file grayscale (disk)     | {(str(gray_disk_kb)+' KB'):<28} |\n")
    f.write(f"| Sorted Pixels Ascending (PNG)    | {os.path.basename(sorted_path):<28} |\n")
    f.write(f"| Ukuran file sorted (disk)        | {(str(sorted_disk_kb)+' KB'):<28} |\n")
    f.write(f"| Report TXT                       | {os.path.basename(rep_path):<28} |\n")
    f.write("+-----------------------------------+------------------------------+\n\n")

    # 7) FULL table sebelum vs sesudah
    f.write("7) Nilai Piksel SEBELUM vs SESUDAH (SEMUA KOORDINAT)\n")
    f.write("+--------+--------+------------------+------------------+\n")
    f.write("| x      | y      | sebelum(gray)    | sesudah(sorted)  |\n")
    f.write("+--------+--------+------------------+------------------+\n")

    for y in range(h):
        row_base = y * w
        for x in range(w):
            i = row_base + x
            f.write(f"| {x:6d} | {y:6d} | {gray[i]:16d} | {sorted_vals[i]:16d} |\n")

    f.write("+--------+--------+------------------+------------------+\n\n")

# ============================================================
# OUTPUT CONSOLE
# ============================================================
print("\n=== HASIL ===")
print("Resolusi           :", w, "x", h)
print("Jumlah piksel (n)  :", n)
print("Rentang intensitas :", min_val, "..", max_val)
print("\nGrayscale 8-bit    :", gray_path)
print("Sorted pixels img  :", sorted_path)
print("Report TXT         :", rep_path)
print("\nSelesai. Semua output ada di folder:", out_dir)
