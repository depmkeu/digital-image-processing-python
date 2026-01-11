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

# Paksa input jadi RGB 
img_rgb = img_pil.convert("RGB")
arr_rgb = np.array(img_rgb)

w, h = img_rgb.size
nama = os.path.basename(path)
format_file = os.path.splitext(path)[1].upper()
ukuran_file_kb = round(os.path.getsize(path) / 1024, 2)
rasio_aspek = round(w / h, 6)

print("\n======================= PROPERTI CITRA =======================")
print(f"Nama Citra            : {nama}")
print(f"- Format file         : {format_file}")
print(f"- Resolusi            : {w} x {h} (lebar x tinggi)")
print(f"- Rasio aspek         : {rasio_aspek}")
print(f"- Ukuran file (disk)  : {ukuran_file_kb} KB")
print("==============================================================\n")

# ===============================
# INPUT PARAMETER
# ===============================
alpha = float(input("Masukkan nilai alpha (α): ").strip())
mask_type = input("Pilih mask (5 = lima titik, 9 = sembilan titik): ").strip()

# ===============================
# Mask 5 titik:
# [ 0   -α   0 ]
# [ -α 1+4α -α ]
# [ 0   -α   0 ]
#
# Mask 9 titik:
# [ -α  -α  -α ]
# [ -α 1+8α -α ]
# [ -α  -α  -α ]
# ===============================
if mask_type == "5":
    kernel = np.array([
        [0,        -alpha, 0],
        [-alpha, 1 + 4*alpha, -alpha],
        [0,        -alpha, 0]
    ], dtype=np.float32)
elif mask_type == "9":
    kernel = np.array([
        [-alpha, -alpha, -alpha],
        [-alpha, 1 + 8*alpha, -alpha],
        [-alpha, -alpha, -alpha]
    ], dtype=np.float32)
else:
    print("Pilihan mask tidak valid!")
    raise SystemExit

# ===============================
# KONVERSI KE GRAYSCALE 
# ===============================
gray = np.array(img_rgb.convert("L"), dtype=np.float32)
H, W = gray.shape

# siapkan output, mulai dari copy input (biar border aman, tidak hitam)
sharpened = gray.copy()

# ===============================
# SHARPENING (MANUAL)
# h(x,y) = ΣΣ f(x+i, y+j) * w(i,j)
# ===============================
for y in range(1, H-1):
    for x in range(1, W-1):
        total = 0.0

        total += kernel[0,0] * gray[y-1, x-1]
        total += kernel[0,1] * gray[y-1, x]
        total += kernel[0,2] * gray[y-1, x+1]

        total += kernel[1,0] * gray[y,   x-1]
        total += kernel[1,1] * gray[y,   x]
        total += kernel[1,2] * gray[y,   x+1]

        total += kernel[2,0] * gray[y+1, x-1]
        total += kernel[2,1] * gray[y+1, x]
        total += kernel[2,2] * gray[y+1, x+1]

        sharpened[y, x] = total

# batasi ke 0..255 (citra 8-bit)
sharpened_u8 = np.clip(sharpened, 0, 255).astype(np.uint8)

# ===============================
# SIMPAN OUTPUT
# ===============================
os.makedirs("sharpening_result", exist_ok=True)
base = os.path.splitext(os.path.basename(path))[0]
alpha_str = str(alpha).replace(".", "_")
out_path = f"sharpening_result/{base}_sharpen_mask{mask_type}_alpha{alpha_str}.png"

Image.fromarray(sharpened_u8).save(out_path)

print("Hasil penajaman disimpan:", out_path)

# ===============================
# TAMPILKAN
# ===============================
plt.figure(figsize=(12, 4))

plt.subplot(1, 3, 1)
plt.imshow(img_rgb)
plt.title("Citra Asli (RGB)")
plt.axis("off")

plt.subplot(1, 3, 2)
plt.imshow(gray.astype(np.uint8), cmap="gray")
plt.title("Citra Grayscale (Input Proses)")
plt.axis("off")

plt.subplot(1, 3, 3)
plt.imshow(sharpened_u8, cmap="gray")
plt.title(f"Sharpening (Mask {mask_type}, α={alpha})")
plt.axis("off")

plt.tight_layout()
plt.show()
