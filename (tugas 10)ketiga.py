import os
from PIL import Image

# ============================================================
# SEGMENTASI BERDASARKAN INTENSITAS (URUT PIXEL) - GRAYSCALE 8-BIT
# + PENCARIAN INTENSITAS TERBESAR KE-2
# 1) Scan semua pixel -> ubah RGB ke grayscale (0..255)
# 2) Buat histogram (count[0..255]) -> hitung frekuensi intensitas
# 3) "Sorting" global pakai counting sort -> hasil urut kecil -> besar
# 4) Cari nilai intensitas terbesar dan terbesar ke-2 dari histogram
# 5) Cari koordinat pixel yang nilainya == terbesar ke-2
# 6) Buat mask: putih=posisi pixel terbesar ke-2, hitam=lainnya
# 7) Simpan semua output dan report
# ============================================================

# ===============================
# INPUT PATH GAMBAR
# ===============================
image_path = input("Masukkan path citra: ").strip()

try:
    img_rgb = Image.open(image_path).convert("RGB")  # Convert ke RGB supaya pasti 3 channel
except:
    print("File tidak ditemukan!")
    raise SystemExit

w, h = img_rgb.size

pix = img_rgb.load()

# Total pixel = lebar * tinggi
n = w * h

# ===============================
# SIAPKAN FOLDER OUTPUT
# ===============================
out_dir = "segmentasi_sort_output"
os.makedirs(out_dir, exist_ok=True)

base = os.path.splitext(os.path.basename(image_path))[0]
nama = os.path.basename(image_path)
format_file = os.path.splitext(image_path)[1].upper()

ukuran_file_kb = round(os.path.getsize(image_path) / 1024, 2)

# Rasio aspek w/h
rasio_aspek = round(w / h, 6)

# ============================================================
# (1) KONVERSI GRAYSCALE 8-BIT (SCAN SEMUA PIXEL)
# ============================================================
# gray akan menampung grayscale dalam bentuk array 1D panjang n.
# Urutan penyimpanan: row-major (baris dulu, lalu kolom)
# Artinya:
#   index i = y*w + x
#   pixel (0,0) disimpan pertama, lalu (1,0), ..., (w-1,0),
#   lanjut (0,1), ..., sampai (w-1,h-1)

gray = [0] * n       # array intensitas grayscale
min_val = 255        # untuk cari intensitas minimum
max_val = 0          # untuk cari intensitas maximum

idx = 0
# LOOP 1: loop koordinat pixel (x,y) untuk MEMBACA SEMUA PIXEL
for y in range(h):               
    for x in range(w):           
        r, g, b = pix[x, y]      

        # Rumus grayscale sesuai modul:
        # I = 0.299R + 0.587G + 0.114B
        v = int(round(0.299*r + 0.587*g + 0.114*b))

        if v < 0:
            v = 0
        elif v > 255:
            v = 255

        # Simpan ke array gray urutan 1D
        gray[idx] = v
        idx += 1

        # Update min/max intensitas
        if v < min_val:
            min_val = v
        if v > max_val:
            max_val = v

# Buat image grayscale dan simpan
gray_img = Image.new("L", (w, h))
gray_img.putdata(gray)
gray_path = os.path.join(out_dir, f"{base}_grayscale_8bit.png")
gray_img.save(gray_path)
gray_disk_kb = round(os.path.getsize(gray_path) / 1024, 2)

# ============================================================
# (2) HISTOGRAM + COUNTING SORT (SORTING TANPA sorted())
# ============================================================
# count[val] = berapa kali intensitas val muncul di gambar
# Ini histogram derajat keabuan

count = [0] * 256

# LOOP 2: loop seluruh pixel grayscale untuk HITUNG FREKUENSI
for v in gray:
    count[v] += 1

# Setelah histogram ada, kita bisa "urutkan" intensitas
sorted_vals = [0] * n
pos = 0

# LOOP 3: loop intensitas dari kecil ke besar (0..255)
for val in range(256):
    # tulis val sebanyak count[val]
    for _ in range(count[val]):
        sorted_vals[pos] = val
        pos += 1

# sorted_vals sekarang terurut ascending (kecil -> besar)
# lalu diisikan kembali ke image output secara row-major:
sorted_img = Image.new("L", (w, h))
sorted_img.putdata(sorted_vals)
sorted_path = os.path.join(out_dir, f"{base}_sorted_pixels_ascending.png")
sorted_img.save(sorted_path)
sorted_disk_kb = round(os.path.getsize(sorted_path) / 1024, 2)

# ============================================================
# (3) CARI INTENSITAS TERBESAR (max1) DAN TERBESAR KE-2 (max2)
# ============================================================

found_max1 = False
found_max2 = False
max1 = 0
max2 = 0

val = 255  # mulai dari intensitas paling besar
while val >= 0:
    if count[val] > 0:
        if not found_max1:
            max1 = val
            found_max1 = True
        elif (not found_max2) and (val != max1):
            max2 = val
            found_max2 = True
            break
    val -= 1

# kalau cuma ada 1 intensitas unik, max2 tidak ketemu
if not found_max2:
    max2 = max1


# ============================================================
# (4) AMBIL KOORDINAT PIXEL YANG NILAINYA == max2
# ============================================================
# Di sini kita perlu balik lagi ke koordinat (x,y) untuk tau posisi pixel.
# mencari lokasi intensitas max2.

pixels_max2 = []

# LOOP 5: scan semua koordinat pixel untuk CARI POSISI yang gray[i]==max2
for y in range(h):
    row_base = y * w                 
    for x in range(w):
        i = row_base + x            
        if gray[i] == max2:
            pixels_max2.append((x, y))

# ============================================================
# (5) BUAT MASK IMAGE
# ============================================================

mask = [0] * n

# LOOP 6: loop semua koordinat yang tadi ditemukan (pixels_max2)
for (x, y) in pixels_max2:
    mask[y * w + x] = 255         

# Simpan mask image
mask_img = Image.new("L", (w, h))
mask_img.putdata(mask)
mask_path = os.path.join(out_dir, f"{base}_mask_second_max.png")
mask_img.save(mask_path)
mask_disk_kb = round(os.path.getsize(mask_path) / 1024, 2)

# ============================================================
# (6) BUAT REPORT TXT
# ============================================================
rep_path = os.path.join(out_dir, f"{base}_report_segmentasi_sort.txt")
with open(rep_path, "w", encoding="utf-8") as f:
    f.write("SEGMENTASI BERDASARKAN INTENSITAS (URUT PIXEL) - GRAYSCALE 8-BIT\n")
    f.write("================================================================\n\n")

    f.write("1) Properti Citra\n")
    f.write(f"Nama Citra      : {nama}\n")
    f.write(f"Format          : {format_file}\n")
    f.write(f"Resolusi        : {w} x {h}\n")
    f.write(f"Jumlah Piksel   : {n}\n")
    f.write(f"Intensitas min  : {min_val}\n")
    f.write(f"Intensitas max  : {max_val}\n")
    f.write(f"Ukuran File     : {ukuran_file_kb} KB\n\n")

    f.write("2) Rumus Grayscale\n")
    f.write("I = 0.299R + 0.587G + 0.114B\n\n")

    f.write("3) Intensitas Terbesar\n")
    f.write(f"Terbesar (max1)        : {max1}\n")
    f.write(f"Terbesar ke-2 (max2)   : {max2}\n")
    f.write(f"Jumlah pixel max2      : {len(pixels_max2)}\n\n")

    f.write("4) Koordinat Pixel Intensitas Terbesar Ke-2\n")
    for (x, y) in pixels_max2:
        f.write(f"(x={x}, y={y})\n")

    f.write("\n5) Output File\n")
    f.write(f"Grayscale Image        : {os.path.basename(gray_path)} ({gray_disk_kb} KB)\n")
    f.write(f"Sorted Image           : {os.path.basename(sorted_path)} ({sorted_disk_kb} KB)\n")
    f.write(f"Mask Second Max Image  : {os.path.basename(mask_path)} ({mask_disk_kb} KB)\n")
    f.write(f"Report TXT             : {os.path.basename(rep_path)}\n")

# ============================================================
# OUTPUT CONSOLE
# ============================================================
print("\n=== HASIL AKHIR ===")
print("Resolusi                 :", w, "x", h)
print("Intensitas terbesar      :", max1)
print("Intensitas terbesar ke-2 :", max2)
print("Jumlah pixel max ke-2    :", len(pixels_max2))
print("Grayscale image          :", gray_path)
print("Sorted image             :", sorted_path)
print("Mask second max image    :", mask_path)
print("Report TXT               :", rep_path)
print("\nSelesai. Semua output ada di folder:", out_dir)
