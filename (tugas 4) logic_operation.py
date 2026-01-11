from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os

# ====================== 1. INPUT GAMBAR ======================
gambar_A = input("Masukkan file gambar A: ").strip()
gambar_B = input("Masukkan file gambar B: ").strip()

try:
    A = Image.open(gambar_A)
    B = Image.open(gambar_B)
except:
    print("File tidak ditemukan! Pastikan nama file benar.")
    exit()

# ====================== 2. SAMAKAN UKURAN (ke ukuran terkecil) ======================
# Pilihan ini dipakai agar tidak otomatis memperbesar satu gambar sehingga kehilangan detail.
# Cara: ambil ukuran terkecil dari kedua gambar lalu resize kedua gambar ke ukuran (w,h) tersebut.
if A.size != B.size:
    print("\nUkuran gambar berbeda — disesuaikan otomatis ke ukuran terkecil.")
    w = min(A.width, B.width)
    h = min(A.height, B.height)
    A = A.resize((w, h))
    B = B.resize((w, h))
else:
    w, h = A.size

# ====================== 3. DETEKSI MODE WARNA & PROPERTI CITRA ======================
# Kita deteksi mode warna berdasarkan array numpy (jika semua channel sama -> grayscale).
# Lalu tampilkan properti sesuai format yang diinginkan (tanpa fungsi).
img_array_A = np.array(A)
if len(img_array_A.shape) == 2:
    modeA = "Grayscale"
    bandsA = ["L"]
elif img_array_A.shape[2] == 3 and np.array_equal(img_array_A[:,:,0], img_array_A[:,:,1]) and np.array_equal(img_array_A[:,:,1], img_array_A[:,:,2]):
    modeA = "Grayscale"
    bandsA = ["L"]
else:
    modeA = "RGB"
    bandsA = ["R","G","B"]

img_array_B = np.array(B)
if len(img_array_B.shape) == 2:
    modeB = "Grayscale"
    bandsB = ["L"]
elif img_array_B.shape[2] == 3 and np.array_equal(img_array_B[:,:,0], img_array_B[:,:,1]) and np.array_equal(img_array_B[:,:,1], img_array_B[:,:,2]):
    modeB = "Grayscale"
    bandsB = ["L"]
else:
    modeB = "RGB"
    bandsB = ["R","G","B"]

formatA = os.path.splitext(gambar_A)[1].upper()
formatB = os.path.splitext(gambar_B)[1].upper()
ukuranA_kb = round(os.path.getsize(gambar_A) / 1024, 2)
ukuranB_kb = round(os.path.getsize(gambar_B) / 1024, 2)
rasioA = round(w / h, 2)
rasioB = round(w / h, 2)  # setelah resize ukuran sama

print("\n======================= PROPERTI CITRA =======================")
print(f"Nama Citra           : Citra A")
print(f"- Format file        : {formatA}")
print(f"- Mode warna         : {modeA}")
print(f"- Resolusi           : {w} x {h} piksel (lebar x tinggi)")
print(f"- Jumlah kanal warna : {len(bandsA)} ({', '.join(bandsA)})")
print(f"- Kedalaman warna    : 8 bit per kanal")
print(f"- Rasio aspek        : {rasioA}")
print(f"- Ukuran file        : {ukuranA_kb} KB")
print("==============================================================\n")

# ====================== 4. KONVERSI KE GRAYSCALE (jika perlu) & BINARISASI ======================
# Modul mengilustrasikan operasi logika pada citra biner (hitam-putih).
# Jadi kita konversi ke grayscale dulu (jika RGB) lalu threshold ke biner.
A_gray = A.convert("L")
B_gray = B.convert("L")

# Threshold yang dipakai: 128 (nilai tengah 0-255)
threshold = 128
A_bin = np.where(np.array(A_gray) > threshold, 255, 0).astype(np.uint8)
B_bin = np.where(np.array(B_gray) > threshold, 255, 0).astype(np.uint8)

# ====================== 5. RUMUS OPERASI LOGIKA ======================
## RUMUS MODUL:
## C(x,y) = A(x,y) AND B(x,y)   -> 1 only if A=1 and B=1
## C(x,y) = A(x,y) OR  B(x,y)   -> 1 if A=1 or B=1 or both
## C(x,y) = A(x,y) XOR B(x,y)   -> 1 if A != B
## C(x,y) = A SUB B (A - B)     -> A - B if A >= B, else 0
## C(x,y) = NOT A(x,y)          -> inverse: 1 -> 0, 0 -> 1  (in grayscale: 255 - A)

# Karena kita pakai biner 0/255, kita implementasikan dengan operasi numpy/logika.
# Perhatikan: kita gunakan nilai 0 dan 255 untuk hasil.

# ====================== 6. PENERAPAN RUMUS KE KODE ======================
C_AND = (np.logical_and(A_bin, B_bin) * 255).astype(np.uint8)
C_OR  = (np.logical_or(A_bin, B_bin) * 255).astype(np.uint8)
C_XOR = (np.logical_xor(A_bin, B_bin) * 255).astype(np.uint8)
# SUB: jika A >= B -> A-B, else 0
C_SUB = np.where(A_bin >= B_bin, (A_bin.astype(int) - B_bin.astype(int)), 0).astype(np.uint8)
# NOT A
C_NOTA = (np.logical_not(A_bin) * 255).astype(np.uint8)
C_NOTB = (np.logical_not(B_bin) * 255).astype(np.uint8)

# ====================== 7. SIMPAN HASIL ======================
os.makedirs("logic_operation_result", exist_ok=True)
Image.fromarray(A_bin).save("logic_operation_result/A_binary.png")
Image.fromarray(B_bin).save("logic_operation_result/B_binary.png")
Image.fromarray(C_AND).save("logic_operation_result/A_AND_B.png")
Image.fromarray(C_OR).save("logic_operation_result/A_OR_B.png")
Image.fromarray(C_XOR).save("logic_operation_result/A_XOR_B.png")
Image.fromarray(C_SUB).save("logic_operation_result/A_SUB_B.png")
Image.fromarray(C_NOTA).save("logic_operation_result/NOT_A.png")
Image.fromarray(C_NOTB).save("logic_operation_result/NOT_B.png")

print("Semua hasil operasi logika berhasil disimpan di folder 'logic_operation_result'!\n")

# ====================== 8. TAMPILKAN SEMUA HASIL (PLT) ======================
plt.figure("OPERASI LOGIKA CITRA", figsize=(10, 8))

plt.subplot(3, 3, 1)
plt.imshow(A_bin, cmap="gray")
plt.title("Citra A (Biner)")
plt.axis("off")

plt.subplot(3, 3, 2)
plt.imshow(B_bin, cmap="gray")
plt.title("Citra B (Biner)")
plt.axis("off")

plt.subplot(3, 3, 3)
plt.imshow(C_AND, cmap="gray")
plt.title("A AND B")
plt.axis("off")

plt.subplot(3, 3, 4)
plt.imshow(C_OR, cmap="gray")
plt.title("A OR B")
plt.axis("off")

plt.subplot(3, 3, 5)
plt.imshow(C_XOR, cmap="gray")
plt.title("A XOR B")
plt.axis("off")

plt.subplot(3, 3, 6)
plt.imshow(C_SUB, cmap="gray")
plt.title("A SUB B")
plt.axis("off")

plt.subplot(3, 3, 7)
plt.imshow(C_NOTA, cmap="gray")
plt.title("NOT A")
plt.axis("off")

plt.subplot(3, 3, 8)
plt.imshow(C_NOTB, cmap="gray")
plt.title("NOT B")
plt.axis("off")

plt.tight_layout()
plt.show()
