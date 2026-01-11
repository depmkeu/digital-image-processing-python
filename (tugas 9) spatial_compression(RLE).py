import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import os

# ===============================
# INPUT + BACA CITRA
# ===============================
image_path = input("Masukkan path citra: ").strip()

try:
    img_pil = Image.open(image_path)
except:
    print("File tidak ditemukan!")
    raise SystemExit

# Paksa semua input jadi grayscale
img_gray = img_pil.convert("L")
img = np.array(img_gray, dtype=np.uint8)

h, w = img.shape
n = h * w

# ===============================
# OUTPUT FOLDER
# ===============================
out_dir = "rle_result"
os.makedirs(out_dir, exist_ok=True)

base = os.path.splitext(os.path.basename(image_path))[0]
nama = os.path.basename(image_path)
format_file = os.path.splitext(image_path)[1].upper()
ukuran_file_kb = round(os.path.getsize(image_path) / 1024, 2)
rasio_aspek = round(w / h, 6)
min_val = int(img.min())
max_val = int(img.max())

# ===============================
# BARISAN NILAI (scan baris per baris)
# ===============================
sequence = []
for y in range(h):
    for x in range(w):
        sequence.append(int(img[y, x]))

# ===============================
# RLE: hitung run-length untuk nilai yang berurutan
# runs = [(value, length), ...]
# ===============================
runs = []
if len(sequence) > 0:
    current_val = sequence[0]
    run_len = 1

    for i in range(1, len(sequence)):
        if sequence[i] == current_val:
            run_len += 1
        else:
            runs.append((current_val, run_len))
            current_val = sequence[i]
            run_len = 1
    runs.append((current_val, run_len))

# hasil encoding: v1, len1, v2, len2, ...
encoded = []
for v, ln in runs:
    encoded.append(v)
    encoded.append(ln)

# ===============================
# DECODE (rekonstruksi) -> bukti lossless RLE
# ===============================
decoded_sequence = []
for i in range(0, len(encoded), 2):
    value = encoded[i]
    length = encoded[i + 1]
    decoded_sequence.extend([value] * length)

decoded_img = np.array(decoded_sequence, dtype=np.uint8).reshape(h, w)
lossless_ok = np.array_equal(decoded_img, img)

# ===============================
# RUMUS MODUL (berbasis JUMLAH NILAI)
# sebelum: jumlah nilai = n
# sesudah: jumlah nilai encoding = 2 * jumlah_run
# ratio = 100% - (hasil/asli * 100%)
# CR = asli/hasil
# ===============================
before_count = len(sequence)           # = n
after_count = len(encoded)            # = 2*len(runs)
reduced = before_count - after_count

ratio_kompresi = 100.0 - ((after_count / before_count) * 100.0) if before_count > 0 else 0.0
cr = (before_count / after_count) if after_count > 0 else 0.0

# ===============================
# SIMPAN GAMBAR HASIL REKONSTRUKSI
# ===============================
out_img_path = os.path.join(out_dir, f"{base}_decoded_rle.png")
Image.fromarray(decoded_img).save(out_img_path)
decoded_disk_kb = round(os.path.getsize(out_img_path) / 1024, 2)

# ===============================
# HELPER: format output list panjang
# ===============================
def write_numbers(f, data, per_line=40):
    for i in range(0, len(data), per_line):
        f.write(" ".join(str(x) for x in data[i:i+per_line]) + "\n")

def write_runs(f, runs_list, per_line=12):
    for i in range(0, len(runs_list), per_line):
        f.write(" ".join(f"({v},{ln})" for v, ln in runs_list[i:i+per_line]) + "\n")

# ===============================
# SIMPAN TXT
# ===============================
out_txt_path = os.path.join(out_dir, f"{base}_rle_report.txt")

with open(out_txt_path, "w", encoding="utf-8") as f:
    f.write("SPATIAL COMPRESSION – RUN LENGTH ENCODING (RLE)\n")
    f.write("==============================================\n\n")

    # 1) Properti citra
    f.write("1) Properti Citra (Input)\n")
    f.write("+---------------------------+------------------------------+\n")
    f.write(f"| Nama Citra                 | {nama:<28} |\n")
    f.write(f"| Format File                | {format_file:<28} |\n")
    f.write(f"| Mode Proses                | {'Grayscale (L) 8-bit':<28} |\n")
    f.write(f"| Resolusi (w x h)           | {(str(w)+' x '+str(h)):<28} |\n")
    f.write(f"| Jumlah Piksel (n)          | {n:<28} |\n")
    f.write(f"| Derajat Keabuan (min..max) | {(str(min_val)+' .. '+str(max_val)):<28} |\n")
    f.write(f"| Rasio Aspek (w/h)          | {str(rasio_aspek):<28} |\n")
    f.write(f"| Ukuran File Input (disk)   | {(str(ukuran_file_kb)+' KB'):<28} |\n")
    f.write("+---------------------------+------------------------------+\n\n")

    # 2) Barisan nilai
    f.write("2) Barisan Nilai (scan baris per baris)\n")
    f.write("+---------------------------+------------------------------+\n")
    f.write(f"| Total nilai (sebelum)      | {before_count:<28} |\n")
    f.write("+---------------------------+------------------------------+\n")
    write_numbers(f, sequence)
    f.write("\n")

    # 3) Run-length
    f.write("3) Run-length (nilai, panjang)\n")
    f.write("+---------------------------+------------------------------+\n")
    f.write(f"| Total run                  | {len(runs):<28} |\n")
    f.write("+---------------------------+------------------------------+\n")
    write_runs(f, runs)
    f.write("\n")

    # 4) Hasil encoding
    f.write("4) Hasil Encoding (v1 l1 v2 l2 ...)\n")
    f.write("+---------------------------+------------------------------+\n")
    f.write(f"| Total nilai (sesudah)      | {after_count:<28} |\n")
    f.write("+---------------------------+------------------------------+\n")
    write_numbers(f, encoded)
    f.write("\n")

    # 5) Ringkasan
    f.write("5) Ringkasan\n")
    f.write("+-------------------------------------------+------------------+\n")
    f.write(f"| Ukuran citra asli (jumlah nilai)           | {before_count:16d} |\n")
    f.write(f"| Ukuran citra hasil (jumlah nilai)          | {after_count:16d} |\n")
    f.write(f"| Berkurang                                  | {reduced:16d} |\n")
    f.write(f"| Ratio = 100% - (hasil/asli x 100%)         | {ratio_kompresi:16.2f} |\n")
    f.write(f"| CR (Asli/Hasil)                            | {cr:16.4f} |\n")
    f.write("+-------------------------------------------+------------------+\n\n")

    # 6) Output + verifikasi
    f.write("6) Output\n")
    f.write("+-----------------------------------+------------------------------+\n")
    f.write(f"| Gambar hasil decode (PNG)         | {out_img_path:<28} |\n")
    f.write(f"| Ukuran file hasil (disk)          | {(str(decoded_disk_kb)+' KB'):<28} |\n")
    f.write(f"| Verifikasi (decode==input)        | {('YA (lossless)' if lossless_ok else 'TIDAK'):<28} |\n")
    f.write("+-----------------------------------+------------------------------+\n")

# ===============================
# OUTPUT CONSOLE 
# ===============================
print("\n======================= PROPERTI CITRA =======================")
print(f"Nama Citra            : {nama}")
print(f"- Format file         : {format_file}")
print(f"- Mode proses         : Grayscale (L) 8-bit")
print(f"- Resolusi            : {w} x {h} (lebar x tinggi)")
print(f"- Jumlah piksel (n)   : {n}")
print(f"- Derajat keabuan     : {min_val} .. {max_val}")
print(f"- Ukuran file (disk)  : {ukuran_file_kb} KB")
print("==============================================================")

print("\n=== HASIL KOMPRESI RLE ===")
print(f"Ukuran sebelum (jumlah nilai) : {before_count}")
print(f"Ukuran sesudah (jumlah nilai) : {after_count}")
print("Ratio = 100% - (hasil/asli * 100%)")
print(f"      = 100% - ({after_count}/{before_count} * 100%)")
print(f"      = {ratio_kompresi:.2f}%")
print(f"CR (Asli/Hasil)               : {cr:.4f}")
print("Lossless check                :", "OK" if lossless_ok else "GAGAL")
print("================================")

print("\nSelesai.")
print("TXT tersimpan   :", out_txt_path)
print("Gambar tersimpan:", out_img_path)

# ===============================
# TAMPILKAN GAMBAR
# ===============================
plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
plt.imshow(img, cmap="gray")
plt.title("Citra Input (Grayscale)")
plt.axis("off")

plt.subplot(1, 2, 2)
plt.imshow(decoded_img, cmap="gray")
plt.title("Citra Hasil RLE")
plt.axis("off")

plt.tight_layout()
plt.show()
