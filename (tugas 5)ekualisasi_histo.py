from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os

# ========================= 1. INPUT GAMBAR ============================
gambar_path = input("Masukkan nama file gambar: ").strip()

try:
    img = Image.open(gambar_path)
except:
    print("File tidak ditemukan! Pastikan nama file benar.")
    exit()

# ========================= 2. AMBIL INFORMASI FILE =====================
nama = os.path.basename(gambar_path)
format_file = img.format
mode_awal = img.mode
ukuran_file_kb = round(os.path.getsize(gambar_path) / 1024, 2)

# ========================= 3. KONVERSI KE ARRAY ========================
img_array_awal = np.array(img)

# ========================= 4. DETEKSI MODE WARNA OTOMATIS ==============
# Jika shape 2 dimensi → pasti grayscale
if len(img_array_awal.shape) == 2:
    mode = "Grayscale"
    bands = ["L"]

# Jika RGB tetapi ketiga kanal sama → grayscale terselubung
elif img_array_awal.shape[2] == 3 and \
     np.array_equal(img_array_awal[:,:,0], img_array_awal[:,:,1]) and \
     np.array_equal(img_array_awal[:,:,1], img_array_awal[:,:,2]):
    mode = "Grayscale"
    bands = ["L"]

# Jika tidak → RGB asli
else:
    mode = "RGB"
    bands = ["R", "G", "B"]

# Rasio aspek
w, h = img.size
rasio_aspek = round(w / h, 2)

# ========================= 5. CETAK PROPERTI CITRA =====================
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

# ========================= 6. PASTIKAN GRAYSCALE =======================
# Histogram equalization hanya berlaku pada grayscale
if mode == "RGB":
    print("Citra RGB terdeteksi → dikonversi menjadi grayscale dengan metode rata-rata.")
    img = img.convert("L")

img_array = np.array(img)
w, h = img.size
total_pixel = w * h

# ========================= 7. HITUNG HISTOGRAM =========================
# hist[i] = jumlah piksel yg bernilai i (0–255)
hist, bins = np.histogram(img_array.flatten(), bins=256, range=[0, 256])

# ========================= 8. DISTRIBUSI KUMULATIF ======================
# Ci = ∑ histogram hingga i
cum_hist = hist.cumsum()

# ======================= 9. RUMUS EKUALISASI ==================
# Ko = round( (Ci / (w*h)) * (2^8 - 1) )
# Ko = round( Ci * 255 / total_pixel )
equalized_map = np.round((cum_hist * 255) / total_pixel).astype(np.uint8)

# ========================= 10. BENTUK CITRA HASIL ======================
equalized_img = equalized_map[img_array]

# ========================= 11. SIMPAN HASIL =============================
os.makedirs("equalization_result", exist_ok=True)
result_path = "equalization_result/histogram_equalized.png"
Image.fromarray(equalized_img).save(result_path)

# ========================= 12. CETAK TABEL PERHITUNGAN =================
print("\n=== TABEL PERHITUNGAN HISTOGRAM EKUALISASI ===")
print(f"{'Nilai Keabuan (i)':<20}{'Frekuensi (Ci)':<20}{'Distribusi Kumulatif':<25}{'Nilai Baru (Ko)':<15}")
print("-" * 80)

for i in range(256):
    if hist[i] > 0:
        print(f"{i:<20}{hist[i]:<20}{cum_hist[i]:<25}{equalized_map[i]:<15}")

# ========================= 13. TAMPILKAN GRAFIK =========================
plt.figure("Ekualisasi Histogram", figsize=(12, 6))

# Citra Asli
plt.subplot(2, 2, 1)
plt.imshow(img, cmap='gray')
plt.title("Citra Asli (Grayscale)")
plt.axis("off")

# Histogram Asli
plt.subplot(2, 2, 2)
plt.plot(hist)
plt.title("Histogram Asli")

# Citra Hasil
plt.subplot(2, 2, 3)
plt.imshow(equalized_img, cmap='gray')
plt.title("Citra Hasil Ekualisasi")
plt.axis("off")

# Histogram Hasil
plt.subplot(2, 2, 4)
hist_equalized = np.histogram(equalized_img.flatten(), bins=256, range=[0,256])[0]
plt.plot(hist_equalized)
plt.title("Histogram Setelah Ekualisasi")

plt.tight_layout()
plt.show()

print(f"\nHasil ekualisasi histogram disimpan di: {result_path}")
