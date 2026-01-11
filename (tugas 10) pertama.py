import os
import math
from PIL import Image

def write_numbers(f, data, per_line=40):
    for i in range(0, len(data), per_line):
        f.write(" ".join(str(x) for x in data[i:i + per_line]) + "\n")

def write_runs(f, runs_list, per_line=12):
    for i in range(0, len(runs_list), per_line):
        f.write(" ".join(f"({v},{ln})" for v, ln in runs_list[i:i + per_line]) + "\n")

# ===============================
# INPUT
# ===============================
image_path = input("Masukkan path citra: ").strip()

try:
    img_rgb = Image.open(image_path).convert("RGB")  # I/O
except:
    print("File tidak ditemukan!")
    raise SystemExit

w, h = img_rgb.size
pix = img_rgb.load()
n = w * h

out_dir = "output_soal1"
os.makedirs(out_dir, exist_ok=True)

base = os.path.splitext(os.path.basename(image_path))[0]
nama = os.path.basename(image_path)
format_file = os.path.splitext(image_path)[1].upper()
ukuran_file_kb = round(os.path.getsize(image_path) / 1024, 2)
rasio_aspek = round(w / h, 6)

# ============================================================
# (1) GRAYSCALE 8-BIT
# Rumus: I = 0.299R + 0.587G + 0.114B
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

original_bits = n * 8

# ============================================================
# Histogram (untuk Huffman)
# freq[k] = nk
# ============================================================
freq = [0] * 256
for v in gray:
    freq[v] += 1 #jumlah kemunculan intensitas k

symbols = []
for k in range(256):
    if freq[k] > 0:
        symbols.append(k)

L = len(symbols)  # jumlah simbol unik
prob = [0.0] * 256
for k in symbols:
    prob[k] = freq[k] / n

# ============================================================
# (2) QUANTIZING (LOSSY) - uniform
# step = 256/L_new
# new = floor(old/step)
# ukuran: n*8 -> n*log2(L_new)
# ============================================================
L_new = 16 #Menentukan jumlah level baru dan bit/piksel baru
bit_new = int(round(math.log2(L_new)))
if (2 ** bit_new) != L_new:
    print("L_new harus pangkat 2 (4, 8, 16, 32, 64, 128, 256)")
    raise SystemExit

step = 256 // L_new #Menentukan lebar interval level

quant = [0] * n #Mapping hasilnya
for i in range(n):
    oldv = gray[i]
    newv = oldv // step
    if newv > (L_new - 1):
        newv = L_new - 1
    quant[i] = newv

scale = 255 // (L_new - 1) if L_new > 1 else 0
quant_view = [0] * n
for i in range(n):
    quant_view[i] = quant[i] * scale

quant_img = Image.new("L", (w, h))
quant_img.putdata(quant_view)
quant_path = os.path.join(out_dir, f"{base}_quantized_{L_new}level.png")
quant_img.save(quant_path)

quant_bits = n * bit_new
quant_ratio = 100.0 - ((quant_bits / original_bits) * 100.0) if original_bits > 0 else 0.0
quant_cr = (original_bits / quant_bits) if quant_bits > 0 else 0.0
quant_disk_kb = round(os.path.getsize(quant_path) / 1024, 2)

# ============================================================
# (3) HUFFMAN (LOSSLESS)
# ============================================================
#Urutkan node berdasarkan freq (kecil → besar)
class Node:
    __slots__ = ("value", "freq", "left", "right")
    def __init__(self, value, freq):
        self.value = value
        self.freq = freq
        self.left = None
        self.right = None

#Ambil dua node paling kecil (left, right).
nodes = []
for k in symbols:
    nodes.append(Node(k, freq[k]))

#Buat pohonnya
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

# buat kode: kiri=0 kanan=1
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

# ukuran hasil = Σ(nk * panjang_kode)
huff_bits = 0
for k in symbols:
    huff_bits += freq[k] * len(codes[k])

huff_ratio = 100.0 - ((huff_bits / original_bits) * 100.0) if original_bits > 0 else 0.0
huff_cr = (original_bits / huff_bits) if huff_bits > 0 else 0.0

# encode bitstream (string)
bit_parts = [] #ubah semua piksel jadi bitstream
for v in gray:
    bit_parts.append(codes[v])
bitstream = "".join(bit_parts)

# decode manual
decoded_huff = [0] * n #baca bitstream, telusuri pohon, dapatkan simbol asli
idx_bit = 0
for i in range(n):
    node = root
    while node.value is None:
        b = bitstream[idx_bit]
        idx_bit += 1
        if b == "0":
            node = node.left
        else:
            node = node.right
    decoded_huff[i] = node.value

lossless_huff = True
for i in range(n):
    if decoded_huff[i] != gray[i]:
        lossless_huff = False
        break

huff_img = Image.new("L", (w, h))
huff_img.putdata(decoded_huff)
huff_path = os.path.join(out_dir, f"{base}_decoded_huffman.png")
huff_img.save(huff_path)
huff_disk_kb = round(os.path.getsize(huff_path) / 1024, 2)

# ============================================================
# (4) RLE (LOSSLESS) - scan row-major
# after_count = 2*jumlah_run
# ============================================================
#MENGHITUNG RUN-LENGTH DAN MENGELOMPOKKAN YANG SAMA
runs = []
cur = gray[0]
run_len = 1
for i in range(1, n):
    v = gray[i]
    if v == cur:
        run_len += 1
    else:
        runs.append((cur, run_len))
        cur = v
        run_len = 1
runs.append((cur, run_len))

# MENYUSUN HASIL RLE ke format encoding linear
encoded = []
for v, ln in runs:
    encoded.append(v)
    encoded.append(ln)

#MENDEKODE hasil RLE
decoded_rle = [0] * n
pos = 0
for i in range(0, len(encoded), 2):
    v = encoded[i]
    ln = encoded[i + 1]
    for _ in range(ln):
        decoded_rle[pos] = v
        pos += 1

lossless_rle = True
for i in range(n):
    if decoded_rle[i] != gray[i]:
        lossless_rle = False
        break

rle_img = Image.new("L", (w, h))
rle_img.putdata(decoded_rle)
rle_path = os.path.join(out_dir, f"{base}_decoded_rle.png")
rle_img.save(rle_path)
rle_disk_kb = round(os.path.getsize(rle_path) / 1024, 2)

before_count = n
after_count = len(encoded)  # 2*jumlah_run
rle_ratio = 100.0 - ((after_count / before_count) * 100.0) if before_count > 0 else 0.0
rle_cr = (before_count / after_count) if after_count > 0 else 0.0

# ============================================================
# REPORT 1: QUANTIZING 
# ============================================================
rep_q = os.path.join(out_dir, f"{base}_report_quantizing.txt")
with open(rep_q, "w", encoding="utf-8") as f:
    f.write("QUANTIZING COMPRESSION (LOSSY)\n")
    f.write("==============================================\n\n")

    f.write("1) Properti Citra (Input Grayscale 8-bit)\n")
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

    f.write("2) Parameter Quantizing\n")
    f.write("+---------------------------+------------------------------+\n")
    f.write(f"| Level baru (L_new)         | {L_new:<28} |\n")
    f.write(f"| Bit/piksel baru (log2 L)   | {bit_new:<28} |\n")
    f.write(f"| Step = 256/L_new           | {step:<28} |\n")
    f.write("+---------------------------+------------------------------+\n\n")

    f.write("3) Rumus Mapping\n")
    f.write("new = floor(old / step)\n\n")

    f.write("4) Ukuran Data (bit) + Rasio\n")
    f.write("+---------------------------------------------+------------------+\n")
    f.write(f"| Ukuran citra asli (n x 8 bit)               | {original_bits:16d} |\n")
    f.write(f"| Ukuran citra hasil (n x {bit_new} bit)              | {quant_bits:16d} |\n")
    f.write("+---------------------------------------------+------------------+\n\n")

    f.write("Penghematan (rumus):\n")
    f.write("P  = 100% - (UkuranHasil/UkuranAsli * 100%)\n")
    f.write(f"  = 100% - ({quant_bits}/{original_bits} * 100%)\n")
    f.write(f"  = {quant_ratio:.2f}%\n\n")

    f.write("Compression Ratio (CR):\n")
    f.write("CR = UkuranAsli / UkuranHasil\n")
    f.write(f"   = {original_bits} / {quant_bits}\n")
    f.write(f"   = {quant_cr:.4f}\n\n")

    f.write("5) Output\n")
    f.write("+-----------------------------------+------------------------------+\n")
    f.write(f"| Grayscale 8-bit (PNG)            | {os.path.basename(gray_path):<28} |\n")
    f.write(f"| Quantized (PNG)                  | {os.path.basename(quant_path):<28} |\n")
    f.write(f"| Ukuran file quantized (disk)     | {(str(quant_disk_kb)+' KB'):<28} |\n")
    f.write(f"| Catatan                          | {'LOSSY (level berubah)':<28} |\n")
    f.write("+-----------------------------------+------------------------------+\n")

# ============================================================
# REPORT 2: HUFFMAN
# ============================================================
rep_h = os.path.join(out_dir, f"{base}_report_huffman.txt")
with open(rep_h, "w", encoding="utf-8") as f:
    f.write("STATISTICAL COMPRESSION – HUFFMAN CODING (LOSSLESS)\n")
    f.write("===================================================\n\n")

    # 1) Properti
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
    # urutkan: kode terpendek dulu biar rapi
    symbols_sorted = sorted(symbols, key=lambda x: (len(codes[x]), x))
    for k in symbols_sorted:
        code = codes[k]
        f.write(f"| {k:8d} | {code:<28} | {len(code):12d} | {freq[k]:10d} |\n")
    f.write("+----------+------------------------------+--------------+------------+\n\n")

    # 4) Ukuran data
    f.write("4) Ukuran Data (bit)\n")
    f.write("+---------------------------------------------+------------------+\n")
    f.write(f"| Ukuran citra sebelum (n x 8 bit)            | {original_bits:16d} |\n")
    f.write(f"| Ukuran citra sesudah (Σ nk x panjang_kode)  | {huff_bits:16d} |\n")
    f.write("+---------------------------------------------+------------------+\n\n")

    f.write("Penghematan (rumus):\n")
    f.write("P  = 100% - (UkuranHasil/UkuranAsli * 100%)\n")
    f.write(f"  = 100% - ({huff_bits}/{original_bits} * 100%)\n")
    f.write(f"  = {huff_ratio:.2f}%\n\n")

    f.write("Compression Ratio (CR):\n")
    f.write("CR  = UkuranAsli / UkuranHasil\n")
    f.write(f"   = {original_bits} / {huff_bits}\n")
    f.write(f"   = {huff_cr:.4f}\n\n")

    # 5) Output
    f.write("5) Output (rekonstruksi / decode)\n")
    f.write("+-----------------------------------+------------------------------+\n")
    f.write(f"| Grayscale 8-bit (PNG)            | {os.path.basename(gray_path):<28} |\n")
    f.write(f"| Gambar hasil decode (PNG)        | {os.path.basename(huff_path):<28} |\n")
    f.write(f"| Ukuran file hasil (disk)         | {(str(huff_disk_kb)+' KB'):<28} |\n")
    f.write("+-----------------------------------+------------------------------+\n\n")

    # 6) Verifikasi lossless
    f.write("6) Verifikasi Lossless\n")
    f.write(f"- Decode == Input grayscale : {'YA (lossless)' if lossless_huff else 'TIDAK'}\n")

# ============================================================
# REPORT 3: RLE
# ============================================================
rep_r = os.path.join(out_dir, f"{base}_report_rle.txt")
with open(rep_r, "w", encoding="utf-8") as f:
    f.write("SPATIAL COMPRESSION – RUN LENGTH ENCODING (RLE)\n")
    f.write("==============================================\n\n")

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

    f.write("2) Run-length (nilai, panjang)\n")
    f.write("+---------------------------+------------------------------+\n")
    f.write(f"| Total run                  | {len(runs):<28} |\n")
    f.write(f"| Total nilai sebelum (n)    | {before_count:<28} |\n")
    f.write(f"| Total nilai sesudah (2R)   | {after_count:<28} |\n")
    f.write("+---------------------------+------------------------------+\n\n")

    f.write("Contoh daftar run (format: (nilai,panjang)):\n")
    # tampilkan 300 run pertama
    sample_runs = runs[:300] if len(runs) > 300 else runs
    write_runs(f, sample_runs, per_line=10)
    if len(runs) > 300:
        f.write("... (dipotong, run terlalu banyak)\n\n")

    f.write("3) Ringkasan ukuran\n")
    f.write("+-------------------------------------------+------------------+\n")
    f.write(f"| Ukuran citra asli (jumlah nilai)          | {before_count:16d} |\n")
    f.write(f"| Ukuran citra hasil (jumlah nilai)         | {after_count:16d} |\n")
    f.write(f"| Ratio = 100% - (hasil/asli x 100%)        | {rle_ratio:16.2f} |\n")
    f.write(f"| CR (Asli/Hasil)                           | {rle_cr:16.4f} |\n")
    f.write("+-------------------------------------------+------------------+\n\n")

    f.write("4) Output + verifikasi\n")
    f.write("+-----------------------------------+------------------------------+\n")
    f.write(f"| Grayscale 8-bit (PNG)            | {os.path.basename(gray_path):<28} |\n")
    f.write(f"| Gambar hasil decode (PNG)        | {os.path.basename(rle_path):<28} |\n")
    f.write(f"| Ukuran file hasil (disk)         | {(str(rle_disk_kb)+' KB'):<28} |\n")
    f.write(f"| Verifikasi (decode==input)       | {('YA (lossless)' if lossless_rle else 'TIDAK'):<28} |\n")
    f.write("+-----------------------------------+------------------------------+\n\n")

# ============================================================
# OUTPUT CONSOLE
# ============================================================
print("\n======================= PROPERTI CITRA =======================")
print(f"Nama Citra            : {nama}")
print(f"- Format              : {format_file}")
print(f"- Resolusi            : {w} x {h}")
print(f"- Jumlah piksel (n)   : {n}")
print(f"- Intensitas (min..max): {min_val} .. {max_val}")
print(f"- Ukuran file input   : {ukuran_file_kb} KB")
print("==============================================================")

print("\nOutput grayscale :", gray_path)

print("\n=== QUANTIZING (LOSSY) ===")
print(f"L_new={L_new}, bit={bit_new}, step={step}")
print(f"Ukuran asli  : {original_bits} bit")
print(f"Ukuran hasil : {quant_bits} bit")
print(f"Ratio        : {quant_ratio:.2f}%")
print(f"CR           : {quant_cr:.4f}")
print("Report       :", rep_q)

print("\n=== HUFFMAN (LOSSLESS) ===")
print(f"Ukuran hasil : {huff_bits} bit")
print(f"Ratio        : {huff_ratio:.2f}%")
print(f"CR           : {huff_cr:.4f}")
print("Lossless     :", "YA" if lossless_huff else "TIDAK")
print("Report       :", rep_h)

print("\n=== RLE (LOSSLESS - jumlah nilai) ===")
print(f"Jumlah run   : {len(runs)}")
print(f"Sebelum      : {before_count}")
print(f"Sesudah      : {after_count}")
print(f"Ratio        : {rle_ratio:.2f}%")
print(f"CR           : {rle_cr:.4f}")
print("Lossless     :", "YA" if lossless_rle else "TIDAK")
print("Report       :", rep_r)

print("\nSelesai. Semua output ada di folder:", out_dir)
