import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import os
import math

# ===============================
# INPUT + BACA CITRA
# ===============================
image_path = input("Masukkan path citra: ").strip()

try:
    img_pil = Image.open(image_path)
except:
    print("File tidak ditemukan!")
    raise SystemExit

# Paksa semua input (RGB/RGBA/dll) jadi grayscale 8-bit (0..255)
img_gray = img_pil.convert("L")
img = np.array(img_gray, dtype=np.uint8)

h, w = img.shape
n = h * w

# ===============================
# OUTPUT FOLDER
# ===============================
out_dir = "huffman_result"
os.makedirs(out_dir, exist_ok=True)

base = os.path.splitext(os.path.basename(image_path))[0]
nama = os.path.basename(image_path)
format_file = os.path.splitext(image_path)[1].upper()
ukuran_file_kb = round(os.path.getsize(image_path) / 1024, 2)
rasio_aspek = round(w / h, 6)
min_val = int(img.min())
max_val = int(img.max())

# ===============================
# HITUNG FREKUENSI nk dan P(k)=nk/n
# ===============================
freq = {}
for y in range(h):
    for x in range(w):
        v = int(img[y, x])
        if v in freq:
            freq[v] += 1
        else:
            freq[v] = 1

symbols = sorted(freq.keys())
L = len(symbols)

prob = {}
for k in symbols:
    prob[k] = freq[k] / n

# ===============================
# UKURAN SEBELUM KOMPRESI (bit)
# grayscale 8-bit -> ukuran asli = n * 8
# ===============================
original_bits = n * 8

# ===============================
# NODE HUFFMAN
# ===============================
class Node:
    def __init__(self, value, freq):
        self.value = value
        self.freq = freq
        self.left = None
        self.right = None

nodes = []
for k in symbols:
    nodes.append(Node(k, freq[k]))

# ===============================
# BANGUN POHON HUFFMAN 
# gabung 2 frekuensi terkecil berulang
# yang kecil di kiri
# ===============================
if len(nodes) == 1:
    root = nodes[0]
else:
    while len(nodes) > 1:
        nodes.sort(key=lambda x: x.freq)
        left = nodes.pop(0)
        right = nodes.pop(0)

        parent = Node(None, left.freq + right.freq)
        parent.left = left
        parent.right = right
        nodes.append(parent)

    root = nodes[0]

# ===============================
# BUAT KODE BINER
# kiri=0, kanan=1
# ===============================
codes = {}
stack = [(root, "")]

while len(stack) > 0:
    node, code = stack.pop()

    if node.value is not None:
        codes[node.value] = code if code != "" else "0"
    else:
        if node.right is not None:
            stack.append((node.right, code + "1"))
        if node.left is not None:
            stack.append((node.left, code + "0"))

# ===============================
# UKURAN HASIL KOMPRESI (bit)
# Ukuran hasil = Σ (nk * panjang_kode)
# ===============================
compressed_bits = 0
for k in symbols:
    compressed_bits += freq[k] * len(codes[k])

# ===============================
# PENGHEMATAN (sesuai bentuk modul)
# Penghematan(%) = 100% - (UkuranHasil/UkuranAsli * 100%)
# + Compression Ratio (CR) = UkuranAsli / UkuranHasil
# ===============================
saving_percent = 100.0 - ((compressed_bits / original_bits) * 100.0)
cr = (original_bits / compressed_bits) if compressed_bits != 0 else 0.0

# ===============================
# ENCODE -> bitstream (internal, tidak disimpan)
# ===============================
bit_parts = []
for y in range(h):
    for x in range(w):
        bit_parts.append(codes[int(img[y, x])])
bitstream = "".join(bit_parts)

# ===============================
# DECODE (rekonstruksi) - telusuri pohon (manual)
# ===============================
decoded = np.zeros((h, w), dtype=np.uint8)
idx = 0
node = root

for y in range(h):
    for x in range(w):
        while node.value is None:
            b = bitstream[idx]
            idx += 1
            if b == "0":
                node = node.left
            else:
                node = node.right
        decoded[y, x] = node.value
        node = root

lossless_ok = np.array_equal(decoded, img)

# ===============================
# SIMPAN GAMBAR HASIL REKONSTRUKSI (decode)
# ===============================
out_img_path = os.path.join(out_dir, f"{base}_decoded_huffman.png")
Image.fromarray(decoded).save(out_img_path)
decoded_disk_kb = round(os.path.getsize(out_img_path) / 1024, 2)

# ===============================
# SIMPAN TXT (tabel rapi)
# ===============================
out_txt_path = os.path.join(out_dir, f"{base}_huffman_report.txt")

with open(out_txt_path, "w", encoding="utf-8") as f:
    f.write("STATISTICAL COMPRESSION – HUFFMAN CODING (LOSSLESS)\n")
    f.write("===================================================\n\n")

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
    f.write(f"| Jumlah Simbol Unik (L)     | {L:<28} |\n")
    f.write("+---------------------------+------------------------------+\n\n")

    # 2) Frekuensi & peluang
    f.write("2) Frekuensi & Peluang (nk dan P(k)=nk/n)\n")
    f.write("+----------+------------+------------+\n")
    f.write("| k        | nk         | P(k)       |\n")
    f.write("+----------+------------+------------+\n")
    for k in symbols:
        f.write(f"| {k:8d} | {freq[k]:10d} | {prob[k]:10.6f} |\n")
    f.write("+----------+------------+------------+\n\n")

    # 3) Kode Huffman
    f.write("3) Kode Huffman (kiri=0, kanan=1)\n")
    f.write("+----------+------------------------------+--------------+------------+\n")
    f.write("| k        | kode                         | panjang(bit) | nk         |\n")
    f.write("+----------+------------------------------+--------------+------------+\n")
    for k in sorted(symbols, key=lambda x: (len(codes[x]), x)):
        code = codes[k]
        f.write(f"| {k:8d} | {code:<28} | {len(code):12d} | {freq[k]:10d} |\n")
    f.write("+----------+------------------------------+--------------+------------+\n\n")

    # 4) Ukuran data + rumus modul
    f.write("4) Ukuran Data (bit)\n")
    f.write("+---------------------------------------------+------------------+\n")
    f.write(f"| Ukuran citra sebelum (n x 8 bit)            | {original_bits:16d} |\n")
    f.write(f"| Ukuran citra sesudah (Σ nk x panjang_kode)  | {compressed_bits:16d} |\n")
    f.write("+---------------------------------------------+------------------+\n\n")

    f.write("Penghematan (rumus):\n")
    f.write("P  = 100% - (UkuranHasil/UkuranAsli * 100%)\n")
    f.write(f"  = 100% - ({compressed_bits}/{original_bits} * 100%)\n")
    f.write(f"  = {saving_percent:.2f}%\n\n")

    f.write("Compression Ratio (CR):\n")
    f.write("CR  = UkuranAsli / UkuranHasil\n")
    f.write(f"   = {original_bits} / {compressed_bits}\n")
    f.write(f"   = {cr:.4f}\n\n")

    # 5) Output
    f.write("5) Output (rekonstruksi / decode)\n")
    f.write("+-----------------------------------+------------------------------+\n")
    f.write(f"| Gambar hasil decode (PNG)         | {out_img_path:<28} |\n")
    f.write(f"| Ukuran file hasil (disk)          | {(str(decoded_disk_kb)+' KB'):<28} |\n")
    f.write("+-----------------------------------+------------------------------+\n\n")

    # 6) Verifikasi
    f.write("6) Verifikasi Lossless\n")
    f.write(f"- Decode == Input grayscale : {'YA (lossless)' if lossless_ok else 'TIDAK'}\n")

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

print("\n=== HASIL KOMPRESI HUFFMAN ===")
print(f"Ukuran sebelum  : n x 8 = {n} x 8 = {original_bits} bit")
print(f"Ukuran sesudah  : Σ(nk x panjang_kode) = {compressed_bits} bit")
print("Penghematan(%)  : 100% - (UkuranHasil/UkuranAsli * 100%)")
print(f"                = 100% - ({compressed_bits}/{original_bits} * 100%)")
print(f"                = {saving_percent:.2f}%")
print(f"CR (Asli/Hasil) : {cr:.4f}")
print("================================")

print("\nSelesai.")
print("TXT tersimpan   :", out_txt_path)
print("Gambar tersimpan:", out_img_path)
print("Cek lossless    :", "OK" if lossless_ok else "GAGAL")

# ===============================
# TAMPILKAN GAMBAR
# ===============================
plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
plt.imshow(img, cmap="gray")
plt.title("Citra Input (Grayscale)")
plt.axis("off")

plt.subplot(1, 2, 2)
plt.imshow(decoded, cmap="gray")
plt.title("Citra Hasil Huffman")
plt.axis("off")

plt.tight_layout()
plt.show()
