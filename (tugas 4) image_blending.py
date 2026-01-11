from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os

# === INPUT GAMBAR ===
gambar_A = input("Masukkan file gambar A: ").strip()
gambar_B = input("Masukkan file gambar B: ").strip()

try:
    A = Image.open(gambar_A).convert("RGB")
    B = Image.open(gambar_B).convert("RGB")
except:
    print("File tidak ditemukan! Pastikan nama file benar.")
    exit()

# === CEK DAN SESUAIKAN UKURAN (AUTO RESIZE) ===
if A.size != B.size:
    print("Ukuran gambar berbeda — disesuaikan otomatis ke ukuran terkecil.")
    w = min(A.width, B.width)
    h = min(A.height, B.height)
    A = A.resize((w, h))
    B = B.resize((w, h))
else:
    w, h = A.size

# === TAMPILKAN PROPERTI CITRA ===
def tampilkan_properti(gambar, nama, path):
    img_array = np.array(gambar)
    w, h = gambar.size
    format_file = os.path.splitext(path)[1].upper()
    ukuran_file_kb = round(os.path.getsize(path) / 1024, 2)

    # Deteksi mode warna
    if len(img_array.shape) == 2:
        mode = "Grayscale"
        bands = ["L"]
    elif img_array.shape[2] == 3 and np.array_equal(img_array[:,:,0], img_array[:,:,1]) and np.array_equal(img_array[:,:,1], img_array[:,:,2]):
        mode = "Grayscale"
        bands = ["L"]
    else:
        mode = "RGB"
        bands = ["R", "G", "B"]

    rasio_aspek = round(w / h, 2)
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

# === TAMPILKAN PROPERTI KEDUA CITRA ===
tampilkan_properti(A, "Citra A", gambar_A)
tampilkan_properti(B, "Citra B", gambar_B)

# === INPUT BOBOT ===
# bobot di masukkan di A saja, klo mau di keduanya nanti ubah
try:
    wa = float(input("Masukkan bobot untuk Citra A (0–1): "))
except ValueError:
    print("Input bobot harus berupa angka desimal, misalnya 0.4")
    exit()

if not (0 <= wa <= 1):
    print("Bobot harus antara 0 dan 1.")
    exit()

wb = 1 - wa
print(f"\n Bobot diterima:")
print(f"- Bobot Citra A (wa): {wa}")
print(f"- Bobot Citra B (wb): {wb}")
print(f"- Total Bobot       : {wa + wb}\n")

# === PROSES BLENDING MANUAL ===
C = Image.new("RGB", (w, h))
for y in range(h):
    for x in range(w):
        rA, gA, bA = A.getpixel((x, y))
        rB, gB, bB = B.getpixel((x, y))

        # Rumus blending: C(x,y) = wa*A(x,y) + wb*B(x,y)
        r = int((wa * rA) + (wb * rB))
        g = int((wa * gA) + (wb * gB))
        b = int((wa * bA) + (wb * bB))

        # Batasi ke rentang 0–255
        r = min(max(r, 0), 255)
        g = min(max(g, 0), 255)
        b = min(max(b, 0), 255)

        C.putpixel((x, y), (r, g, b))

# === SIMPAN HASIL BLENDING ===
os.makedirs("blending_result", exist_ok=True)
result_path = f"blending_result/blending_wa{wa:.2f}_wb{wb:.2f}.png"
C.save(result_path)

print(f"Penggabungan citra selesai! Hasil disimpan di: {result_path}")

# === TAMPILKAN HASIL ===
plt.figure("Penggabungan Citra (Blending)", figsize=(12, 5))

plt.subplot(1, 3, 1)
plt.imshow(A)
plt.title("Citra A")
plt.axis("off")

plt.subplot(1, 3, 2)
plt.imshow(B)
plt.title("Citra B")
plt.axis("off")

plt.subplot(1, 3, 3)
plt.imshow(C)
plt.title(f"Hasil Blending (wa={wa:.2f}, wb={wb:.2f})")
plt.axis("off")

plt.tight_layout()
plt.show()
