from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os

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

# Paksa grayscale
img_gray_pil = img_pil.convert("L")
img = np.array(img_gray_pil, dtype=np.uint8)

h, w = img.shape
n = h * w

# ===============================
# OUTPUT FOLDER
# ===============================
out_dir = "smoothing_result"
os.makedirs(out_dir, exist_ok=True)

base = os.path.splitext(os.path.basename(path))[0]
nama = os.path.basename(path)
format_file = os.path.splitext(path)[1].upper()
ukuran_file_kb = round(os.path.getsize(path) / 1024, 2)
rasio_aspek = round(w / h, 6)
min_val = int(img.min())
max_val = int(img.max())

# ===============================
# PILIH MASK 
# ===============================
print("Pilih mask smoothing:")
print("1. 5 titik bertetangga (cross) bobot 1/5")
print("2. 9 titik bertetangga (3x3) bobot 1/9")
print("3. 25 titik bertetangga (5x5) bobot 1/25")
pilih = input("Masukkan pilihan (1/2/3): ").strip()

if pilih == "1":
    kernel = np.array([
        [0,   1/5, 0],
        [1/5, 1/5, 1/5],
        [0,   1/5, 0]
    ], dtype=np.float32)
    mask_name = "5-titik (cross), bobot 1/5"
elif pilih == "2":
    kernel = np.full((3, 3), 1/9, dtype=np.float32)
    mask_name = "9-titik (3x3), bobot 1/9"
elif pilih == "3":
    kernel = np.full((5, 5), 1/25, dtype=np.float32)
    mask_name = "25-titik (5x5), bobot 1/25"
else:
    print("Pilihan tidak valid!")
    raise SystemExit

kH, kW = kernel.shape
pad_y, pad_x = kH // 2, kW // 2

# ===============================
# SMOOTHING (KONVOLUSI)
# h(x,y) = ΣΣ f(x+i,y+j) * w(i,j)
# padding = edge supaya border tidak jadi 0
# ===============================
padded = np.pad(img, ((pad_y, pad_y), (pad_x, pad_x)), mode="edge")
out = np.zeros((h, w), dtype=np.float32)

for y in range(h):
    for x in range(w):
        total = 0.0
        for ky in range(kH):
            for kx in range(kW):
                total += float(padded[y + ky, x + kx]) * float(kernel[ky, kx])
        out[y, x] = total

out_u8 = np.clip(out, 0, 255).astype(np.uint8)

# ===============================
# CONTOH HITUNG 1 TITIK
# default: titik tengah citra
# ===============================
cy, cx = h // 2, w // 2  # (y,x) 0-based
# ambil window di padded
wy0, wx0 = cy, cx
window = padded[wy0:wy0 + kH, wx0:wx0 + kW]

terms = []
sum_detail = 0.0
for ky in range(kH):
    for kx in range(kW):
        wgt = float(kernel[ky, kx])
        if wgt != 0.0:  # untuk cross 5-titik: 0 tdk ikut
            pix = int(window[ky, kx])
            val = pix * wgt
            sum_detail += val
            terms.append((pix, wgt, val))

contoh_h = int(round(sum_detail))  # dibulatkan
nilai_asli = int(img[cy, cx])
nilai_hasil = int(out_u8[cy, cx])

# ===============================
# SIMPAN GAMBAR OUTPUT
# ===============================
out_img_path = os.path.join(out_dir, f"{base}_smooth_{kH}x{kW}.png")
Image.fromarray(out_u8).save(out_img_path)
hasil_disk_kb = round(os.path.getsize(out_img_path) / 1024, 2)

# ===============================
# SIMPAN TXT (TABEL RAPI, SESUAI MODUL)
# ===============================
out_txt_path = os.path.join(out_dir, f"{base}_smoothing_report.txt")

with open(out_txt_path, "w", encoding="utf-8") as f:
    f.write("PENGHALUSAN CITRA (SMOOTHING)\n")
    f.write("==============================================\n\n")

    # 1) Properti citra
    f.write("1) Properti Citra (Input)\n")
    f.write("+---------------------------+------------------------------+\n")
    f.write(f"| Nama Citra                 | {nama:<28} |\n")
    f.write(f"| Format File                | {format_file:<28} |\n")
    f.write(f"| Mode asli (sebelum)        | {mode_asli:<28} |\n")
    f.write(f"| Mode proses (dipakai)      | {'Grayscale (L) 8-bit':<28} |\n")
    f.write(f"| Resolusi (w x h)           | {(str(w)+' x '+str(h)):<28} |\n")
    f.write(f"| Jumlah piksel (n)          | {n:<28} |\n")
    f.write(f"| Derajat keabuan (min..max) | {(str(min_val)+' .. '+str(max_val)):<28} |\n")
    f.write(f"| Rasio aspek (w/h)          | {str(rasio_aspek):<28} |\n")
    f.write(f"| Ukuran file input (disk)   | {(str(ukuran_file_kb)+' KB'):<28} |\n")
    f.write("+---------------------------+------------------------------+\n\n")

    # 2) Mask
    f.write("2) Mask Smoothing\n")
    f.write("+---------------------------+------------------------------+\n")
    f.write(f"| Jenis mask                 | {mask_name:<28} |\n")
    f.write(f"| Ukuran mask                | {str(kH)+' x '+str(kW):<28} |\n")
    f.write("+---------------------------+------------------------------+\n\n")

    # 3) Kernel
    f.write("3) Kernel (bobot)\n")
    for row in kernel:
        f.write(" ".join(f"{v:.5f}" for v in row) + "\n")
    f.write("\n")

    # 4) Contoh perhitungan 1 titik
    f.write("4) Contoh Perhitungan 1 Titik\n")
    f.write(f"Titik contoh (y,x) = ({cy},{cx}) [0-based], pusat window\n")
    f.write(f"Nilai f(y,x) asli  = {nilai_asli}\n\n")

    f.write("+----------+----------+--------------+\n")
    f.write("| f(i,j)   | bobot    | f(i,j)*bobot |\n")
    f.write("+----------+----------+--------------+\n")
    for pix, wgt, val in terms:
        f.write(f"| {pix:8d} | {wgt:8.5f} | {val:12.5f} |\n")
    f.write("+----------+----------+--------------+\n")
    f.write(f"Σ = {sum_detail:.5f}\n")
    f.write(f"h(y,x) = round(Σ) = {contoh_h}\n")
    f.write(f"Nilai output di citra hasil (posisi sama) = {nilai_hasil}\n\n")

    # 5) Output
    f.write("5) Output\n")
    f.write("+-----------------------------------+------------------------------+\n")
    f.write(f"| Gambar hasil smoothing (PNG)      | {out_img_path:<28} |\n")
    f.write(f"| Ukuran file hasil (disk)          | {(str(hasil_disk_kb)+' KB'):<28} |\n")
    f.write("+-----------------------------------+------------------------------+\n")

# ===============================
# OUTPUT CONSOLE
# ===============================
print("\n======================= PROPERTI CITRA =======================")
print(f"Nama Citra            : {nama}")
print(f"- Format file         : {format_file}")
print(f"- Mode asli           : {mode_asli}")
print(f"- Mode proses         : Grayscale (L) 8-bit")
print(f"- Resolusi            : {w} x {h} (lebar x tinggi)")
print(f"- Jumlah piksel (n)   : {n}")
print(f"- Derajat keabuan     : {min_val} .. {max_val}")
print(f"- Ukuran file (disk)  : {ukuran_file_kb} KB")
print("==============================================================")

print("\n=== HASIL SMOOTHING ===")
print(f"Mask: {mask_name} | Kernel: {kH}x{kW}")
print(f"Contoh titik (y,x)=({cy},{cx}) -> f={nilai_asli}, h={nilai_hasil}")
print("TXT tersimpan   :", out_txt_path)
print("Gambar tersimpan:", out_img_path)

# ===============================
# TAMPILKAN GAMBAR
# ===============================
plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
plt.imshow(img, cmap="gray")
plt.title("Citra Asli (Grayscale)")
plt.axis("off")

plt.subplot(1, 2, 2)
plt.imshow(out_u8, cmap="gray")
plt.title(f"Hasil Smoothing ({kH}x{kW})")
plt.axis("off")

plt.tight_layout()
plt.show()
